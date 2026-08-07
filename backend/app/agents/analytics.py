from pydantic import BaseModel, Field
from app.agents.role import AgentRole


class AgentAnalyticsReport(BaseModel):
    total_task_executions: int = Field(default=0, ge=0)
    success_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    average_duration_ms: float = Field(default=0.0, ge=0.0)
    most_active_role: str = "support"


class AgentAnalyticsManager:
    """Aggregates multi-agent telemetry and performance analytics."""

    def __init__(self) -> None:
        self.executions = 0
        self.successes = 0
        self.total_duration_ms = 0.0
        self.role_counts: dict[str, int] = {}

    def record_task_execution(self, duration_ms: float, success: bool, role: AgentRole) -> None:
        self.executions += 1
        if success:
            self.successes += 1
        self.total_duration_ms += duration_ms
        r_str = str(role)
        self.role_counts[r_str] = self.role_counts.get(r_str, 0) + 1

    def get_report(self) -> AgentAnalyticsReport:
        top_role = max(self.role_counts, key=self.role_counts.get) if self.role_counts else "support"
        avg_dur = (self.total_duration_ms / self.executions) if self.executions > 0 else 0.0
        rate = (self.successes / self.executions) if self.executions > 0 else 1.0

        return AgentAnalyticsReport(
            total_task_executions=self.executions,
            success_rate=round(rate, 4),
            average_duration_ms=round(avg_dur, 2),
            most_active_role=top_role,
        )
