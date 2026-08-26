from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ToolMetadata(BaseModel):
    """Metadata container for tool elements."""

    version: str = "1.0.0"
    author: str = "system"
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    custom_attributes: dict[str, Any] = Field(default_factory=dict)
