from pydantic import BaseModel, Field


class ToolStatistics(BaseModel):
    """Snapshot container recording current state statistics of the tool repository."""

    total_registered_tools: int = Field(default=0, ge=0)
    active_tools: int = Field(default=0, ge=0)
    deprecated_tools: int = Field(default=0, ge=0)
    disabled_tools: int = Field(default=0, ge=0)
    total_executions: int = Field(default=0, ge=0)
    average_execution_latency_ms: float = Field(default=0.0, ge=0.0)
