from pydantic import BaseModel, Field


class ToolMetrics(BaseModel):
    """Runtime execution metrics container for tool operations."""

    total_tool_calls: int = Field(default=0, ge=0)
    successful_calls: int = Field(default=0, ge=0)
    failed_calls: int = Field(default=0, ge=0)
    timed_out_calls: int = Field(default=0, ge=0)
    average_latency_ms: float = Field(default=0.0, ge=0.0)
