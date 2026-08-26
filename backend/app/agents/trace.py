import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentTraceStep(BaseModel):
    step_id: str = Field(default_factory=lambda: f"step_{uuid.uuid4().hex[:8]}")
    agent_id: str
    action: str
    latency_ms: float
    output: dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=lambda: 1786088000.0)


class AgentTrace(BaseModel):
    trace_id: str = Field(default_factory=lambda: f"trace_{uuid.uuid4().hex[:8]}")
    steps: list[AgentTraceStep] = Field(default_factory=list)

    def add_step(
        self,
        agent_id: str,
        action: str,
        latency_ms: float,
        output: Optional[dict[str, Any]] = None,
    ) -> None:
        self.steps.append(
            AgentTraceStep(
                agent_id=agent_id,
                action=action,
                latency_ms=round(latency_ms, 2),
                output=output or {},
            )
        )
