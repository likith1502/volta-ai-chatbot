from abc import ABC, abstractmethod
from typing import Optional
from app.prompt.contracts import PromptResponse


class PromptCache(ABC):
    """Abstract Base Class defining prompt response caching contracts."""

    @abstractmethod
    async def get(self, cache_key: str) -> Optional[PromptResponse]:
        """Retrieves cached PromptResponse if present."""
        pass

    @abstractmethod
    async def set(self, cache_key: str, response: PromptResponse, ttl_seconds: int = 3600) -> None:
        """Stores PromptResponse in cache."""
        pass

    @abstractmethod
    async def invalidate(self, cache_key: str) -> None:
        """Invalidates cache entry by key."""
        pass
