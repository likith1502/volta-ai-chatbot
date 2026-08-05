import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class StreamHeartbeat(BaseModel):
    """Heartbeat signal monitoring stream health and round-trip transport latency."""

    heartbeat_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    latency: float = 0.0
    status: str = "healthy"
