from pydantic import BaseModel, Field


class MemoryStatistics(BaseModel):
    """Snapshot container recording current state statistics of the memory repository."""

    total_memories: int = Field(default=0, ge=0)
    active_memories: int = Field(default=0, ge=0)
    pinned_memories: int = Field(default=0, ge=0)
    archived_memories: int = Field(default=0, ge=0)
    expired_memories: int = Field(default=0, ge=0)
    average_importance: float = Field(default=0.0, ge=0.0, le=1.0)
    average_age_seconds: float = Field(default=0.0, ge=0.0)
    memory_usage_bytes: int = Field(default=0, ge=0)
    total_token_usage: int = Field(default=0, ge=0)
