import uuid
from typing import Any

from pydantic import BaseModel, Field

from app.streaming.stream_types import StreamPriority


class StreamSubscription(BaseModel):
    """Binding model representing a subscriber's registered interest in a stream."""

    subscription_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    subscriber_id: str
    filters: list[Any] = Field(default_factory=list)
    priority: StreamPriority = StreamPriority.NORMAL
    active: bool = True
