import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IntegrationContext(BaseModel):
    """Unified context container passed to integration adapters."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    context_id: str = Field(default_factory=lambda: f"ctx_{uuid.uuid4().hex[:8]}")
    environment: str = "development"
    sandbox_mode: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    resolved_secrets: dict[str, str] = Field(default_factory=dict)
    created_at: float = Field(default_factory=lambda: 1786088000.0)
