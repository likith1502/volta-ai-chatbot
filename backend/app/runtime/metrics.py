from pydantic import BaseModel, Field
from app.runtime.contracts import RuntimeTokenUsage


class RuntimeMetrics(BaseModel):
    """Execution telemetry container tracking latency, breakdown timings, token counts, and cost."""

    latency_ms: float = Field(default=0.0, ge=0.0, description="Total turn execution latency in milliseconds")
    provider_time_ms: float = Field(default=0.0, ge=0.0, description="Time spent awaiting remote LLM provider")
    serialization_time_ms: float = Field(default=0.0, ge=0.0, description="Time spent serializing request/response payload")
    total_execution_time_ms: float = Field(default=0.0, ge=0.0, description="Total wall-clock execution time")
    retries_attempted: int = Field(default=0, ge=0, description="Number of backoff retry attempts executed")
    tokens: RuntimeTokenUsage = Field(default_factory=RuntimeTokenUsage)
    estimated_cost_usd: float = Field(default=0.0, ge=0.0)
