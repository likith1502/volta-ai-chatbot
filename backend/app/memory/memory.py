import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.memory.metadata import MemoryMetadata
from app.memory.status import MemoryStatus
from app.memory.types import MemoryType


class Memory(BaseModel):
    """Primary domain model representing an immutable conversation memory record."""

    memory_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    conversation_id: Optional[uuid.UUID] = None
    execution_id: Optional[uuid.UUID] = None
    memory_type: MemoryType = Field(default=MemoryType.SHORT_TERM)
    status: MemoryStatus = Field(default=MemoryStatus.ACTIVE)
    content: str = Field(..., min_length=1, description="Memory text payload")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance score [0.0 - 1.0]")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    metadata: MemoryMetadata = Field(default_factory=MemoryMetadata)

    @property
    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_pinned(self) -> bool:
        return self.status == MemoryStatus.PINNED
