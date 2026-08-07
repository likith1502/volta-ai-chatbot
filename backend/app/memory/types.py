from enum import Enum


class MemoryType(str, Enum):
    """Categorical classification types for conversational memory elements."""

    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    WORKING = "working"
    SYSTEM = "system"
    USER = "user"
    SESSION = "session"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    CUSTOM = "custom"
