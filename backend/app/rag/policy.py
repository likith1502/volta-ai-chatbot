from pydantic import BaseModel, Field
from app.rag.budget import RetrievalBudget


class RAGPolicy(BaseModel):
    """RAG execution policy binding retrieval budget and strict filters."""

    budget: RetrievalBudget = Field(default_factory=RetrievalBudget)
    strict_provenance: bool = True
