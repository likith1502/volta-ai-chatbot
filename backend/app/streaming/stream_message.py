import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.streaming.stream_metadata import StreamMetadata
from app.streaming.stream_types import StreamType


class StreamMessage(BaseModel):
    """
    Immutable real-time stream message container.
    Messages are transport-independent and strictly frozen upon instantiation.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    message_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    stream_type: StreamType = StreamType.EVENT
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[uuid.UUID] = None
    execution_id: Optional[uuid.UUID] = None
    workflow_id: Optional[str] = None
    graph_id: Optional[str] = None
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: StreamMetadata = Field(default_factory=StreamMetadata)
