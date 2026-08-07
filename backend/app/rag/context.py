from typing import Any
from pydantic import BaseModel, Field
from app.rag.citation import Citation


class RAGContext(BaseModel):
    """Assembled RAG context container ready for injection into PromptManager."""

    query: str
    context_text: str = Field(..., min_length=1)
    citations: list[Citation] = Field(default_factory=list)
    scores: list[float] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
