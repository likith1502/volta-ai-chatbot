from datetime import datetime, timezone
from pydantic import BaseModel, Field


class PromptTraceStep(BaseModel):
    """Execution trace step recording pipeline stage timing and status."""

    stage_name: str = Field(..., description="'validation', 'security', 'injection', 'rendering', 'optimization', 'compilation'")
    status: str = Field(default="COMPLETED", description="'COMPLETED', 'SKIPPED', 'FAILED'")
    duration_ms: float = Field(default=0.0, ge=0.0)
    details: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PromptTrace(BaseModel):
    """Complete execution trace recording per-stage pipeline performance."""

    steps: list[PromptTraceStep] = Field(default_factory=list)
    total_duration_ms: float = Field(default=0.0, ge=0.0)

    def add_step(self, stage_name: str, duration_ms: float, status: str = "COMPLETED", details: str = "") -> None:
        self.steps.append(PromptTraceStep(stage_name=stage_name, duration_ms=duration_ms, status=status, details=details))
        self.total_duration_ms += duration_ms
