from typing import Any, Optional

from app.context.state import ConversationState
from app.execution.execution_policy import ExecutionPolicy
from app.graph.contracts import IGraph


class ExecutionPlanner:
    """
    Contract placeholder for graph execution planning.
    Future extension point for parallel execution, priority scheduling, and branch optimization.
    """

    def plan_execution(
        self,
        graph: IGraph,
        initial_state: ConversationState,
        policy: Optional[ExecutionPolicy] = None,
    ) -> dict[str, Any]:
        """Generates an execution plan metadata contract for graph traversal."""
        return {
            "entry_node": graph.entry_node,
            "total_nodes": len(graph.nodes),
            "total_edges": len(graph.edges),
            "strategy": "sequential",
            "optimizations": [],
        }
