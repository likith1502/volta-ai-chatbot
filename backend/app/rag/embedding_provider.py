import hashlib
import math
from abc import ABC, abstractmethod

from app.rag.chunk import Chunk, EmbeddedChunk


class EmbeddingProvider(ABC):
    """Abstract interface for embedding vector providers."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        pass

    @abstractmethod
    async def embed_batch(self, chunks: list[Chunk]) -> list[EmbeddedChunk]:
        pass


class MockEmbeddingProvider(EmbeddingProvider):
    """Reference provider generating deterministic normalized pseudo-random vector embeddings."""

    def __init__(
        self, provider_id: str = "mock-embedder-v1", dimension: int = 1536
    ) -> None:
        self._provider_id = provider_id
        self._dimension = dimension

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed_text(self, text: str) -> list[float]:
        # Generate deterministic vector from text hash
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        vector = []
        for i in range(self._dimension):
            val = float(digest[i % len(digest)]) / 255.0 - 0.5
            vector.append(val)

        # Normalize vector
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [round(v / norm, 6) for v in vector]

    async def embed_batch(self, chunks: list[Chunk]) -> list[EmbeddedChunk]:
        embedded: list[EmbeddedChunk] = []
        for chk in chunks:
            vec = await self.embed_text(chk.text)
            emb = EmbeddedChunk(
                chunk_id=chk.chunk_id,
                document_id=chk.document_id,
                vector=vec,
                provider_id=self.provider_id,
                dimension=self.dimension,
            )
            embedded.append(emb)
        return embedded
