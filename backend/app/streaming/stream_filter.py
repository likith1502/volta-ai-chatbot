import uuid
from typing import Optional

from pydantic import BaseModel, Field

from app.streaming.stream_message import StreamMessage
from app.streaming.stream_types import StreamPriority, StreamType

_PRIORITY_WEIGHTS = {
    StreamPriority.CRITICAL: 4,
    StreamPriority.HIGH: 3,
    StreamPriority.NORMAL: 2,
    StreamPriority.LOW: 1,
    StreamPriority.BACKGROUND: 0,
}


class StreamFilter(BaseModel):
    """Predicate filter matching stream messages against configured subscription criteria."""

    stream_types: list[StreamType] = Field(default_factory=list)
    execution_id: Optional[uuid.UUID] = None
    workflow_id: Optional[str] = None
    graph_id: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    min_priority: Optional[StreamPriority] = None

    def matches(self, message: StreamMessage) -> bool:
        """Evaluates whether message satisfies all specified non-empty criteria."""
        if self.stream_types and message.stream_type not in self.stream_types:
            return False

        if self.execution_id and message.execution_id != self.execution_id:
            return False

        if self.workflow_id and message.workflow_id != self.workflow_id:
            return False

        if self.graph_id and message.graph_id != self.graph_id:
            return False

        if self.tags:
            msg_tags = set(message.metadata.tags)
            if not any(tag in msg_tags for tag in self.tags):
                return False

        if self.min_priority:
            min_weight = _PRIORITY_WEIGHTS.get(self.min_priority, 0)
            msg_weight = _PRIORITY_WEIGHTS.get(message.metadata.priority, 0)
            if msg_weight < min_weight:
                return False

        return True
