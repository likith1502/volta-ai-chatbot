import logging

from app.rag.chunk import Chunk
from app.rag.embedding_registry import EmbeddingRegistry
from app.rag.plan import RetrievalPlan
from app.rag.repository import DocumentRepository
from app.rag.vector_repository import VectorRepository

logger = logging.getLogger("app.rag.retriever")


class DocumentRetriever:
    """Executes vector and keyword retrieval based on a RetrievalPlan."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        vector_repository: VectorRepository,
        embedding_registry: EmbeddingRegistry,
    ) -> None:
        self.document_repository = document_repository
        self.vector_repository = vector_repository
        self.embedding_registry = embedding_registry

    async def retrieve(self, plan: RetrievalPlan) -> list[tuple[Chunk, float]]:
        embedder = self.embedding_registry.get_provider()
        query_vec = await embedder.embed_text(plan.query)

        search_results = await self.vector_repository.search(
            query_vector=query_vec,
            top_k=plan.top_k,
            filters=plan.filters,
        )

        matched_chunks: list[tuple[Chunk, float]] = []
        for emb, score in search_results:
            chk = self.document_repository.get_chunk(emb.chunk_id)
            if chk:
                matched_chunks.append((chk, score))

        logger.info(
            f"DocumentRetriever fetched {len(matched_chunks)} chunks for query '{plan.query}'"
        )
        return matched_chunks
