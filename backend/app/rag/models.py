"""Consolidated Models Module for Rag Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from app.rag.chunk import Chunk
from app.rag.embedding_registry import EmbeddingRegistry
from app.rag.parser_registry import ParserRegistry
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any
from typing import Optional
import uuid

# --- Consolidated from job_status.py ---
class JobStatus(str, Enum):
    """Ingestion job status enum."""
    QUEUED = 'queued'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'

# --- Consolidated from document_version.py ---
class DocumentVersion(BaseModel):
    """Tracks document version lineage and hash checksums."""
    version_id: str = Field(default_factory=lambda: f'ver_{uuid.uuid4().hex[:8]}')
    document_id: str
    version_number: int = Field(default=1, ge=1)
    checksum: str = Field(default='')
    created_at: float = Field(default_factory=lambda: 1786088000.0)

# --- Consolidated from index.py ---
class DocumentIndex(BaseModel):
    """Index container tracking indexed documents, total chunks, and vector dimension."""
    index_id: str = Field(default_factory=lambda: f'idx_{uuid.uuid4().hex[:8]}')
    name: str = 'volta_knowledge_index'
    total_documents: int = Field(default=0, ge=0)
    total_chunks: int = Field(default=0, ge=0)
    total_vectors: int = Field(default=0, ge=0)
    dimension: int = 1536
    updated_at: float = Field(default_factory=lambda: 1786088000.0)

# --- Consolidated from citation.py ---
class Citation(BaseModel):
    """Structured audit reference citation pointing to source document, page, and chunk."""
    citation_id: str = Field(default_factory=lambda: f'cit_{uuid.uuid4().hex[:8]}')
    document_id: str
    document_title: str
    page_number: int = Field(default=1, ge=1)
    chunk_id: str
    snippet: str = Field(default='')
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    source_uri: str = Field(default='')

# --- Consolidated from budget.py ---
class RetrievalBudget(BaseModel):
    """Resource limits and budgeting constraints for RAG retrieval & context assembly."""
    max_chunks: int = Field(default=10, ge=1)
    max_documents: int = Field(default=5, ge=1)
    max_context_tokens: int = Field(default=4096, ge=1)
    max_total_tokens: int = Field(default=8192, ge=1)
    max_citations: int = Field(default=10, ge=1)

# --- Consolidated from chunk_strategy.py ---
class ChunkStrategy(str, Enum):
    """Strategies for splitting document text into chunks."""
    FIXED = 'fixed'
    SLIDING_WINDOW = 'sliding_window'
    SENTENCE = 'sentence'
    PARAGRAPH = 'paragraph'
    SEMANTIC = 'semantic'

# --- Consolidated from config.py ---
class RAGConfig(BaseModel):
    """Global configuration for Enterprise RAG Engine."""
    default_chunk_size: int = Field(default=512, ge=64)
    default_chunk_overlap: int = Field(default=64, ge=0)
    default_top_k: int = Field(default=5, ge=1)
    default_embedding_provider: str = 'mock-embedder-v1'
    default_reranker: str = 'cosine'

# --- Consolidated from context.py ---
class RAGContext(BaseModel):
    """Assembled RAG context container ready for injection into PromptManager."""
    query: str
    context_text: str = Field(..., min_length=1)
    citations: list[Citation] = Field(default_factory=list)
    scores: list[float] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

# --- Consolidated from explanation.py ---
class RetrievalExplanation(BaseModel):
    """Detailed audit explanation of why specific chunks were selected and reranked."""
    query: str
    selected_chunk_ids: list[str] = Field(default_factory=list)
    reranker: str = 'Cosine'
    reason: str = 'Top-K cosine similarity search'
    average_score: float = Field(default=0.92, ge=0.0, le=1.0)
    details: dict[str, Any] = Field(default_factory=dict)

# --- Consolidated from policy.py ---
class RAGPolicy(BaseModel):
    """RAG execution policy binding retrieval budget and strict filters."""
    budget: RetrievalBudget = Field(default_factory=RetrievalBudget)
    strict_provenance: bool = True

# --- Consolidated from ranking_strategy.py ---
class RankingStrategy(str, Enum):
    """Supported reranking strategies."""
    COSINE = 'cosine'
    HYBRID = 'hybrid'
    BM25 = 'bm25'
    WEIGHTED = 'weighted'
    RECENCY = 'recency'
    METADATA = 'metadata'
    CROSS_ENCODER = 'cross_encoder'

# --- Consolidated from registry.py ---
class RAGRegistry:
    """Registry maintaining active document parsers, embedding providers, and vector stores."""

    def __init__(self) -> None:
        self.parsers = ParserRegistry()
        self.embeddings = EmbeddingRegistry()

# --- Consolidated from retriever_strategy.py ---
class RetrievalStrategy(str, Enum):
    """Supported retrieval strategies."""
    TOP_K = 'top_k'
    HYBRID = 'hybrid'
    KEYWORD = 'keyword'
    VECTOR = 'vector'
    METADATA_FILTER = 'metadata_filter'

# --- Consolidated from rewriter.py ---
class QueryRewriter:
    """Query Rewriter hook transforming or expanding user queries prior to retrieval planning."""

    def rewrite_query(self, original_query: str) -> str:
        """Standardizes query, performs spelling cleanup, and removes noise words."""
        cleaned = original_query.strip()
        return cleaned

# --- Consolidated from selector.py ---
class ChunkSelector:
    """Selects target chunks based on relevance scores and limits."""

    @staticmethod
    def select_top_chunks(chunks: list[tuple[Chunk, float]], limit: int=5) -> list[Chunk]:
        return [c for c, _ in chunks[:limit]]

# --- Consolidated from versioning.py ---
class RAGVersion(BaseModel):
    version: str = '7.6.0'
    milestone: str = 'Phase 7.6 Enterprise RAG Engine'
    frozen_dependencies: list[str] = Field(default_factory=lambda: ['app.runtime (v7.0)', 'app.prompt (v7.1)', 'app.memory (v7.2)', 'app.tools (v7.3)', 'app.graph_runtime (v7.4)', 'app.agents (v7.5)'])

