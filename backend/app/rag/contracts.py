import uuid
from typing import Any, Optional
from pydantic import BaseModel, Field


class RAGDocumentPayload(BaseModel):
    title: str = Field(..., min_length=1)
    raw_text: str = Field(..., min_length=1)
    mime_type: str = "text/plain"
    metadata: dict[str, Any] = Field(default_factory=dict)


class RAGIngestPayload(BaseModel):
    document_id: str
    chunk_strategy: str = "fixed"
    chunk_size: int = 512
    chunk_overlap: int = 64


class RAGRetrievePayload(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)
    strategy: str = "vector"
    reranker: str = "cosine"
    filters: dict[str, Any] = Field(default_factory=dict)


class RAGQueryPayload(BaseModel):
    query: str = Field(..., min_length=1)
    conversation_id: Optional[uuid.UUID] = None
    top_k: int = Field(default=5, ge=1, le=50)


class RAGContextResponse(BaseModel):
    query: str
    context_text: str
    chunks_count: int
    citations_count: int
    latency_ms: float


class RAGResponse(BaseModel):
    success: bool = True
    data: dict[str, Any]
    message: str = "RAG operation completed"
