from abc import ABC, abstractmethod
from typing import Any, Optional

from app.rag.chunk import EmbeddedChunk


class VectorRepository(ABC):
    """Abstract interface for storing and searching vector embeddings."""

    @abstractmethod
    async def upsert(self, embeddings: list[EmbeddedChunk]) -> None:
        pass

    @abstractmethod
    async def delete(self, document_id: str) -> None:
        pass

    @abstractmethod
    async def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[tuple[EmbeddedChunk, float]]:
        pass

    @abstractmethod
    async def count(self) -> int:
        pass
