from typing import Optional

from app.context.state import ConversationState
from app.graph.contracts import IGraph


class ExecutionScheduler:
    """Schedules graph traversal by evaluating outgoing directed edges and priority predicates."""

    async def select_next_node(
        self,
        graph: IGraph,
        current_node_id: str,
        state: ConversationState,
    ) -> Optional[str]:
        """
        Evaluates outgoing edges from current_node_id sorted by priority.
        Returns target node_id of first satisfied edge, or None if terminal.
        """
        outgoing_edges = graph.get_outgoing_edges(current_node_id)
        if not outgoing_edges:
            return None

        # Sort edges by priority (highest priority first)
        sorted_edges = sorted(
            outgoing_edges, key=lambda e: getattr(e, "priority", 0), reverse=True
        )

        for edge in sorted_edges:
            is_satisfied = await edge.evaluate(state)
            if is_satisfied:
                return edge.target_node

        return None
