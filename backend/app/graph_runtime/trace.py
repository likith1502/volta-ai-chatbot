import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field


class TraceStep(BaseModel):
    """Single step recorded in an ExecutionTrace."""

    step_index: int
    node_id: str
    action: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: float = 0.0
    payload: dict[str, Any] = Field(default_factory=dict)


class ExecutionTrace(BaseModel):
    """Execution trace recorder tracking step-by-step events for single execution debugging."""

    trace_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    workflow_id: str
    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    steps: list[TraceStep] = Field(default_factory=list)

    def add_step(self, node_id: str, action: str, latency_ms: float, payload: Optional[dict] = None) -> None:
        idx = len(self.steps) + 1
        self.steps.append(
            TraceStep(
                step_index=idx,
                node_id=node_id,
                action=action,
                latency_ms=round(latency_ms, 2),
                payload=payload or {},
            )
        )
