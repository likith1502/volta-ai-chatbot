from pydantic import BaseModel, Field


class RAGStatistics(BaseModel):
    """Statistics snapshot for RAG Engine operations."""

    total_documents_ingested: int = Field(default=0, ge=0)
    total_chunks_indexed: int = Field(default=0, ge=0)
    total_queries_processed: int = Field(default=0, ge=0)
    average_retrieval_latency_ms: float = Field(default=0.0, ge=0.0)
