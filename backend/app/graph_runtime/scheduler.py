import logging
from typing import Optional

from app.graph_runtime.cursor import GraphCursor
from app.graph_runtime.execution_plan import GraphExecutionPlan

logger = logging.getLogger("app.graph_runtime.scheduler")


class GraphScheduler:
    """Schedules sequential, parallel, and conditional node execution steps for Graph Runtime."""

    def schedule_next(self, plan: GraphExecutionPlan, cursor: GraphCursor) -> Optional[str]:
        """Schedules the next node to execute based on plan and cursor location."""
        order = plan.execution_order
        if not cursor.current_node or cursor.current_node not in order:
            return order[0] if order else None

        current_idx = order.index(cursor.current_node)
        if current_idx + 1 < len(order):
            return order[current_idx + 1]
        return None
