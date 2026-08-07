import asyncio
import logging
import time
import uuid
from typing import Optional

from app.events.event import WorkflowEvent
from app.events.event_bus import WorkflowEventBus
from app.runtime.config import RuntimeConfig
from app.runtime.context import RuntimeContext
from app.runtime.contracts import RuntimeRequest, RuntimeResponse
from app.runtime.exceptions import (
    ProviderConfigurationError,
    ProviderNotFoundError,
    RuntimeExecutionError,
    RuntimeRetryExhaustedError,
    RuntimeTimeoutError,
)
from app.runtime.execution_store import InMemoryExecutionStore, RuntimeExecutionStore
from app.runtime.factory import RuntimeFactory
from app.runtime.health import RuntimeHealthManager
from app.runtime.metrics import RuntimeMetrics
from app.runtime.middleware.base import RuntimeMiddleware
from app.runtime.middleware.logging_middleware import LoggingMiddleware
from app.runtime.middleware.metrics_middleware import MetricsMiddleware
from app.runtime.middleware.validation_middleware import ValidationMiddleware
from app.runtime.model_registry import ModelRegistry
from app.runtime.providers.gemini_provider import GeminiProvider
from app.runtime.providers.mock_provider import MockProvider
from app.runtime.registry import RuntimeRegistry
from app.runtime.result import RuntimeResult

logger = logging.getLogger("app.runtime.manager")


