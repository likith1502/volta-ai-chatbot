from pydantic import BaseModel, Field


class MemoryConfiguration(BaseModel):
    """Pydantic configuration settings for the Memory Runtime."""

    max_memories_per_conversation: int = Field(default=500, ge=10)
    default_importance: float = Field(default=0.5, ge=0.0, le=1.0)
    default_assembly_strategy: str = Field(default="hybrid", description="'recent', 'importance', 'hybrid', 'sliding_window'")
    cleanup_interval_seconds: int = Field(default=3600, ge=60)
    token_budget_limit: int = Field(default=4000, ge=100)
    enable_auto_compaction: bool = True
    enable_event_publishing: bool = True
