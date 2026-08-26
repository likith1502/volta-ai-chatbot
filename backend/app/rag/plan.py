import uuid
from typing import Any

from pydantic import BaseModel, Field


class RetrievalPlan(BaseModel):
    """Execution plan detailing retrieval strategy, top_k, reranker, and metadata filters."""

    plan_id: str = Field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:8]}")
    query: str
    strategy: str = "vector"
    top_k: int = Field(default=5, ge=1, le=50)
    reranker: str = "cosine"
    filters: dict[str, Any] = Field(default_factory=dict)
