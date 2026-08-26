import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.rag.lifecycle import DocumentLifecycleManager, DocumentLifecycleState
from app.rag.source import DocumentSourceLocator


class Document(BaseModel):
    """Core domain model representing an ingested knowledge document."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    document_id: str = Field(default_factory=lambda: f"doc_{uuid.uuid4().hex[:8]}")
    title: str = Field(..., min_length=1)
    raw_text: str = Field(default="")
    mime_type: str = "text/plain"
    source: DocumentSourceLocator = Field(default_factory=DocumentSourceLocator)
    metadata: dict[str, Any] = Field(default_factory=dict)
    checksum: str = Field(default="")
    version: int = Field(default=1, ge=1)
    lifecycle: DocumentLifecycleManager = Field(
        default_factory=DocumentLifecycleManager
    )
    created_at: float = Field(default_factory=lambda: 1786088000.0)

    @property
    def status(self) -> DocumentLifecycleState:
        return self.lifecycle.current_state

    def transition_status(self, target: DocumentLifecycleState) -> bool:
        return self.lifecycle.transition_to(target)
