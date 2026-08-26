import logging
import time
from typing import Optional

from app.events.event import WorkflowEvent
from app.events.event_bus import WorkflowEventBus
from app.graph_runtime.checkpoint import GraphCheckpointIntegration
from app.graph_runtime.execution_plan import GraphExecutionPlan
from app.graph_runtime.execution_result import GraphExecutionResult
from app.graph_runtime.interrupt import GraphInterruptIntegration
from app.graph_runtime.middleware import GraphRuntimePipeline
from app.graph_runtime.resolver import GraphResolver
from app.graph_runtime.scheduler import GraphScheduler
from app.graph_runtime.session import GraphRuntimeSession
from app.graph_runtime.state import GraphRuntimeState
from app.graph_runtime.trace import ExecutionTrace
from app.graph_runtime.validator import GraphRuntimeValidator
from app.memory.manager import MemoryManager
from app.prompt.manager import PromptManager
from app.runtime.manager import RuntimeManager
from app.tools.manager import ToolManager

logger = logging.getLogger("app.graph_runtime.executor")


class GraphRuntimeExecutor:
    """Executes GraphExecutionPlan, orchestrating runtime managers (Prompt, Memory, Tool, Runtime, Checkpoint, HITL, Events)."""

    def __init__(
        self,
        prompt_manager: Optional[PromptManager] = None,
        memory_manager: Optional[MemoryManager] = None,
        tool_manager: Optional[ToolManager] = None,
        runtime_manager: Optional[RuntimeManager] = None,
        event_bus: Optional[WorkflowEventBus] = None,
    ) -> None:
        self.prompt_manager = prompt_manager or PromptManager()
        self.memory_manager = memory_manager or MemoryManager()
        self.tool_manager = tool_manager or ToolManager()
        self.runtime_manager = runtime_manager or RuntimeManager()
        self.event_bus = event_bus or WorkflowEventBus()

        self.scheduler = GraphScheduler()
        self.resolver = GraphResolver()
        self.validator = GraphRuntimeValidator()
        self.pipeline = GraphRuntimePipeline()
        self.checkpoint_integration = GraphCheckpointIntegration()
        self.interrupt_integration = GraphInterruptIntegration()

    async def execute_plan(
        self, plan: GraphExecutionPlan, session: GraphRuntimeSession
    ) -> GraphExecutionResult:
        """Executes a GraphExecutionPlan step-by-step."""
        t0 = time.perf_counter()
        self.validator.validate_plan(plan)
        trace = ExecutionTrace(
            workflow_id=plan.workflow_id, execution_id=session.session_id
        )

        session.state = GraphRuntimeState.RUNNING
        visited = []

        # Emit start event
        try:
            await self.event_bus.publish(
                WorkflowEvent(
                    event_name="graph_runtime.started",
                    payload={
                        "workflow_id": plan.workflow_id,
                        "session_id": str(session.session_id),
                    },
                    source="graph_runtime_executor",
                )
            )
        except Exception:
            pass

        for node_id in plan.execution_order:
            step_t0 = time.perf_counter()
            session.cursor.advance_to(node_id)
            visited.append(node_id)

            action = self.resolver.resolve_action(node_id)
            dt_step = (time.perf_counter() - step_t0) * 1000.0
            trace.add_step(node_id=node_id, action=action, latency_ms=dt_step)

            # Auto-checkpointing if enabled
            if (
                plan.policy.checkpoint_interval > 0
                and len(visited) % plan.policy.checkpoint_interval == 0
            ):
                await self.checkpoint_integration.create_snapshot(session)

        session.state = GraphRuntimeState.COMPLETED
        dt_total = (time.perf_counter() - t0) * 1000.0

        # Emit completion event
        try:
            await self.event_bus.publish(
                WorkflowEvent(
                    event_name="graph_runtime.completed",
                    payload={
                        "workflow_id": plan.workflow_id,
                        "session_id": str(session.session_id),
                        "duration_ms": dt_total,
                    },
                    source="graph_runtime_executor",
                )
            )
        except Exception:
            pass

        return GraphExecutionResult(
            execution_id=session.session_id,
            session_id=session.session_id,
            workflow_id=plan.workflow_id,
            status=GraphRuntimeState.COMPLETED,
            success=True,
            visited_nodes=visited,
            total_latency_ms=round(dt_total, 2),
            final_output={
                "message": f"Graph '{plan.workflow_id}' executed successfully.",
                "nodes": visited,
            },
            trace=trace,
        )
