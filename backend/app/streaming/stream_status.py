from enum import Enum


class StreamStatus(str, Enum):
    """Lifecycle states of a stream or streaming channel."""

    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    FAILED = "failed"
