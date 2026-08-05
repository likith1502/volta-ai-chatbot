import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.streaming.stream_types import StreamMode


class StreamContext(BaseModel):
    """Runtime context tracking session configuration and mode for real-time streaming."""

    stream_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    execution_id: Optional[uuid.UUID] = None
    workflow_id: Optional[str] = None
    correlation_id: Optional[uuid.UUID] = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    replay_mode: StreamMode = StreamMode.LIVE
    metadata: dict[str, Any] = Field(default_factory=dict)
