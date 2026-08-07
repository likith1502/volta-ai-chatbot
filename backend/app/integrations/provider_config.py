from typing import Any
from pydantic import BaseModel, Field


class ProviderConfig(BaseModel):
    """Adapter-specific configuration container."""

    provider_id: str
    enabled: bool = True
    priority: int = Field(default=10, ge=1)
    weight: float = Field(default=1.0, ge=0.0)
    preferred: bool = False
    options: dict[str, Any] = Field(default_factory=dict)
