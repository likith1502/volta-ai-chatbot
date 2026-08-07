import asyncio
import logging
import time
import uuid
from typing import Optional

from app.events.event import WorkflowEvent
from app.events.event_bus import WorkflowEventBus
from app.prompt.compiler import PromptCompiler
from app.prompt.context import PromptContext
from app.prompt.contracts import PromptRequest, PromptResponse
from app.prompt.exceptions import PromptRenderError, TemplateNotFoundError
from app.prompt.execution_store import InMemoryPromptExecutionStore, PromptExecutionStore, PromptSnapshot
from app.prompt.factory import PromptFactory
from app.prompt.health import PromptHealthManager
from app.prompt.metrics import PromptMetrics
from app.prompt.middleware.audit_mw import AuditMiddleware
from app.prompt.middleware.base import PromptMiddleware, PromptPipeline
from app.prompt.middleware.injection_mw import VariableInjectionMiddleware
from app.prompt.middleware.optimization_mw import OptimizationMiddleware
from app.prompt.middleware.rendering_mw import RenderingMiddleware
from app.prompt.middleware.security_mw import SecurityMiddleware
from app.prompt.middleware.validation_mw import ValidationMiddleware
from app.prompt.processors.linter import PromptLinter
from app.prompt.processors.optimizer import PromptOptimizer
from app.prompt.processors.renderer import PromptRenderer
from app.prompt.processors.validator import PromptValidator
from app.prompt.registry import PromptRegistry
from app.prompt.result import PromptResult
from app.prompt.trace import PromptTrace
from app.runtime.contracts import RuntimeRequest
from app.runtime.manager import RuntimeManager

logger = logging.getLogger("app.prompt.manager")


