from pydantic import BaseModel, Field


class IntegrationRuntimeConfig(BaseModel):
    """Runtime execution bounds and timeout settings."""

    connection_timeout_seconds: float = Field(default=5.0, ge=0.1)
    health_check_interval_seconds: float = Field(default=30.0, ge=1.0)
    max_reconnect_attempts: int = Field(default=3, ge=1)
