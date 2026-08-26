from enum import Enum


class GraphRuntimeState(str, Enum):
    """Execution lifecycle state for Graph Runtime sessions."""

    RUNNING = "running"
    WAITING = "waiting"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    INTERRUPTED = "interrupted"
