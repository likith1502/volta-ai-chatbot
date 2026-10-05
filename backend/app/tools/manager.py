import asyncio
import logging
import time
import uuid
from typing import Any, Optional

from app.events.event import WorkflowEvent
from app.events.event_bus import WorkflowEventBus
from app.tools.analytics import ToolAnalyticsManager
from app.tools.builtin import CalculatorTool, DatetimeTool, EchoTool, UUIDTool
from app.tools.chain import ChainResult, ToolChain, ToolChainStep
from app.tools.contracts import ToolExecutePayload
from app.tools.discovery import ToolDiscoveryService
from app.tools.dispatcher import ToolDispatcher
from app.tools.exceptions import ToolNotFoundError, ToolValidationError
from app.tools.executor import ToolExecutor
from app.tools.factory import ToolFactory
from app.tools.health import ToolHealthManager
from app.tools.manifest import ToolManifest
from app.tools.metrics import ToolMetrics
from app.tools.pipeline import PipelineResult, ToolPipeline
from app.tools.policy import ToolPolicy
from app.tools.registry import ToolRegistry
from app.tools.repository import ToolRepository
from app.tools.request import ToolRequest
from app.tools.result import ToolResult
from app.tools.statistics import ToolStatistics
from app.tools.tool import BaseTool
from app.tools.validator import ToolValidator

logger = logging.getLogger("app.tools.manager")


class ToolManager:
    """Central orchestrator for the Enterprise Tool Runtime handling tool registration, schema lookup, discovery, authorization, pipeline processing, chain execution, health reporting, and event bus notification dispatch."""

    def __init__(
        self,
        registry: Optional[ToolRegistry] = None,
        event_bus: Optional[WorkflowEventBus] = None,
    ) -> None:
        self.registry = registry or ToolRegistry()
        self.event_bus = event_bus or WorkflowEventBus()

        self.validator = ToolValidator()
        self.executor = ToolExecutor()
        self.dispatcher = ToolDispatcher(executor=self.executor)
        self.pipeline = ToolPipeline(validator=self.validator, dispatcher=self.dispatcher)
        self.health_manager = ToolHealthManager(self.registry)
        self.analytics_manager = ToolAnalyticsManager()
        self.metrics = ToolMetrics()

        self._initialized = False

    async def initialize(self) -> None:
        """Initializes ToolManager with default in-memory built-in reference tools."""
        if not self._initialized:
            repo = await ToolFactory.create_default_repository()
            self.registry.set_repository(repo)
            self.discovery = ToolDiscoveryService(repo)
            self._initialized = True

    async def _ensure_init(self) -> None:
        if not self._initialized:
            await self.initialize()

    async def _emit_event(self, event_name: str, payload: dict) -> None:
        """Publishes event to Phase 6.5 WorkflowEventBus."""
        try:
            event = WorkflowEvent(
                event_name=f"tool.{event_name}",
                payload=payload,
                source="tool_manager",
            )
            await self.event_bus.publish(event)
        except Exception as exc:
            logger.debug(f"Tool event emission notice: {exc}")

    async def register_tool(self, tool_instance: BaseTool) -> ToolManifest:
        """Registers a BaseTool instance."""
        await self._ensure_init()
        manifest = await self.registry.register(tool_instance)
        await self._emit_event("registered", {
            "tool_name": manifest.tool_name,
            "version": manifest.version,
        })
        return manifest

    async def get_manifest(self, name: str) -> ToolManifest:
        """Retrieves ToolManifest by tool name."""
        await self._ensure_init()
        manifest = await self.registry.get_repository().get_manifest(name)
        if not manifest:
            raise ToolNotFoundError(f"Tool '{name}' not found.")
        return manifest

    async def list_tools(self) -> list[ToolManifest]:
        """Lists all registered tool manifests."""
        await self._ensure_init()
        return await self.registry.get_repository().list_all()

    async def execute_tool(self, payload: ToolExecutePayload) -> ToolResult:
        """Executes a single tool request."""
        await self._ensure_init()
        manifest = await self.get_manifest(payload.tool_name)
        tool_instance = await self.registry.get_repository().get_by_name(payload.tool_name)

        if not tool_instance:
            raise ToolNotFoundError(f"Tool instance for '{payload.tool_name}' not found.")

        req = ToolRequest(
            conversation_id=payload.conversation_id,
            execution_id=payload.execution_id,
            tool_name=payload.tool_name,
            arguments=payload.arguments,
        )

        await self._emit_event("started", {
            "tool_name": payload.tool_name,
            "execution_id": str(req.execution_id),
        })

        t0 = time.perf_counter()
        self.validator.validate(manifest, payload.arguments)
        result = await self.dispatcher.dispatch_single(tool_instance, req)
        dt = (time.perf_counter() - t0) * 1000.0

        self.analytics_manager.record_execution(payload.tool_name, result.success, dt)
        self.metrics.total_tool_calls += 1
        if result.success:
            self.metrics.successful_calls += 1
            await self._emit_event("completed", {
                "tool_name": payload.tool_name,
                "execution_id": str(req.execution_id),
                "duration_ms": dt,
            })
        else:
            self.metrics.failed_calls += 1
            await self._emit_event("failed", {
                "tool_name": payload.tool_name,
                "execution_id": str(req.execution_id),
                "error": str(result.errors),
            })

        return result

    async def execute_pipeline(self, payload: ToolExecutePayload) -> PipelineResult:
        """Executes tool request through ToolPipeline."""
        await self._ensure_init()
        manifest = await self.get_manifest(payload.tool_name)
        tool_instance = await self.registry.get_repository().get_by_name(payload.tool_name)
        req = ToolRequest(
            conversation_id=payload.conversation_id,
            execution_id=payload.execution_id,
            tool_name=payload.tool_name,
            arguments=payload.arguments,
        )
        return await self.pipeline.execute_pipeline(manifest, tool_instance, req)

    async def execute_chain(self, chain: ToolChain) -> ChainResult:
        """Executes a sequential multi-step ToolChain."""
        await self._ensure_init()
        t0 = time.perf_counter()
        results = []
        last_output = None

        for step in chain.steps:
            # Merge output of last step into current arguments if specified
            args = step.arguments.copy()
            if last_output is not None and isinstance(last_output, dict):
                args.update(last_output)

            payload = ToolExecutePayload(tool_name=step.tool_name, arguments=args)
            res = await self.execute_tool(payload)
            results.append(res)

            if not res.success:
                dt = (time.perf_counter() - t0) * 1000.0
                return ChainResult(
                    chain_id=chain.chain_id,
                    status="failed",
                    success=False,
                    completed_steps=len(results) - 1,
                    total_steps=len(chain.steps),
                    step_results=results,
                    total_latency_ms=round(dt, 2),
                )
            last_output = res.output

        dt = (time.perf_counter() - t0) * 1000.0
        return ChainResult(
            chain_id=chain.chain_id,
            status="success",
            success=True,
            completed_steps=len(results),
            total_steps=len(chain.steps),
            step_results=results,
            total_latency_ms=round(dt, 2),
            final_output=last_output,
        )

    async def get_statistics(self) -> ToolStatistics:
        """Returns snapshot statistics of tool repository."""
        await self._ensure_init()
        manifests = await self.registry.get_repository().list_all()
        active = [m for m in manifests if not m.deprecated]
        deprecated = [m for m in manifests if m.deprecated]

        report = self.analytics_manager.get_report()
        return ToolStatistics(
            total_registered_tools=len(manifests),
            active_tools=len(active),
            deprecated_tools=len(deprecated),
            total_executions=report.total_executions,
            average_execution_latency_ms=report.average_latency_ms,
        )
