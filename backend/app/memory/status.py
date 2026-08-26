from enum import Enum


class MemoryStatus(str, Enum):
    """Lifecycle status states for memory entries."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    EXPIRED = "expired"
    DELETED = "deleted"
    PINNED = "pinned"
