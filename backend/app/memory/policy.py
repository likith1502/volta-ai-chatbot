from pydantic import BaseModel, Field


class MemoryPolicy(BaseModel):
    """Retention, expiration, and cleanup policy for Memory Runtime."""

    retention_days: int = Field(default=30, ge=1)
    auto_archive_expired: bool = True
    auto_delete_archived_days: int = Field(default=90, ge=1)
    max_active_memories_per_conversation: int = Field(default=100, ge=5)
    default_importance_threshold: float = Field(default=0.2, ge=0.0, le=1.0)
    pinning_bypasses_expiration: bool = True
