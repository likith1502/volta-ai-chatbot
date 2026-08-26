import logging
from typing import Optional

from app.memory.factory import MemoryFactory
from app.memory.repository import MemoryRepository

logger = logging.getLogger("app.memory.registry")


class MemoryRegistry:
    """Registry managing active MemoryRepository implementations."""

    def __init__(self, repository: Optional[MemoryRepository] = None) -> None:
        self.repository = repository or MemoryFactory.create_repository()

    def register(self, repository: MemoryRepository) -> None:
        self.repository = repository
        logger.info("Registered new MemoryRepository instance in MemoryRegistry")

    def get_repository(self) -> MemoryRepository:
        return self.repository
