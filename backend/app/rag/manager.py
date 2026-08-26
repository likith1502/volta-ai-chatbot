import logging
import time
from typing import Any, Optional

from app.prompt.manager import PromptManager
from app.rag.analytics import RAGAnalyticsManager
from app.rag.cache import CacheProvider, InMemoryCacheProvider
from app.rag.context import RAGContext
from app.rag.contracts import (
    RAGDocumentPayload,
    RAGIngestPayload,
    RAGQueryPayload,
    RAGRetrievePayload,
)
from app.rag.document import Document
from app.rag.embedding_registry import EmbeddingRegistry
from app.rag.explanation import RetrievalExplanation
from app.rag.factory import RAGFactory
from app.rag.health import RAGHealthManager
from app.rag.ingestion_runtime import IngestionRuntime
from app.rag.inmemory_repository import InMemoryDocumentRepository
from app.rag.inmemory_vector_repository import InMemoryVectorRepository
from app.rag.job import IngestionJob
from app.rag.job_manager import JobManager
from app.rag.parser_registry import ParserRegistry
from app.rag.query_runtime import QueryRuntime
from app.rag.repository import DocumentRepository
from app.rag.statistics import RAGStatistics
from app.rag.trace import RetrievalTrace
from app.rag.vector_repository import VectorRepository
from app.runtime.manager import RuntimeManager

logger = logging.getLogger("app.rag.manager")


class RAGManager:
    """Single central orchestration entry point for the Enterprise RAG Engine.

    Coordinates document ingestion, indexing, retrieval, reranking, context assembly, citations, and delegates final generation to frozen PromptManager (v7.1) and RuntimeManager (v7.0).
    """

    def __init__(
        self,
        document_repository: Optional[DocumentRepository] = None,
        vector_repository: Optional[VectorRepository] = None,
        embedding_registry: Optional[EmbeddingRegistry] = None,
        parser_registry: Optional[ParserRegistry] = None,
        cache: Optional[CacheProvider] = None,
        prompt_manager: Optional[PromptManager] = None,
        runtime_manager: Optional[RuntimeManager] = None,
    ) -> None:
        self.document_repository = document_repository or InMemoryDocumentRepository()
        self.vector_repository = vector_repository or InMemoryVectorRepository()
        self.embedding_registry = embedding_registry or EmbeddingRegistry()
        self.parser_registry = parser_registry or ParserRegistry()
        self.cache = cache or InMemoryCacheProvider()
        self.job_manager = JobManager()

        self.prompt_manager = prompt_manager or PromptManager()
        self.runtime_manager = runtime_manager or RuntimeManager()

        self.ingestion_runtime = IngestionRuntime(
            document_repository=self.document_repository,
            vector_repository=self.vector_repository,
            parser_registry=self.parser_registry,
            embedding_registry=self.embedding_registry,
            job_manager=self.job_manager,
        )

        self.query_runtime = QueryRuntime(
            document_repository=self.document_repository,
            vector_repository=self.vector_repository,
            embedding_registry=self.embedding_registry,
            cache=self.cache,
        )

        self.health_manager = RAGHealthManager(
            self.document_repository, self.vector_repository
        )
        self.analytics_manager = RAGAnalyticsManager()
        self.statistics = RAGStatistics()

        # Seed sample mobility reference document
        self._seed_reference_documents()

    def _seed_reference_documents(self) -> None:
        if not self.document_repository.list_documents():
            sample_text = (
                "VOLTA Urban Mobility Platform Service Guide.\n\n"
                "Electric scooter rentals operate across central station, airport terminal 1, and downtown square. "
                "Helmet wearing is mandatory. Maximum speed limit is 25 km/h on designated bike lanes. "
                "Base unlock fee is €1.00 plus €0.20 per minute. Customer support is available 24/7."
            )
            doc = RAGFactory.create_document(
                title="Volta Scooter Rental Policy & Operating Guidelines",
                text=sample_text,
                mime_type="text/plain",
                source_uri="https://volta.mobility/docs/policy.txt",
            )
            self.document_repository.save_document(doc)

    async def add_document(self, payload: RAGDocumentPayload) -> Document:
        """Adds a document to repository."""
        doc = RAGFactory.create_document(
            title=payload.title, text=payload.raw_text, mime_type=payload.mime_type
        )
        self.document_repository.save_document(doc)
        self.statistics.total_documents_ingested += 1
        return doc

    async def ingest_document(self, payload: RAGIngestPayload) -> IngestionJob:
        """Executes ingestion pipeline for a document ID."""
        doc = self.document_repository.get_document(payload.document_id)
        if not doc:
            raise ValueError(f"Document '{payload.document_id}' not found.")

        job = await self.ingestion_runtime.ingest_document(
            document=doc,
            chunk_size=payload.chunk_size,
            chunk_overlap=payload.chunk_overlap,
        )
        self.statistics.total_chunks_indexed += job.chunks_created
        return job

    async def retrieve_context(
        self, payload: RAGRetrievePayload
    ) -> tuple[RAGContext, RetrievalTrace, RetrievalExplanation]:
        """Retrieves and reranks context for query."""
        t0 = time.perf_counter()
        context, trace, explanation = await self.query_runtime.execute_query(
            query=payload.query,
            top_k=payload.top_k,
            strategy=payload.strategy,
            reranker=payload.reranker,
        )
        dt = (time.perf_counter() - t0) * 1000.0
        self.analytics_manager.record_retrieval(
            duration_ms=dt, chunks_count=len(context.citations)
        )
        self.statistics.total_queries_processed += 1
        return context, trace, explanation

    async def answer_query(self, payload: RAGQueryPayload) -> dict[str, Any]:
        """Executes RAG retrieval, context assembly, and delegates response generation to frozen RuntimeManager."""
        context, trace, explanation = await self.query_runtime.execute_query(
            query=payload.query, top_k=payload.top_k
        )

        # Delegate generation to frozen RuntimeManager via public interface
        prompt_text = f"Context:\n{context.context_text}\n\nUser Question: {payload.query}\nAnswer accurately using only the provided context."

        from app.runtime.contracts import ChatMessage, RuntimeRequest

        req = RuntimeRequest(
            messages=[ChatMessage(role="user", content=prompt_text)],
            provider="mock",
            model="mock-model-v1",
        )
        runtime_res = await self.runtime_manager.execute(req)

        answer_text = (
            runtime_res.response.content
            if runtime_res.response
            else "No response generated."
        )

        return {
            "query": payload.query,
            "answer": answer_text,
            "context": context.model_dump(),
            "citations": [c.model_dump() for c in context.citations],
            "trace": trace.model_dump(),
            "explanation": explanation.model_dump(),
        }

    async def get_document(self, document_id: str) -> Optional[Document]:
        return self.document_repository.get_document(document_id)

    async def list_documents(self) -> list[Document]:
        return self.document_repository.list_documents()

    async def delete_document(self, document_id: str) -> bool:
        await self.vector_repository.delete(document_id)
        return self.document_repository.delete_document(document_id)
