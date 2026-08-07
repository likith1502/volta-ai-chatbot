from pydantic import BaseModel, Field


class RetrievalBudget(BaseModel):
    """Resource limits and budgeting constraints for RAG retrieval & context assembly."""

    max_chunks: int = Field(default=10, ge=1)
    max_documents: int = Field(default=5, ge=1)
    max_context_tokens: int = Field(default=4096, ge=1)
    max_total_tokens: int = Field(default=8192, ge=1)
    max_citations: int = Field(default=10, ge=1)
