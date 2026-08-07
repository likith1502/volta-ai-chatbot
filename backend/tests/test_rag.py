import pytest
from app.rag.budget import RetrievalBudget
from app.rag.cache import InMemoryCacheProvider
from app.rag.chunk_strategy import ChunkStrategy
from app.rag.chunker import DocumentChunker
from app.rag.context_builder import RAGContextBuilder
from app.rag.document import Document
from app.rag.embedding_provider import MockEmbeddingProvider
from app.rag.factory import RAGFactory
from app.rag.inmemory_repository import InMemoryDocumentRepository
from app.rag.inmemory_vector_repository import InMemoryVectorRepository
from app.rag.lifecycle import DocumentLifecycleState
from app.rag.reranker import DocumentReranker


@pytest.mark.asyncio
async def test_document_creation_and_lifecycle():
    doc = RAGFactory.create_document("Test Policy", "Sample body text content.")
    assert doc.title == "Test Policy"
    assert doc.status == DocumentLifecycleState.UPLOADED

    assert doc.transition_status(DocumentLifecycleState.PARSING) is True
    assert doc.status == DocumentLifecycleState.PARSING

    assert doc.transition_status(DocumentLifecycleState.CHUNKED) is True
    assert doc.status == DocumentLifecycleState.CHUNKED


@pytest.mark.asyncio
async def test_document_chunking_strategies():
    chunker = DocumentChunker()
    text = "Line 1 text.\nLine 2 text.\nLine 3 text."

    chunks_fixed = chunker.chunk_document("doc1", text, strategy=ChunkStrategy.FIXED, chunk_size=20, chunk_overlap=5)
    assert len(chunks_fixed) >= 1

    chunks_para = chunker.chunk_document("doc1", text, strategy=ChunkStrategy.PARAGRAPH)
    assert len(chunks_para) >= 1


@pytest.mark.asyncio
async def test_mock_embedding_provider():
    embedder = MockEmbeddingProvider()
    assert embedder.dimension == 1536

    vec = await embedder.embed_text("Test query string")
    assert len(vec) == 1536
    assert isinstance(vec[0], float)


@pytest.mark.asyncio
async def test_inmemory_vector_repository():
    v_repo = InMemoryVectorRepository()
    assert await v_repo.count() == 0


@pytest.mark.asyncio
async def test_pluggable_reranker_strategies():
    reranker = DocumentReranker()
    c1 = RAGFactory.create_document("D1", "Text 1")
    chunker = DocumentChunker()
    chk_list = chunker.chunk_document("doc1", "Volta scooter rental battery policy")

    items = [(chk_list[0], 0.8), (chk_list[0], 0.95)]
    res_cosine = reranker.rerank("battery", items, strategy="cosine")
    assert res_cosine[0][1] == 0.95

    res_hybrid = reranker.rerank("battery", items, strategy="hybrid")
    assert len(res_hybrid) == 2


@pytest.mark.asyncio
async def test_rag_cache_provider():
    cache = InMemoryCacheProvider()
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"
    cache.delete("key1")
    assert cache.get("key1") is None
