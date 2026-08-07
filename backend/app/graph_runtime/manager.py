import logging
import time
import uuid
from typing import Any, Optional

from app.events.event_bus import WorkflowEventBus
from app.graph_runtime.analytics import GraphRuntimeAnalyticsManager
from app.graph_runtime.contracts import (
    GraphCancelPayload,
    GraphExecutePayload,
    GraphPausePayload,
    GraphResumePayload,
)
from app.graph_runtime.exceptions import GraphExecutionInterruptedError, GraphNodeNotFoundError
from app.graph_runtime.execution_plan import GraphExecutionPlan
from app.graph_runtime.execution_result import GraphExecutionResult
from app.graph_runtime.executor import GraphRuntimeExecutor
from app.graph_runtime.health import GraphRuntimeHealthManager, GraphRuntimeHealthStatus
from app.graph_runtime.planner import GraphPlanner
from app.graph_runtime.registry import GraphSessionRegistry
from app.graph_runtime.session import GraphRuntimeSession
from app.graph_runtime.state import GraphRuntimeState
from app.graph_runtime.statistics import GraphRuntimeStatistics

logger = logging.getLogger("app.graph_runtime.manager")


class GraphRuntimeManager:
    """Central orchestrator for the Enterprise Graph Runtime handling planning, scheduling, execution dispatch, session state, health, statistics, and analytics."""

    def __init__(
        self,
        event_bus: Optional[WorkflowEventBus] = None,
        registry: Optional[GraphSessionRegistry] = None,
    ) -> None:
        self.event_bus = event_bus or WorkflowEventBus()
        self.registry = registry or GraphSessionRegistry()

        self.planner = GraphPlanner()
        self.executor = GraphRuntimeExecutor(event_bus=self.event_bus)
        self.health_manager = GraphRuntimeHealthManager()
        self.analytics_manager = GraphRuntimeAnalyticsManager()
        self.statistics = GraphRuntimeStatistics()

    async def execute_graph(self, payload: GraphExecutePayload) -> GraphExecutionResult:
        """Plans and executes a workflow graph."""
        session = GraphRuntimeSession(
            session_id=payload.execution_id or uuid.uuid4(),
            conversation_id=payload.conversation_id or uuid.uuid4(),
            workflow_id=payload.workflow_id,
            state=GraphRuntimeState.RUNNING,
            context_data=payload.inputs,
        )
        self.registry.register(session)

        plan = self.planner.plan_execution(workflow_id=payload.workflow_id)
        result = await self.executor.execute_plan(plan, session)

        self.analytics_manager.record_run(
            duration_ms=result.total_latency_ms,
            success=result.success,
            visited_nodes=result.visited_nodes,
        )
        self.statistics.total_executions += 1
        if result.success:
            self.statistics.successful_executions += 1
        else:
            self.statistics.failed_executions += 1

        return result

    async def resume_session(self, payload: GraphResumePayload) -> GraphExecutionResult:
        """Resumes a paused or interrupted graph execution session."""
        session = self.registry.get(str(payload.session_id))
        if not session:
            session = GraphRuntimeSession(
                session_id=payload.session_id,
                workflow_id="resumed_workflow",
                state=GraphRuntimeState.RUNNING,
            )
            self.registry.register(session)

        session.state = GraphRuntimeState.RUNNING
        plan = self.planner.plan_execution(workflow_id=session.workflow_id)
        return await self.executor.execute_plan(plan, session)

    async def pause_session(self, payload: GraphPausePayload) -> GraphRuntimeSession:
        """Pauses a running graph execution session."""
        session = self.registry.get(str(payload.session_id))
        if session:
            session.state = GraphRuntimeState.PAUSED
            return session
        raise GraphNodeNotFoundError(f"Session '{payload.session_id}' not found.")

    async def cancel_session(self, payload: GraphCancelPayload) -> GraphRuntimeSession:
        """Cancels a graph execution session."""
        session = self.registry.get(str(payload.session_id))
        if session:
            session.state = GraphRuntimeState.CANCELLED
            return session
        raise GraphNodeNotFoundError(f"Session '{payload.session_id}' not found.")

    async def get_session(self, session_id: str) -> Optional[GraphRuntimeSession]:
        """Retrieves active GraphRuntimeSession by ID."""
        return self.registry.get(session_id)

    async def get_statistics(self) -> GraphRuntimeStatistics:
        """Returns statistics snapshot of Graph Runtime operations."""
        report = self.analytics_manager.get_report()
        self.statistics.average_latency_ms = report.average_duration_ms
        return self.statistics
