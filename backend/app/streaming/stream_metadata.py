from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.streaming.stream_types import StreamPriority


class StreamMetadata(BaseModel):
    """Metadata attached to a stream message or channel."""

    version: str = "1.0.0"
    schema_version: str = "1.0"
    producer: str = "system"
    source: str = "workflow_engine"
    priority: StreamPriority = StreamPriority.NORMAL
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
