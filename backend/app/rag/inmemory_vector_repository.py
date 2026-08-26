import math
from typing import Any, Optional

from app.rag.chunk import EmbeddedChunk
from app.rag.vector_repository import VectorRepository


class InMemoryVectorRepository(VectorRepository):
    """In-memory cosine similarity implementation of VectorRepository."""

    def __init__(self) -> None:
        self._vectors: dict[str, EmbeddedChunk] = {}

    async def upsert(self, embeddings: list[EmbeddedChunk]) -> None:
        for emb in embeddings:
            self._vectors[emb.embedded_chunk_id] = emb

    async def delete(self, document_id: str) -> None:
        to_del = [
            eid for eid, emb in self._vectors.items() if emb.document_id == document_id
        ]
        for eid in to_del:
            del self._vectors[eid]

    async def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[tuple[EmbeddedChunk, float]]:
        scores: list[tuple[EmbeddedChunk, float]] = []

        q_norm = math.sqrt(sum(v * v for v in query_vector)) or 1.0

        for emb in self._vectors.values():
            if not emb.vector or len(emb.vector) != len(query_vector):
                sim = 0.5
            else:
                dot = sum(a * b for a, b in zip(query_vector, emb.vector))
                e_norm = math.sqrt(sum(v * v for v in emb.vector)) or 1.0
                sim = max(0.0, min(1.0, (dot / (q_norm * e_norm) + 1.0) / 2.0))

            scores.append((emb, round(sim, 4)))

        scores.sort(key=lambda item: item[1], reverse=True)
        return scores[:top_k]

    async def count(self) -> int:
        return len(self._vectors)
