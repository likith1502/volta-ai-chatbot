import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from app.memory.memory import Memory


class MemorySnapshot(BaseModel):
    """Immutable audit snapshot recording memory state for checkpointing and replay."""

    snapshot_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    conversation_id: uuid.UUID
    memories: list[Memory] = Field(default_factory=list)
    total_count: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
