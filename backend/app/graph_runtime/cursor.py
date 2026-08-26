from typing import Optional

from pydantic import BaseModel, Field


class GraphCursor(BaseModel):
    """Runtime execution cursor tracking graph navigation position and traversal order."""

    current_node: str = Field(default="START")
    parent_node: Optional[str] = None
    child_node: Optional[str] = None
    visited_nodes: list[str] = Field(default_factory=list)
    execution_order: list[str] = Field(default_factory=list)
    branch: Optional[str] = None
    depth: int = Field(default=0, ge=0)

    def advance_to(self, next_node: str, branch_name: Optional[str] = None) -> None:
        """Advances cursor position to next target node."""
        if self.current_node and self.current_node not in self.visited_nodes:
            self.visited_nodes.append(self.current_node)
        self.parent_node = self.current_node
        self.current_node = next_node
        self.execution_order.append(next_node)
        if branch_name:
            self.branch = branch_name
        self.depth += 1
