import uuid
from typing import Any, Optional
from pydantic import BaseModel, Field


class RetrievalStepTrace(BaseModel):
    step_id: str = Field(default_factory=lambda: f"step_{uuid.uuid4().hex[:8]}")
    step_name: str
    latency_ms: float
    output: dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=lambda: 1786088000.0)


class RetrievalTrace(BaseModel):
    """Execution trace detailing retrieval steps (Query ➔ Plan ➔ Retrieve ➔ Rerank ➔ Context ➔ Citations)."""

    trace_id: str = Field(default_factory=lambda: f"trace_{uuid.uuid4().hex[:8]}")
    query: str
    steps: list[RetrievalStepTrace] = Field(default_factory=list)

    def add_step(self, step_name: str, latency_ms: float, output: Optional[dict[str, Any]] = None) -> None:
        self.steps.append(
            RetrievalStepTrace(
                step_name=step_name,
                latency_ms=round(latency_ms, 2),
                output=output or {},
            )
        )