class RuntimeManager:
    """Orchestration engine for the Enterprise LLM Runtime Engine."""

    def __init__(
        self,
        config: Optional[RuntimeConfig] = None,
        registry: Optional[RuntimeRegistry] = None,
        execution_store: Optional[RuntimeExecutionStore] = None,
        model_registry: Optional[ModelRegistry] = None,
        event_bus: Optional[WorkflowEventBus] = None,
    ) -> None:
        self.config = config or RuntimeConfig()
        self.model_registry = model_registry or ModelRegistry()
        self.execution_store = execution_store or InMemoryExecutionStore()
        self.event_bus = event_bus or WorkflowEventBus()

        # Initialize registry & register default providers
        self.registry = registry or RuntimeRegistry()
        if not self.registry.exists("mock"):
            self.registry.register(MockProvider(latency_ms=10.0))
        if not self.registry.exists("gemini"):
            self.registry.register_factory("gemini", lambda: RuntimeFactory.create_provider("gemini"))

        self.health_manager = RuntimeHealthManager(self.registry)

        # Setup standard middleware chain
        self.middlewares: list[RuntimeMiddleware] = [
            ValidationMiddleware(),
            LoggingMiddleware(),
            MetricsMiddleware(),
        ]

    async def _emit_event(self, event_name: str, payload: dict) -> None:
        """Emits structured observability event to Phase 6.5 WorkflowEventBus."""
        try:
            event = WorkflowEvent(
                event_name=f"runtime.{event_name}",
                payload=payload,
                source="runtime_manager",
            )
            await self.event_bus.publish(event)
        except Exception as exc:
            logger.debug(f"Event emission non-critical notice: {exc}")

    async def execute(self, request: RuntimeRequest) -> RuntimeResult:
        """Executes a runtime request through middleware chain, provider dispatch, retry handling, and store persistence."""

        async def _core_execution(req: RuntimeRequest) -> RuntimeResult:
            return await self._execute_internal(req)

        # Execute through middleware pipeline
        handler = _core_execution
        for middleware in reversed(self.middlewares):
            current_fn = handler
            current_mw = middleware

            async def _mw_wrapper(r: RuntimeRequest, mw=current_mw, fn=current_fn) -> RuntimeResult:
                return await mw.process(r, fn)

            handler = _mw_wrapper

        return await handler(request)

    async def _execute_internal(self, request: RuntimeRequest) -> RuntimeResult:
        start_time = time.perf_counter()
        runtime_id = uuid.uuid4()

        # Determine target provider & model
        requested_provider = (request.provider or self.config.default_provider).lower().strip()
        requested_model = request.model or self.config.default_model

        context = RuntimeContext(
            runtime_id=runtime_id,
            provider=requested_provider,
            model=requested_model,
            execution_id=request.execution_id or uuid.uuid4(),
            conversation_id=request.conversation_id,
            metadata=request.metadata,
        )

        metrics = RuntimeMetrics()
        await self._emit_event("started", {"runtime_id": str(runtime_id), "provider": requested_provider})

        # 1. Prompt Preparation
        await self._emit_event("prompt_prepared", {"runtime_id": str(runtime_id), "message_count": len(request.messages)})

        # 2. Provider Selection & Fallback
        provider = self.registry.get(requested_provider)
        if not provider:
            if self.config.demo_mode or requested_provider != "mock":
                logger.warning(f"Provider '{requested_provider}' unavailable. Falling back to MockProvider in demo mode.")
                provider = self.registry.lookup("mock")
                context.provider = "mock"
                context.metadata["fallback_from"] = requested_provider
            else:
                raise ProviderNotFoundError(f"Provider '{requested_provider}' not registered.")

        await self._emit_event("provider_selected", {"runtime_id": str(runtime_id), "provider": provider.name})

        # 3. Provider Initialization
        try:
            await provider.initialize()
            await self._emit_event("provider_initialized", {"runtime_id": str(runtime_id), "provider": provider.name})
        except Exception as exc:
            if self.config.demo_mode and provider.name != "mock":
                logger.warning(f"Failed to initialize '{provider.name}'. Falling back to MockProvider: {exc}")
                provider = self.registry.lookup("mock")
                await provider.initialize()
                context.provider = "mock"
            else:
                raise RuntimeExecutionError(f"Failed to initialize provider '{provider.name}': {exc}")

        # 4. Request Dispatch with Retries & Timeout
        max_retries = self.config.max_retries
        timeout_sec = self.config.timeout
        last_exception: Optional[Exception] = None
        response: Optional[RuntimeResponse] = None

        for attempt in range(max_retries + 1):
            try:
                metrics.retries_attempted = attempt
                await self._emit_event("request_sent", {"runtime_id": str(runtime_id), "attempt": attempt + 1})

                prov_start = time.perf_counter()
                
                # Execute generate with timeout
                response = await asyncio.wait_for(
                    provider.generate(request),
                    timeout=timeout_sec,
                )
                
                metrics.provider_time_ms = (time.perf_counter() - prov_start) * 1000.0
                await self._emit_event("response_received", {"runtime_id": str(runtime_id), "response_id": str(response.response_id)})
                break
            except asyncio.TimeoutError:
                last_exception = RuntimeTimeoutError(f"Provider '{provider.name}' timed out after {timeout_sec}s.")
                logger.warning(f"Runtime attempt {attempt + 1} timed out for provider '{provider.name}'.")
            except Exception as exc:
                last_exception = exc
                logger.warning(f"Runtime attempt {attempt + 1} failed for provider '{provider.name}': {exc}")

            if attempt < max_retries:
                await asyncio.sleep(0.1 * (2 ** attempt))

        if not response:
            error_msg = f"Runtime execution failed after {max_retries + 1} attempts. Last error: {last_exception}"
            await self._emit_event("failed", {"runtime_id": str(runtime_id), "error": error_msg})
            
            result_fail = RuntimeResult(
                response=None,
                metrics=metrics,
                context=context,
                execution_status="FAILED",
                errors=[error_msg],
            )
            await self.execution_store.save(result_fail)
            raise RuntimeRetryExhaustedError(error_msg)

        # 5. Response Normalization & Token Accounting
        await self._emit_event("response_normalized", {"runtime_id": str(runtime_id)})
        metrics.tokens = response.token_usage
        metrics.estimated_cost_usd = response.token_usage.estimated_cost_usd
        await self._emit_event("tokens_calculated", {"runtime_id": str(runtime_id), "total_tokens": metrics.tokens.total_tokens})

        # Calculate wall clock latency
        metrics.latency_ms = (time.perf_counter() - start_time) * 1000.0

        result_success = RuntimeResult(
            response=response,
            metrics=metrics,
            context=context,
            execution_status="COMPLETED",
            runtime_version="7.0.0",
            provider_version="1.0.0",
            api_version="v1",
        )

        # Save result to execution store
        await self.execution_store.save(result_success)
        await self._emit_event("completed", {"runtime_id": str(runtime_id), "latency_ms": metrics.latency_ms})

        return result_success
