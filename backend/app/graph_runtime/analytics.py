from pydantic import BaseModel, Field


class GraphRuntimeAnalyticsReport(BaseModel):
    """Telemetry report analyzing workflow execution frequency and node statistics."""

    total_graph_executions: int = Field(default=0, ge=0)
    most_visited_node: str = Field(default="llm_node")
    success_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    average_duration_ms: float = Field(default=0.0, ge=0.0)


class GraphRuntimeAnalyticsManager:
    """Aggregates telemetry and performance metrics for Graph Runtime."""

    def __init__(self) -> None:
        self.executions = 0
        self.successes = 0
        self.total_duration_ms = 0.0
        self.node_counts: dict[str, int] = {}

    def record_run(
        self, duration_ms: float, success: bool, visited_nodes: list[str]
    ) -> None:
        self.executions += 1
        if success:
            self.successes += 1
        self.total_duration_ms += duration_ms
        for n in visited_nodes:
            self.node_counts[n] = self.node_counts.get(n, 0) + 1

    def get_report(self) -> GraphRuntimeAnalyticsReport:
        top_node = (
            max(self.node_counts, key=self.node_counts.get)
            if self.node_counts
            else "llm_node"
        )
        avg_dur = (
            (self.total_duration_ms / self.executions) if self.executions > 0 else 0.0
        )
        rate = (self.successes / self.executions) if self.executions > 0 else 1.0

        return GraphRuntimeAnalyticsReport(
            total_graph_executions=self.executions,
            most_visited_node=top_node,
            success_rate=round(rate, 4),
            average_duration_ms=round(avg_dur, 2),
        )
