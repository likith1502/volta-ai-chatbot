import logging
from app.rag.chunk import EmbeddedChunk
from app.rag.index import DocumentIndex
from app.rag.vector_repository import VectorRepository

logger = logging.getLogger("app.rag.index_builder")


class IndexBuilder:
    """Builds and updates vector indices from EmbeddedChunk collections."""

    def __init__(self, vector_repository: VectorRepository) -> None:
        self.vector_repository = vector_repository

    async def build_index(self, embeddings: list[EmbeddedChunk]) -> DocumentIndex:
        await self.vector_repository.upsert(embeddings)
        cnt = await self.vector_repository.count()
        logger.info(f"IndexBuilder upserted {len(embeddings)} vectors into index. Total vectors: {cnt}")
        return DocumentIndex(total_vectors=cnt, total_chunks=cnt)
