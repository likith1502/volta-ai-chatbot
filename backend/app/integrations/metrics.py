from pydantic import BaseModel, Field


class IntegrationMetrics(BaseModel):
    """Telemetry metrics for adapter latencies and availability."""

    active_adapters_count: int = Field(default=8, ge=0)
    failed_adapters_count: int = Field(default=0, ge=0)
    average_latency_ms: float = Field(default=1.2, ge=0.0)
    uptime_percentage: float = Field(default=100.0, ge=0.0, le=100.0)
