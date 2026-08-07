from pydantic import BaseModel, Field


class GraphRuntimeStatistics(BaseModel):
    """Snapshot statistics of Graph Runtime operations."""

    total_executions: int = Field(default=0, ge=0)
    successful_executions: int = Field(default=0, ge=0)
    failed_executions: int = Field(default=0, ge=0)
    interrupted_executions: int = Field(default=0, ge=0)
    average_latency_ms: float = Field(default=0.0, ge=0.0)
    total_checkpoints_created: int = Field(default=0, ge=0)
