from typing import Any

from pydantic import BaseModel, Field


class ExecutionMetrics(BaseModel):
    """Runtime statistics and metrics captured during graph execution."""

    execution_time: float = 0.0
    node_count: int = 0
    visited_nodes: list[str] = Field(default_factory=list)
    failed_nodes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)
    success_rate: float = 1.0

    def compute_success_rate(self) -> None:
        """Recalculates success rate based on visited and failed node counts."""
        if not self.visited_nodes:
            self.success_rate = 1.0
        else:
            successful = len(self.visited_nodes) - len(self.failed_nodes)
            self.success_rate = round(max(0.0, successful / len(self.visited_nodes)), 4)
