from pydantic import BaseModel


class IntegrationConfig(BaseModel):
    """Global configuration settings for Enterprise Integration Platform."""

    default_secret_provider: str = "env"
    enable_auto_failover: bool = True
    enable_audit_logging: bool = True
    sandbox_mode: bool = False
