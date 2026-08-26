import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


class RuntimeContext(BaseModel):
    """Immutable execution runtime context container, maintaining state parity with Phase 6 Context objects."""

    runtime_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    provider: str
    model: str
    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    workflow_id: Optional[str] = None
    conversation_id: Optional[uuid.UUID] = None
    session_id: Optional[str] = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)
