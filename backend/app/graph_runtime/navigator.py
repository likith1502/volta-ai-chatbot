from typing import Optional

from app.graph_runtime.cursor import GraphCursor


class GraphNavigator:
    """Navigates node cursor traversal through conditional edges and branch paths."""

    def navigate(
        self, cursor: GraphCursor, target_node: str, branch: Optional[str] = None
    ) -> GraphCursor:
        cursor.advance_to(target_node, branch_name=branch)
        return cursor
