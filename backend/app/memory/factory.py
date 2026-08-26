import logging
from typing import Optional

from app.memory.config import MemoryConfiguration
from app.memory.inmemory_repository import InMemoryMemoryRepository
from app.memory.repository import MemoryRepository

logger = logging.getLogger("app.memory.factory")


class MemoryFactory:
    """Factory constructing MemoryRepository instances based on MemoryConfiguration."""

    @staticmethod
    def create_repository(
        config: Optional[MemoryConfiguration] = None,
    ) -> MemoryRepository:
        config = config or MemoryConfiguration()
        # Default in-memory reference implementation
        repo = InMemoryMemoryRepository(
            capacity=config.max_memories_per_conversation * 4
        )
        logger.info("Constructed InMemoryMemoryRepository via MemoryFactory")
        return repo
