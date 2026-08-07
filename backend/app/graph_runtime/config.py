from pydantic import BaseModel, Field


class GraphRuntimeConfig(BaseModel):
    """Configuration settings for Graph Runtime Engine."""

    max_execution_steps: int = Field(default=50, ge=1)
    enable_parallel_execution: bool = True
    enable_auto_checkpoint: bool = True
    checkpoint_interval_steps: int = Field(default=5, ge=1)
    default_timeout_seconds: float = Field(default=30.0, ge=0.5)
    enable_streaming: bool = True
    enable_hitl: bool = True
