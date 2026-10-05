import uuid
from abc import ABC, abstractmethod
from typing import Optional
from app.memory.memory import Memory
from app.memory.status import MemoryStatus


class MemoryRepository(ABC):
    """Abstract Base Class defining storage contracts for memory management (InMemory, Database, Vector Store, Remote Hub)."""

    @abstractmethod
    async def save(self, memory: Memory) -> None:
        """Saves or updates a memory element."""
        pass

    @abstractmethod
    async def get_by_id(self, memory_id: uuid.UUID) -> Optional[Memory]:
        """Retrieves memory by UUID."""
        pass

    @abstractmethod
    async def delete(self, memory_id: uuid.UUID) -> bool:
        """Deletes memory by UUID."""
        pass

    @abstractmethod
    async def list_by_conversation(
        self,
        conversation_id: uuid.UUID,
        status: Optional[MemoryStatus] = None,
        limit: int = 100,
    ) -> list[Memory]:
        """Lists memories by conversation ID."""
        pass

    @abstractmethod
    async def list_all(self, limit: int = 100) -> list[Memory]:
        """Lists all stored memories."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clears all stored memories."""
        pass
