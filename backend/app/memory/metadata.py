from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class MemoryMetadata(BaseModel):
    """Metadata container for memory elements."""

    version: str = "1.0.0"
    schema_version: str = "v1"
    tags: list[str] = Field(default_factory=list)
    priority: int = Field(default=1, ge=1, le=10)
    creator: str = "system"
    access_count: int = Field(default=0, ge=0)
    last_accessed_at: Optional[datetime] = None
    custom_attributes: dict[str, Any] = Field(default_factory=dict)
