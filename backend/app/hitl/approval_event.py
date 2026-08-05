import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ApprovalEvent(BaseModel):
    """Event DTO placeholder representing human-in-the-loop lifecycle notifications."""

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: str = "approval_created"
    approval_id: uuid.UUID
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = Field(default_factory=dict)
