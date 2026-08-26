from pydantic import BaseModel, Field

from app.graph_runtime.retry import RetryPolicy
from app.graph_runtime.timeout import TimeoutPolicy


class GraphRuntimePolicy(BaseModel):
    """Centralized runtime execution policies combining retry, timeout, parallelism, and streaming settings."""

    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    timeout_policy: TimeoutPolicy = Field(default_factory=TimeoutPolicy)
    allow_parallel_nodes: bool = True
    checkpoint_interval: int = Field(default=5, ge=1)
    streaming_enabled: bool = True
    hitl_enabled: bool = True
    memory_injection_enabled: bool = True
    tool_execution_enabled: bool = True
