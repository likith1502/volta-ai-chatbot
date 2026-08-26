from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


class PromptTemplateMetadata(BaseModel):
    """Authoring concerns metadata container for prompt templates."""

    template_id: str
    version: str = "1.0.0"
    schema_version: str = "v1"
    author: str = "system"
    tags: list[str] = Field(default_factory=list)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PromptExecutionMetadata(BaseModel):
    """Runtime execution telemetry metadata container."""

    client_ip: Optional[str] = None
    environment: str = "development"
    user_id: Optional[str] = None
    custom_headers: dict[str, Any] = Field(default_factory=dict)
