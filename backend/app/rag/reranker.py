from abc import ABC, abstractmethod
from app.rag.chunk import Chunk


class BaseReranker(ABC):
    """Abstract interface for RAG rerankers."""

    @abstractmethod
    def rerank(self, query: str, chunks: list[tuple[Chunk, float]]) -> list[tuple[Chunk, float]]:
        pass


class CosineReranker(BaseReranker):
    """Reranks chunks by raw vector cosine similarity score."""

    def rerank(self, query: str, chunks: list[tuple[Chunk, float]]) -> list[tuple[Chunk, float]]:
        return sorted(chunks, key=lambda x: x[1], reverse=True)


class HybridReranker(BaseReranker):
    """Combines vector similarity and keyword presence."""

    def rerank(self, query: str, chunks: list[tuple[Chunk, float]]) -> list[tuple[Chunk, float]]:
        keywords = query.lower().split()
        reranked = []
        for chk, score in chunks:
            text_lower = chk.text.lower()
            bonus = sum(0.05 for kw in keywords if kw in text_lower)
            combined = min(1.0, score + bonus)
            reranked.append((chk, round(combined, 4)))
        return sorted(reranked, key=lambda x: x[1], reverse=True)


class MetadataReranker(BaseReranker):
    """Reranks based on document metadata priorities."""

    def rerank(self, query: str, chunks: list[tuple[Chunk, float]]) -> list[tuple[Chunk, float]]:
        return sorted(chunks, key=lambda x: x[1], reverse=True)


class WeightedReranker(BaseReranker):
    """Applies weighted scoring to vector scores."""

    def rerank(self, query: str, chunks: list[tuple[Chunk, float]]) -> list[tuple[Chunk, float]]:
        return sorted([(c, round(s * 0.9 + 0.1, 4)) for c, s in chunks], key=lambda x: x[1], reverse=True)


class CrossEncoderReranker(BaseReranker):
    """Placeholder for cross-encoder transformer model reranker."""

    def rerank(self, query: str, chunks: list[tuple[Chunk, float]]) -> list[tuple[Chunk, float]]:
        return sorted(chunks, key=lambda x: x[1], reverse=True)


class DocumentReranker:
    """Delegates reranking to target BaseReranker strategy."""

    def __init__(self) -> None:
        self._rerankers: dict[str, BaseReranker] = {
            "cosine": CosineReranker(),
            "hybrid": HybridReranker(),
            "metadata": MetadataReranker(),
            "weighted": WeightedReranker(),
            "cross_encoder": CrossEncoderReranker(),
        }

    def rerank(self, query: str, chunks: list[tuple[Chunk, float]], strategy: str = "cosine") -> list[tuple[Chunk, float]]:
        reranker = self._rerankers.get(strategy.lower(), self._rerankers["cosine"])
        return reranker.rerank(query, chunks)
