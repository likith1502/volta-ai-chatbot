from pydantic import BaseModel, Field


class RAGConfig(BaseModel):
    """Global configuration for Enterprise RAG Engine."""

    default_chunk_size: int = Field(default=512, ge=64)
    default_chunk_overlap: int = Field(default=64, ge=0)
    default_top_k: int = Field(default=5, ge=1)
    default_embedding_provider: str = "mock-embedder-v1"
    default_reranker: str = "cosine"
