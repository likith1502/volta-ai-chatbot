import uuid
from typing import Optional

from app.memory.memory import Memory
from app.memory.status import MemoryStatus
from app.memory.types import MemoryType


class MemoryFilter:
    """Filter criteria container for querying memory elements."""

    def __init__(
        self,
        conversation_id: Optional[uuid.UUID] = None,
        execution_id: Optional[uuid.UUID] = None,
        memory_type: Optional[MemoryType] = None,
        status: Optional[MemoryStatus] = None,
        min_importance: Optional[float] = None,
        tags: Optional[list[str]] = None,
    ) -> None:
        self.conversation_id = conversation_id
        self.execution_id = execution_id
        self.memory_type = memory_type
        self.status = status
        self.min_importance = min_importance
        self.tags = tags or []

    def matches(self, memory: Memory) -> bool:
        """Returns True if memory matches all specified non-None criteria."""
        if self.conversation_id and memory.conversation_id != self.conversation_id:
            return False
        if self.execution_id and memory.execution_id != self.execution_id:
            return False
        if self.memory_type and memory.memory_type != self.memory_type:
            return False
        if self.status and memory.status != self.status:
            return False
        if self.min_importance is not None and memory.importance < self.min_importance:
            return False
        if self.tags and not any(t in memory.metadata.tags for t in self.tags):
            return False
        return True
