from pydantic import BaseModel, Field


class RAGMetrics(BaseModel):
    """Telemetry metrics container for retrieval and reranking performance."""

    retrieval_latency_ms: float = Field(default=0.0, ge=0.0)
    rerank_latency_ms: float = Field(default=0.0, ge=0.0)
    average_chunks_retrieved: float = Field(default=0.0, ge=0.0)
    average_similarity_score: float = Field(default=0.0, ge=0.0)
    cache_hit_rate: float = Field(default=0.0, ge=0.0, le=1.0)
