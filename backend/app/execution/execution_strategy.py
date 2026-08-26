import time
from abc import ABC, abstractmethod
from typing import Any, Optional

from app.context.state import ConversationState
from app.execution.exceptions import ExecutionValidationError
from app.execution.execution_context import ExecutionContext
from app.execution.execution_metrics import ExecutionMetrics
from app.execution.execution_policy import ExecutionPolicy
from app.execution.execution_result import ExecutionResult
from app.execution.execution_snapshot import ExecutionSnapshot
from app.execution.execution_status import ExecutionStatus
from app.graph.contracts import IGraph


class ExecutionStrategy(ABC):
    """Abstract interface for graph traversal strategies."""

    @abstractmethod
    async def execute(
        self,
        graph: IGraph,
        initial_state: ConversationState,
        policy: ExecutionPolicy,
        dispatcher: Any,
        scheduler: Any,
        context: Optional[ExecutionContext] = None,
    ) -> ExecutionResult:
        """Executes graph traversal according to the concrete strategy."""
        pass


class SequentialStrategy(ExecutionStrategy):
    """Strategy for sequential and conditional edge graph execution."""

    async def execute(
        self,
        graph: IGraph,
        initial_state: ConversationState,
        policy: ExecutionPolicy,
        dispatcher: Any,
        scheduler: Any,
        context: Optional[ExecutionContext] = None,
    ) -> ExecutionResult:
        start_time = time.perf_counter()

        if context is None:
            context = ExecutionContext(graph_id=graph.metadata.name or "graph")

        current_node_id = graph.entry_node
        if not current_node_id:
            raise ExecutionValidationError("Graph contains no entry node.")

        current_state = initial_state
        visited_nodes: list[str] = []
        snapshots: list[ExecutionSnapshot] = []
        errors: list[dict[str, Any]] = []
        warnings: list[str] = []
        failed_nodes: list[str] = []

        metrics = ExecutionMetrics()
        status = ExecutionStatus.RUNNING

        while current_node_id is not None:
            context.current_depth += 1
            if context.current_depth > policy.max_depth:
                raise ExecutionValidationError(
                    f"Maximum graph traversal depth of {policy.max_depth} exceeded at node '{current_node_id}'."
                )

            context.previous_node = context.current_node
            context.current_node = current_node_id
            visited_nodes.append(current_node_id)

            # Node execution via dispatcher
            snapshot, updated_state, err = await dispatcher.dispatch(
                graph=graph,
                node_id=current_node_id,
                state=current_state,
                context=context,
            )

            if snapshot:
                snapshots.append(snapshot)
            current_state = updated_state

            if err:
                failed_nodes.append(current_node_id)
                errors.append({"node_id": current_node_id, "error": str(err)})
                if policy.stop_on_error:
                    status = ExecutionStatus.FAILED
                    break

            # Schedule next node
            next_node_id = await scheduler.select_next_node(
                graph=graph,
                current_node_id=current_node_id,
                state=current_state,
            )
            current_node_id = next_node_id

        if status != ExecutionStatus.FAILED:
            status = ExecutionStatus.COMPLETED

        total_time = round(time.perf_counter() - start_time, 4)
        metrics.execution_time = total_time
        metrics.node_count = len(visited_nodes)
        metrics.visited_nodes = visited_nodes
        metrics.failed_nodes = failed_nodes
        metrics.errors = errors
        metrics.warnings = warnings
        metrics.compute_success_rate()

        return ExecutionResult(
            final_state=current_state,
            visited_nodes=visited_nodes,
            execution_metrics=metrics,
            execution_status=status,
            warnings=warnings,
            errors=errors,
            execution_context=context,
            snapshots=snapshots,
        )
