import pytest
from app.rag.factory import RAGFactory
from app.rag.ingestion_runtime import IngestionRuntime
from app.rag.inmemory_repository import InMemoryDocumentRepository
from app.rag.inmemory_vector_repository import InMemoryVectorRepository
from app.rag.query_runtime import QueryRuntime


@pytest.mark.asyncio
async def test_query_runtime_retrieval_and_explanation():
    doc_repo = InMemoryDocumentRepository()
    vec_repo = InMemoryVectorRepository()

    ingestion = IngestionRuntime(doc_repo, vec_repo)
    query_rt = QueryRuntime(doc_repo, vec_repo)

    doc = RAGFactory.create_document("Helmet Safety", "Helmets are mandatory for all electric scooter rides.")
    doc_repo.save_document(doc)
    await ingestion.ingest_document(doc)

    context, trace, explanation = await query_rt.execute_query("helmet requirement", top_k=3)

    assert context.query == "helmet requirement"
    assert len(context.citations) >= 1
    assert len(trace.steps) == 5
    assert explanation.reranker == "cosine"
