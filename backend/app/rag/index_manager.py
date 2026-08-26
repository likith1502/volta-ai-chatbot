import logging
from enum import Enum
from typing import Optional

from app.rag.chunk import EmbeddedChunk
from app.rag.index import DocumentIndex
from app.rag.index_builder import IndexBuilder
from app.rag.vector_repository import VectorRepository

logger = logging.getLogger("app.rag.index_manager")


class IndexingMode(str, Enum):
    """Indexing operations mode."""

    FULL_REBUILD = "full_rebuild"
    INCREMENTAL = "incremental"
    SINGLE_DOCUMENT = "single_document"
    DELETE_INDEX = "delete_index"


class IndexManager:
    """Manages index builds, incremental updates, single document reindexing, and vector deletion."""

    def __init__(self, vector_repository: VectorRepository) -> None:
        self.vector_repository = vector_repository
        self.builder = IndexBuilder(vector_repository)
        self.current_index = DocumentIndex()

    async def update_index(
        self,
        embeddings: list[EmbeddedChunk],
        mode: IndexingMode = IndexingMode.INCREMENTAL,
        document_id: Optional[str] = None,
    ) -> DocumentIndex:
        if mode == IndexingMode.SINGLE_DOCUMENT and document_id:
            await self.vector_repository.delete(document_id)

        await self.builder.build_index(embeddings)
        cnt = await self.vector_repository.count()
        self.current_index.total_vectors = cnt
        self.current_index.total_chunks = cnt
        logger.info(
            f"IndexManager updated index in '{mode.value}' mode. Total vectors: {cnt}"
        )
        return self.current_index
