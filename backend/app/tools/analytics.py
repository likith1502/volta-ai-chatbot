from pydantic import BaseModel, Field


class ToolAnalyticsReport(BaseModel):
    """Telemetry report analyzing tool execution frequency and latency."""

    total_executions: int = Field(default=0, ge=0)
    top_executed_tool: str = Field(default="none")
    success_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    average_latency_ms: float = Field(default=0.0, ge=0.0)


class ToolAnalyticsManager:
    """Aggregates tool execution telemetry."""

    def __init__(self) -> None:
        self.executions = 0
        self.successes = 0
        self.total_latency_ms = 0.0
        self.tool_counts: dict[str, int] = {}

    def record_execution(
        self, tool_name: str, success: bool, latency_ms: float
    ) -> None:
        self.executions += 1
        if success:
            self.successes += 1
        self.total_latency_ms += latency_ms
        self.tool_counts[tool_name] = self.tool_counts.get(tool_name, 0) + 1

    def get_report(self) -> ToolAnalyticsReport:
        top_tool = (
            max(self.tool_counts, key=self.tool_counts.get)
            if self.tool_counts
            else "none"
        )
        avg_lat = (
            (self.total_latency_ms / self.executions) if self.executions > 0 else 0.0
        )
        rate = (self.successes / self.executions) if self.executions > 0 else 1.0

        return ToolAnalyticsReport(
            total_executions=self.executions,
            top_executed_tool=top_tool,
            success_rate=round(rate, 4),
            average_latency_ms=round(avg_lat, 2),
        )
