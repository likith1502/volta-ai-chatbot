from typing import Any
from pydantic import BaseModel, Field


class RetrievalExplanation(BaseModel):
    """Detailed audit explanation of why specific chunks were selected and reranked."""

    query: str
    selected_chunk_ids: list[str] = Field(default_factory=list)
    reranker: str = "Cosine"
    reason: str = "Top-K cosine similarity search"
    average_score: float = Field(default=0.92, ge=0.0, le=1.0)
    details: dict[str, Any] = Field(default_factory=dict)
