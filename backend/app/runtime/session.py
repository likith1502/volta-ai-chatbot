import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field


class RuntimeSession(BaseModel):
    """Runtime execution session container linking user conversation sessions to runtime execution state."""

    session_id: str = Field(default_factory=lambda: f"sess_{uuid.uuid4().hex[:12]}")
    conversation_id: Optional[uuid.UUID] = None
    provider: str
    model: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    turn_count: int = Field(default=0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def touch(self) -> None:
        """Updates last_activity timestamp and increments turn_count."""
        self.last_activity = datetime.now(timezone.utc)
        self.turn_count += 1
