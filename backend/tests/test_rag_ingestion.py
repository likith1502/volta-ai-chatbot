import pytest
from app.rag.factory import RAGFactory
from app.rag.ingestion_runtime import IngestionRuntime
from app.rag.inmemory_repository import InMemoryDocumentRepository
from app.rag.inmemory_vector_repository import InMemoryVectorRepository
from app.rag.job_status import JobStatus
from app.rag.lifecycle import DocumentLifecycleState


@pytest.mark.asyncio
async def test_ingestion_runtime_pipeline():
    doc_repo = InMemoryDocumentRepository()
    vec_repo = InMemoryVectorRepository()
    ingestion = IngestionRuntime(doc_repo, vec_repo)

    doc = RAGFactory.create_document("EV Battery Guide", "Batteries are swappable at Volta hubs.")
    doc_repo.save_document(doc)

    job = await ingestion.ingest_document(doc, chunk_size=100, chunk_overlap=10)
    assert job.status == JobStatus.COMPLETED
    assert job.chunks_created >= 1
    assert doc.status == DocumentLifecycleState.READY
    assert await vec_repo.count() >= 1
