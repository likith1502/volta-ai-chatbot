import uuid

from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Structured audit reference citation pointing to source document, page, and chunk."""

    citation_id: str = Field(default_factory=lambda: f"cit_{uuid.uuid4().hex[:8]}")
    document_id: str
    document_title: str
    page_number: int = Field(default=1, ge=1)
    chunk_id: str
    snippet: str = Field(default="")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    source_uri: str = Field(default="")
