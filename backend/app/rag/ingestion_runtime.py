import logging
from typing import Optional
from app.rag.chunker import DocumentChunker
from app.rag.document import Document
from app.rag.embedding_registry import EmbeddingRegistry
from app.rag.index import DocumentIndex
from app.rag.index_manager import IndexingMode, IndexManager
from app.rag.job import IngestionJob
from app.rag.job_manager import JobManager, JobStatus
from app.rag.lifecycle import DocumentLifecycleState
from app.rag.parser_registry import ParserRegistry
from app.rag.repository import DocumentRepository
from app.rag.vector_repository import VectorRepository

logger = logging.getLogger("app.rag.ingestion_runtime")


class IngestionRuntime:
    """Orchestrates document ingestion pipeline: Parse ➔ Chunk ➔ Embed ➔ Index."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        vector_repository: VectorRepository,
        parser_registry: Optional[ParserRegistry] = None,
        embedding_registry: Optional[EmbeddingRegistry] = None,
        job_manager: Optional[JobManager] = None,
    ) -> None:
        self.document_repository = document_repository
        self.vector_repository = vector_repository
        self.parser_registry = parser_registry or ParserRegistry()
        self.embedding_registry = embedding_registry or EmbeddingRegistry()
        self.job_manager = job_manager or JobManager()
        self.chunker = DocumentChunker()
        self.index_manager = IndexManager(vector_repository)

    async def ingest_document(self, document: Document, chunk_size: int = 512, chunk_overlap: int = 64) -> IngestionJob:
        """Executes full ingestion pipeline for a document."""
        job = self.job_manager.create_job(document.document_id)
        self.job_manager.update_job_status(job.job_id, JobStatus.PROCESSING)

        try:
            # 1. Parse
            document.transition_status(DocumentLifecycleState.PARSING)
            parser = self.parser_registry.get_parser_for_mime(document.mime_type)
            parsed_text = parser.parse(document.raw_text, document.metadata) if parser else document.raw_text

            # 2. Chunk
            chunks = self.chunker.chunk_document(
                document_id=document.document_id,
                text=parsed_text,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                metadata=document.metadata,
            )
            document.transition_status(DocumentLifecycleState.CHUNKED)
            self.document_repository.save_chunks(chunks)

            # 3. Embed
            embedder = self.embedding_registry.get_provider()
            embeddings = await embedder.embed_batch(chunks)

            # 4. Index
            document.transition_status(DocumentLifecycleState.INDEXED)
            await self.index_manager.update_index(
                embeddings,
                mode=IndexingMode.SINGLE_DOCUMENT,
                document_id=document.document_id,
            )

            document.transition_status(DocumentLifecycleState.READY)
            self.document_repository.save_document(document)

            self.job_manager.update_job_status(
                job.job_id,
                status=JobStatus.COMPLETED,
                chunks=len(chunks),
                embeddings=len(embeddings),
            )
            logger.info(f"IngestionRuntime successfully ingested document '{document.document_id}' with {len(chunks)} chunks.")
            return job

        except Exception as exc:
            logger.error(f"IngestionRuntime failed for document '{document.document_id}': {exc}")
            self.job_manager.update_job_status(job.job_id, status=JobStatus.FAILED, error=str(exc))
            raise exc
