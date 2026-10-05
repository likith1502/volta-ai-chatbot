"""Consolidated Models Module for Memory Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel
from pydantic import BaseModel, Field
from typing import Any, Optional

# --- Consolidated from status.py ---
class MemoryStatus(str, Enum):
    """Lifecycle status states for memory entries."""
    ACTIVE = 'active'
    ARCHIVED = 'archived'
    EXPIRED = 'expired'
    DELETED = 'deleted'
    PINNED = 'pinned'

# --- Consolidated from types.py ---
class MemoryType(str, Enum):
    """Categorical classification types for conversational memory elements."""
    SHORT_TERM = 'short_term'
    LONG_TERM = 'long_term'
    WORKING = 'working'
    SYSTEM = 'system'
    USER = 'user'
    SESSION = 'session'
    EPISODIC = 'episodic'
    SEMANTIC = 'semantic'
    CUSTOM = 'custom'

# --- Consolidated from metadata.py ---
class MemoryMetadata(BaseModel):
    """Metadata container for memory elements."""
    version: str = '1.0.0'
    schema_version: str = 'v1'
    tags: list[str] = Field(default_factory=list)
    priority: int = Field(default=1, ge=1, le=10)
    creator: str = 'system'
    access_count: int = Field(default=0, ge=0)
    last_accessed_at: Optional[datetime] = None
    custom_attributes: dict[str, Any] = Field(default_factory=dict)

# --- Consolidated from capabilities.py ---
class MemoryStorageCapabilities(BaseModel):
    """Storage capabilities flags defining supported repository capabilities."""
    supports_embeddings: bool = False
    supports_search: bool = True
    supports_metadata: bool = True
    supports_filters: bool = True
    supports_hybrid: bool = True
    supports_ttl: bool = True
    supports_pinning: bool = True

# --- Consolidated from config.py ---
class MemoryConfiguration(BaseModel):
    """Pydantic configuration settings for the Memory Runtime."""
    max_memories_per_conversation: int = Field(default=500, ge=10)
    default_importance: float = Field(default=0.5, ge=0.0, le=1.0)
    default_assembly_strategy: str = Field(default='hybrid', description="'recent', 'importance', 'hybrid', 'sliding_window'")
    cleanup_interval_seconds: int = Field(default=3600, ge=60)
    token_budget_limit: int = Field(default=4000, ge=100)
    enable_auto_compaction: bool = True
    enable_event_publishing: bool = True

# --- Consolidated from context_window.py ---
class ContextWindowBudget(BaseModel):
    """Tracks token budget allocations for runtime model context windows."""
    max_model_tokens: int = Field(default=128000, description='Total token limit of the target model')
    reserved_system_tokens: int = Field(default=2000, ge=0)
    reserved_completion_tokens: int = Field(default=1000, ge=0)
    memory_token_budget: int = Field(default=4000, ge=100)
    current_memory_tokens: int = Field(default=0, ge=0)

    @property
    def available_prompt_tokens(self) -> int:
        return max(0, self.max_model_tokens - self.reserved_system_tokens - self.reserved_completion_tokens - self.current_memory_tokens)

    @property
    def is_over_budget(self) -> bool:
        return self.current_memory_tokens > self.memory_token_budget

# --- Consolidated from policy.py ---
class MemoryPolicy(BaseModel):
    """Retention, expiration, and cleanup policy for Memory Runtime."""
    retention_days: int = Field(default=30, ge=1)
    auto_archive_expired: bool = True
    auto_delete_archived_days: int = Field(default=90, ge=1)
    max_active_memories_per_conversation: int = Field(default=100, ge=5)
    default_importance_threshold: float = Field(default=0.2, ge=0.0, le=1.0)
    pinning_bypasses_expiration: bool = True

# --- Consolidated from versioning.py ---
class MemoryVersion(BaseModel):
    """Version tracking model for memory schema and runtime releases."""
    memory_version: str = '7.2.0'
    schema_version: str = 'v1'
    serializer_version: str = '1.0.0'

