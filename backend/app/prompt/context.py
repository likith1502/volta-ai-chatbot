import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


class PromptContext(BaseModel):
    """Immutable execution context container tracking prompt rendering lineage."""

    prompt_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    template_id: str
    revision_id: str = "v1"
    conversation_id: Optional[uuid.UUID] = None
    execution_id: Optional[uuid.UUID] = None
    runtime_id: Optional[uuid.UUID] = None
    workflow_id: Optional[str] = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)
