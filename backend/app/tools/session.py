import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


class ToolSession(BaseModel):
    """Session container tracking active tool execution state across turns."""

    session_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    conversation_id: Optional[uuid.UUID] = None
    executed_tools: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    state: dict[str, Any] = Field(default_factory=dict)
