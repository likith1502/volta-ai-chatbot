import uuid
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.memory.memory import Memory
from app.memory.status import MemoryStatus
from app.memory.types import MemoryType


class MemoryRequest(BaseModel):
    """Payload for creating a new memory record."""

    content: str = Field(..., min_length=1)
    conversation_id: Optional[uuid.UUID] = None
    execution_id: Optional[uuid.UUID] = None
    memory_type: MemoryType = Field(default=MemoryType.SHORT_TERM)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    ttl_seconds: Optional[int] = Field(default=None, description="Optional Time-To-Live in seconds")
    tags: list[str] = Field(default_factory=list)
    custom_attributes: dict[str, Any] = Field(default_factory=dict)


class MemoryResponse(BaseModel):
    """Container for single memory operations."""

    memory: Memory
    message: str = "Memory operation successful"


class MemorySearchResult(BaseModel):
    """Structured container for memory search & retrieval operations."""

    matched_memories: list[Memory] = Field(default_factory=list)
    scores: list[float] = Field(default_factory=list)
    execution_time_ms: float = Field(default=0.0, ge=0.0)
    strategy_used: str = Field(default="hybrid")
    total_count: int = Field(default=0, ge=0)
    warnings: list[str] = Field(default_factory=list)
