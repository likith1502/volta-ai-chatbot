import uuid

from pydantic import BaseModel, Field


class DocumentVersion(BaseModel):
    """Tracks document version lineage and hash checksums."""

    version_id: str = Field(default_factory=lambda: f"ver_{uuid.uuid4().hex[:8]}")
    document_id: str
    version_number: int = Field(default=1, ge=1)
    checksum: str = Field(default="")
    created_at: float = Field(default_factory=lambda: 1786088000.0)
