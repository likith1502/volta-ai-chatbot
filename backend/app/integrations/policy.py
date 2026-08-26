from pydantic import BaseModel


class IntegrationPolicy(BaseModel):
    """Security and execution policy for integration adapters."""

    allow_sandbox_override: bool = True
    enforce_tls: bool = True
    require_secret_resolution: bool = True
