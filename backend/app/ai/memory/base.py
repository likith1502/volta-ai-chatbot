import uuid
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory


class MemoryStrategy(ABC):
    """Abstract interface for conversation memory retrieval strategies."""

    @abstractmethod
    async def retrieve_memories(
        self,
        session: AsyncSession,
        conversation_id: uuid.UUID,
        limit: int = 10,
    ) -> list[Memory]:
        """Retrieves memories relevant to the conversation session."""
        pass
