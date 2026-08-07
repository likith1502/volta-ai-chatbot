from typing import Any
from pydantic import BaseModel, Field


class PromptAnalyticsReport(BaseModel):
    """Analytics and usage telemetry report across all prompt executions."""

    total_executions: int = Field(default=0, ge=0)
    total_renders: int = Field(default=0, ge=0)
    average_render_time_ms: float = Field(default=0.0, ge=0.0)
    failure_rate_pct: float = Field(default=0.0, ge=0.0)
    top_templates: list[str] = Field(default_factory=list)
    average_token_estimate: float = Field(default=0.0, ge=0.0)
    average_compression_ratio: float = Field(default=1.0, ge=0.0)


class PromptAnalyticsManager:
    """Aggregates execution analytics telemetry for dashboard inspection."""

    def __init__(self) -> None:
        self.render_count = 0
        self.exec_count = 0
        self.total_render_ms = 0.0
        self.failures = 0
        self.template_counts: dict[str, int] = {}

    def record_render(self, template_id: str, duration_ms: float, is_success: bool = True) -> None:
        self.render_count += 1
        self.total_render_ms += duration_ms
        self.template_counts[template_id] = self.template_counts.get(template_id, 0) + 1
        if not is_success:
            self.failures += 1

    def record_execution(self, template_id: str) -> None:
        self.exec_count += 1

    def get_report(self) -> PromptAnalyticsReport:
        avg_render = (self.total_render_ms / self.render_count) if self.render_count > 0 else 0.0
        fail_pct = (self.failures / self.render_count * 100.0) if self.render_count > 0 else 0.0
        top = sorted(self.template_counts.keys(), key=lambda k: self.template_counts[k], reverse=True)[:5]

        return PromptAnalyticsReport(
            total_executions=self.exec_count,
            total_renders=self.render_count,
            average_render_time_ms=avg_render,
            failure_rate_pct=fail_pct,
            top_templates=top,
        )
