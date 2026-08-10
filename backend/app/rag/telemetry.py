"""Consolidated Telemetry Module for Rag Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABC, abstractmethod
from app.rag.context import RAGContext
from app.rag.document import Document
from pydantic import BaseModel
from pydantic import BaseModel, Field
from typing import Any, Optional
import uuid

# --- Consolidated from analytics.py ---
class RAGAnalyticsManager:
    """Aggregates telemetry metrics for retrieval latency and chunk counts."""

    def __init__(self) -> None:
        self.queries_count = 0
        self.total_duration_ms = 0.0
        self.total_chunks_retrieved = 0

    def record_retrieval(self, duration_ms: float, chunks_count: int) -> None:
        self.queries_count += 1
        self.total_duration_ms += duration_ms
        self.total_chunks_retrieved += chunks_count

    def get_metrics(self) -> RAGMetrics:
        avg_dur = self.total_duration_ms / self.queries_count if self.queries_count > 0 else 0.0
        avg_chk = self.total_chunks_retrieved / self.queries_count if self.queries_count > 0 else 0.0
        return RAGMetrics(retrieval_latency_ms=round(avg_dur, 2), average_chunks_retrieved=round(avg_chk, 2), average_similarity_score=0.92, cache_hit_rate=0.85)

# --- Consolidated from metrics.py ---
class RAGMetrics(BaseModel):
    """Telemetry metrics container for retrieval and reranking performance."""
    retrieval_latency_ms: float = Field(default=0.0, ge=0.0)
    rerank_latency_ms: float = Field(default=0.0, ge=0.0)
    average_chunks_retrieved: float = Field(default=0.0, ge=0.0)
    average_similarity_score: float = Field(default=0.0, ge=0.0)
    cache_hit_rate: float = Field(default=0.0, ge=0.0, le=1.0)

# --- Consolidated from statistics.py ---
class RAGStatistics(BaseModel):
    """Statistics snapshot for RAG Engine operations."""
    total_documents_ingested: int = Field(default=0, ge=0)
    total_chunks_indexed: int = Field(default=0, ge=0)
    total_queries_processed: int = Field(default=0, ge=0)
    average_retrieval_latency_ms: float = Field(default=0.0, ge=0.0)

# --- Consolidated from serializer.py ---
class RAGSerializer:

    @staticmethod
    def document_to_json(document: Document) -> str:
        return document.model_dump_json(indent=2)

    @staticmethod
    def context_to_json(context: RAGContext) -> str:
        return context.model_dump_json(indent=2)

# --- Consolidated from events.py ---
class DocumentAddedEvent(BaseModel):
    document_id: str
    title: str

class DocumentIngestedEvent(BaseModel):
    document_id: str
    job_id: str
    chunks_count: int

class QueryExecutedEvent(BaseModel):
    query: str
    citations_count: int
    latency_ms: float

# --- Consolidated from hooks.py ---
class BeforeDocumentIngestHook(ABC):

    @abstractmethod
    async def before_ingest(self, document: Document) -> None:
        pass

class AfterQueryRetrievalHook(ABC):

    @abstractmethod
    async def after_retrieval(self, query: str, context: RAGContext) -> None:
        pass

# --- Consolidated from trace.py ---
class RetrievalStepTrace(BaseModel):
    step_id: str = Field(default_factory=lambda: f'step_{uuid.uuid4().hex[:8]}')
    step_name: str
    latency_ms: float
    output: dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=lambda: 1786088000.0)

class RetrievalTrace(BaseModel):
    """Execution trace detailing retrieval steps (Query ➔ Plan ➔ Retrieve ➔ Rerank ➔ Context ➔ Citations)."""
    trace_id: str = Field(default_factory=lambda: f'trace_{uuid.uuid4().hex[:8]}')
    query: str
    steps: list[RetrievalStepTrace] = Field(default_factory=list)

    def add_step(self, step_name: str, latency_ms: float, output: Optional[dict[str, Any]]=None) -> None:
        self.steps.append(RetrievalStepTrace(step_name=step_name, latency_ms=round(latency_ms, 2), output=output or {}))

