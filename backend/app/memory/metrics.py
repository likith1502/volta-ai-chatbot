from pydantic import BaseModel, Field


class MemoryMetrics(BaseModel):
    """Runtime execution metrics container for memory operations."""

    memory_count: int = Field(default=0, ge=0)
    hits: int = Field(default=0, ge=0)
    misses: int = Field(default=0, ge=0)
    cache_ratio: float = Field(default=1.0, ge=0.0, le=1.0)
    assembly_latency_ms: float = Field(default=0.0, ge=0.0)
    cleanup_count: int = Field(default=0, ge=0)
