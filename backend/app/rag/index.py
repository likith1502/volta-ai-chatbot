import uuid
from pydantic import BaseModel, Field


class DocumentIndex(BaseModel):
    """Index container tracking indexed documents, total chunks, and vector dimension."""

    index_id: str = Field(default_factory=lambda: f"idx_{uuid.uuid4().hex[:8]}")
    name: str = "volta_knowledge_index"
    total_documents: int = Field(default=0, ge=0)
    total_chunks: int = Field(default=0, ge=0)
    total_vectors: int = Field(default=0, ge=0)
    dimension: int = 1536
    updated_at: float = Field(default_factory=lambda: 1786088000.0)
