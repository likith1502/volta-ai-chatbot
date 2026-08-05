from typing import Optional, Tuple

from app.context.state import ConversationState
from app.execution.execution_context import ExecutionContext
from app.execution.execution_snapshot import ExecutionSnapshot
from app.graph.contracts import IGraph
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext, NodeResult


class ExecutionDispatcher:
    """Dispatches lifecycle hooks for workflow node execution and captures state snapshots."""

    async def dispatch(
        self,
        graph: IGraph,
        node_id: str,
        state: ConversationState,
        context: ExecutionContext,
    ) -> Tuple[Optional[ExecutionSnapshot], ConversationState, Optional[Exception]]:
        node = graph.get_node(node_id)
        node_exec_ctx = NodeExecutionContext(
            execution_id=context.execution_id,
            graph_id=context.graph_id,
            node_id=node_id,
            execution_mode=context.execution_mode,
            retry_count=context.retry_count,
        )

        current_state = state
        node_error: Optional[Exception] = None

        try:
            # 1. before_execute
            if hasattr(node, "before_execute"):
                current_state = await node.before_execute(current_state, node_exec_ctx)

            # 2. execute
            if hasattr(node, "execute"):
                current_state = await node.execute(current_state, node_exec_ctx)

            # 3. after_execute
            if hasattr(node, "after_execute"):
                current_state = await node.after_execute(current_state, node_exec_ctx)

        except Exception as exc:
            node_error = exc
            if hasattr(node, "on_error"):
                try:
                    current_state = await node.on_error(current_state, exc, node_exec_ctx)
                except Exception:
                    pass

        # Construct NodeResult & ExecutionSnapshot
        node_res = NodeResult(
            state=current_state,
            execution_time=0.0,
            metadata={"node_id": node_id, "node_type": getattr(node, "node_type", "custom")},
        )
        snapshot = ExecutionSnapshot(
            node_id=node_id,
            state=current_state,
            node_result=node_res,
            execution_context=context,
        )

        return snapshot, current_state, node_error
