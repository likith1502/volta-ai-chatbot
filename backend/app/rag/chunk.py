import uuid
from typing import Any, Optional
from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """Un-embedded text chunk extracted from a document."""

    chunk_id: str = Field(default_factory=lambda: f"chk_{uuid.uuid4().hex[:8]}")
    document_id: str
    page_number: int = Field(default=1, ge=1)
    text: str = Field(..., min_length=1)
    token_count: int = Field(default=0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EmbeddedChunk(BaseModel):
    """Vector embedding binding for a text Chunk."""

    embedded_chunk_id: str = Field(default_factory=lambda: f"emb_chk_{uuid.uuid4().hex[:8]}")
    chunk_id: str
    document_id: str
    vector: list[float] = Field(default_factory=list)
    provider_id: str = "mock"
    dimension: int = Field(default=1536, ge=1)
    created_at: float = Field(default_factory=lambda: 1786088000.0)
