from enum import Enum


class ExecutionStatus(str, Enum):
    """Lifecycle status of a graph execution lifecycle."""

    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    TIMEOUT = "timeout"
