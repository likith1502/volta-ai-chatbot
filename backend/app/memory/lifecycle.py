import logging
from enum import Enum

from app.memory.status import MemoryStatus

logger = logging.getLogger("app.memory.lifecycle")


class MemoryLifecycleState(str, Enum):
    """Formal lifecycle transition states."""

    CREATED = "created"
    ACTIVE = "active"
    PINNED = "pinned"
    ARCHIVED = "archived"
    EXPIRED = "expired"
    DELETED = "deleted"


class MemoryLifecycleManager:
    """Manages valid state transitions and lifecycle validation rules for Memory instances."""

    _ALLOWED_TRANSITIONS = {
        MemoryLifecycleState.CREATED: {MemoryStatus.ACTIVE, MemoryStatus.PINNED},
        MemoryStatus.ACTIVE: {
            MemoryStatus.PINNED,
            MemoryStatus.ARCHIVED,
            MemoryStatus.EXPIRED,
            MemoryStatus.DELETED,
        },
        MemoryStatus.PINNED: {
            MemoryStatus.ACTIVE,
            MemoryStatus.ARCHIVED,
            MemoryStatus.DELETED,
        },
        MemoryStatus.ARCHIVED: {MemoryStatus.ACTIVE, MemoryStatus.DELETED},
        MemoryStatus.EXPIRED: {MemoryStatus.ARCHIVED, MemoryStatus.DELETED},
        MemoryStatus.DELETED: set(),
    }

    @classmethod
    def can_transition(
        cls, current_status: MemoryStatus, target_status: MemoryStatus
    ) -> bool:
        """Returns True if state transition from current_status to target_status is valid."""
        allowed = cls._ALLOWED_TRANSITIONS.get(current_status, set())
        return target_status in allowed

    @classmethod
    def validate_transition(
        cls, current_status: MemoryStatus, target_status: MemoryStatus
    ) -> None:
        """Validates state transition or raises ValueError."""
        if not cls.can_transition(current_status, target_status):
            raise ValueError(
                f"Invalid memory lifecycle transition from '{current_status}' to '{target_status}'."
            )
