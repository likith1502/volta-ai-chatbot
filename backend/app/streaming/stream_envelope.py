from typing import Any

from pydantic import BaseModel, Field

from app.streaming.stream_message import StreamMessage


class StreamEnvelope(BaseModel):
    """Transport envelope wrapping StreamMessage with routing headers and metadata."""

    headers: dict[str, str] = Field(default_factory=dict)
    message: StreamMessage
    delivery_metadata: dict[str, Any] = Field(default_factory=dict)
    serialization_format: str = "json"
