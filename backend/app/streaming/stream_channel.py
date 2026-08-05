from pydantic import BaseModel, Field

from app.streaming.stream_metadata import StreamMetadata


class StreamChannel(BaseModel):
    """Logical channel grouping stream message topics and active subscriber bindings."""

    channel_id: str
    name: str
    description: str = ""
    subscribers: list[str] = Field(default_factory=list)
    metadata: StreamMetadata = Field(default_factory=StreamMetadata)
