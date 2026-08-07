from pydantic import BaseModel, Field


class GraphRuntimeMetrics(BaseModel):
    """Runtime execution metrics container."""

    total_runs: int = Field(default=0, ge=0)
    active_sessions: int = Field(default=0, ge=0)
    paused_sessions: int = Field(default=0, ge=0)
    average_node_latency_ms: float = Field(default=0.0, ge=0.0)
