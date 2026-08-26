from pydantic import BaseModel, Field


class IntegrationStatistics(BaseModel):
    """Statistics snapshot for Integration Platform operations."""

    total_providers_registered: int = Field(default=8, ge=0)
    total_health_checks_executed: int = Field(default=0, ge=0)
    total_failovers_triggered: int = Field(default=0, ge=0)
    average_adapter_latency_ms: float = Field(default=1.5, ge=0.0)
