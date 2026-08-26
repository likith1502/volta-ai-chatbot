from pydantic import BaseModel, Field


class AgentMetrics(BaseModel):
    total_agents: int = Field(default=0, ge=0)
    active_workers: int = Field(default=0, ge=0)
    pending_tasks: int = Field(default=0, ge=0)
    average_latency_ms: float = Field(default=0.0, ge=0.0)
