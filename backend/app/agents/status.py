from enum import Enum


class AgentStatus(str, Enum):
    """Operational status of an agent instance."""

    IDLE = "idle"
    BUSY = "busy"
    WAITING = "waiting"
    DELEGATING = "delegating"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"