class PromptManager:
    """Central orchestrator for the Prompt Execution Engine, handling prompt templating, rendering, validation, optimization, linting, and LLM runtime execution."""

    def __init__(
        self,
        registry: Optional[PromptRegistry] = None,
        runtime_manager: Optional[RuntimeManager] = None,
        execution_store: Optional[PromptExecutionStore] = None,
        event_bus: Optional[WorkflowEventBus] = None,
    ) -> None:
        self.registry = registry or PromptRegistry()
        self.runtime_manager = runtime_manager or RuntimeManager()
        self.execution_store = execution_store or InMemoryPromptExecutionStore()
        self.event_bus = event_bus or WorkflowEventBus()

        # Register default presets if empty
        if not self.registry.exists_template("mobility_assistant_v1"):
            self.registry.register_template(PromptFactory.create_mobility_assistant_template())
        if not self.registry.exists_template("ride_booking_v1"):
            self.registry.register_template(PromptFactory.create_ride_booking_template())
        if not self.registry.exists_template("system_chat_v1"):
            self.registry.register_template(PromptFactory.create_system_chat_template())

        self.health_manager = PromptHealthManager(self.registry)

        # Processors & Compiler
        self.renderer = PromptRenderer()
        self.validator = PromptValidator()
        self.optimizer = PromptOptimizer()
        self.linter = PromptLinter()
        self.compiler = PromptCompiler()

        # Setup standard pipeline
        self.pipeline = PromptPipeline(
            middlewares=[
                ValidationMiddleware(),
                SecurityMiddleware(),
                VariableInjectionMiddleware(),
                RenderingMiddleware(),
                OptimizationMiddleware(),
                AuditMiddleware(),
            ]
        )

    async def _emit_event(self, event_name: str, payload: dict) -> None:
        """Emits event to Phase 6.5 WorkflowEventBus."""
        try:
            event = WorkflowEvent(
                event_name=f"prompt.{event_name}",
                payload=payload,
                source="prompt_manager",
            )
            await self.event_bus.publish(event)
        except Exception as exc:
            logger.debug(f"Prompt event emission notice: {exc}")

    async def render(self, request: PromptRequest) -> PromptResult:
        """Renders, validates, lints, and optimizes prompt WITHOUT executing LLM generation."""

        async def _core_render(req: PromptRequest) -> PromptResult:
            return await self._render_internal(req)

        return await self.pipeline.execute(request, _core_render)

    async def _render_internal(self, request: PromptRequest) -> PromptResult:
        start_time = time.perf_counter()
        prompt_id = uuid.uuid4()
        revision_id = request.revision_id or "v1"

        context = PromptContext(
            prompt_id=prompt_id,
            template_id=request.template_id,
            revision_id=revision_id,
            conversation_id=request.conversation_id,
            metadata=request.metadata,
        )

        metrics = PromptMetrics()
        trace = PromptTrace()

        await self._emit_event("created", {"prompt_id": str(prompt_id), "template_id": request.template_id})

        # 1. Lookup Template
        template = self.registry.lookup_template(request.template_id)

        # Handle template inheritance
        effective_system_instruction = template.system_instruction
        if template.parent_template_id and self.registry.exists_template(template.parent_template_id):
            parent = self.registry.lookup_template(template.parent_template_id)
            if parent.system_instruction and not effective_system_instruction:
                effective_system_instruction = parent.system_instruction

        # 2. Validation
        val_start = time.perf_counter()
        val_res = self.validator.validate(
            messages=template.messages,
            required_variables=template.variables,
            supplied_variables=request.variables,
        )
        val_dt = (time.perf_counter() - val_start) * 1000.0
        metrics.validation_time_ms = val_dt

        warnings = list(val_res.warnings)
        if not val_res.is_valid:
            await self._emit_event("failed", {"prompt_id": str(prompt_id), "errors": val_res.errors})
            return PromptResult(
                rendered_prompt=None,
                metrics=metrics,
                context=context,
                trace=trace,
                execution_status="FAILED",
                errors=val_res.errors,
                warnings=warnings,
            )

        await self._emit_event("validated", {"prompt_id": str(prompt_id)})

        # 3. Linting
        lint_res = self.linter.lint(
            messages=template.messages,
            system_instruction=effective_system_instruction,
            declared_variables=template.variables,
        )
        for issue in lint_res.issues:
            warnings.append(f"[{issue.severity.upper()}] {issue.message}")

        # 4. Rendering
        rend_start = time.perf_counter()
        rendered_resp = self.renderer.render(
            template_id=template.template_id,
            revision_id=revision_id,
            messages=template.messages,
            variables=request.variables,
            system_instruction=effective_system_instruction,
        )
        rend_dt = (time.perf_counter() - rend_start) * 1000.0
        metrics.render_time_ms = rend_dt
        await self._emit_event("rendered", {"prompt_id": str(prompt_id)})

        # 5. Optimization
        opt_start = time.perf_counter()
        opt_res = self.optimizer.optimize(rendered_resp)
        opt_dt = (time.perf_counter() - opt_start) * 1000.0
        metrics.optimization_time_ms = opt_dt
        metrics.template_size_chars = opt_res.original_chars
        metrics.rendered_size_chars = opt_res.optimized_chars
        metrics.compression_ratio = opt_res.compression_ratio
        metrics.optimization_pct = opt_res.optimization_pct

        total_chars = sum(len(m.content) for m in rendered_resp.messages)
        metrics.token_estimate = max(1, total_chars // 4)

        await self._emit_event("optimized", {"prompt_id": str(prompt_id), "compression_ratio": metrics.compression_ratio})

        metrics.execution_time_ms = (time.perf_counter() - start_time) * 1000.0

        result = PromptResult(
            rendered_prompt=rendered_resp,
            metrics=metrics,
            context=context,
            trace=trace,
            execution_status="COMPLETED",
            warnings=warnings,
        )

        # Save snapshot
        snapshot_content = "\n".join(m.content for m in rendered_resp.messages)
        await self.execution_store.save_snapshot(
            PromptSnapshot(
                template_id=request.template_id,
                revision_id=revision_id,
                variables=request.variables,
                rendered_content=snapshot_content,
            )
        )
        await self.execution_store.save_result(result)

        return result

    async def execute(self, request: PromptRequest) -> PromptResult:
        """Renders prompt via pipeline, compiles payload, and executes end-to-end through RuntimeManager."""
        prompt_res = await self.render(request)
        if prompt_res.execution_status == "FAILED" or not prompt_res.rendered_prompt:
            return prompt_res

        # Lookup profile if supplied
        profile = self.registry.lookup_profile(request.profile_id) if request.profile_id else None

        # Compile prompt
        compiled = self.compiler.compile(request, prompt_res.rendered_prompt, profile=profile)

        # Construct RuntimeRequest
        runtime_req = RuntimeRequest(
            conversation_id=request.conversation_id,
            messages=compiled.messages,
            system_prompt=compiled.system_prompt,
            provider=compiled.provider,
            model=compiled.model,
            temperature=compiled.temperature,
            max_tokens=compiled.max_tokens,
            metadata=request.metadata,
        )

        # Execute LLM generation turn via RuntimeManager
        runtime_res = await self.runtime_manager.execute(runtime_req)
        prompt_res.runtime_result = runtime_res
        prompt_res.context.runtime_id = runtime_res.context.runtime_id

        await self._emit_event("executed", {"prompt_id": str(prompt_res.context.prompt_id), "runtime_id": str(runtime_res.context.runtime_id)})
        await self.execution_store.save_result(prompt_res)

        return prompt_res
