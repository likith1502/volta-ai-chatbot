"""Consolidated Telemetry Module for Memory Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABC, abstractmethod
from app.memory.context import MemoryContext
from app.memory.contracts import MemoryRequest
from app.memory.memory import Memory
from pydantic import BaseModel, Field
from typing import Any
import json

# --- Consolidated from analytics.py ---
class MemoryAnalyticsReport(BaseModel):
    """Telemetry report analyzing retrieval frequency, top memory types, and cleanup counts."""
    total_creations: int = Field(default=0, ge=0)
    total_searches: int = Field(default=0, ge=0)
    total_context_assemblies: int = Field(default=0, ge=0)
    average_assembly_latency_ms: float = Field(default=0.0, ge=0.0)
    expired_memories_count: int = Field(default=0, ge=0)

class MemoryAnalyticsManager:
    """Aggregates memory runtime analytics telemetry."""

    def __init__(self) -> None:
        self.creations = 0
        self.searches = 0
        self.assemblies = 0
        self.total_assembly_ms = 0.0

    def record_creation() -> None:
        self.creations += 1

    def record_search() -> None:
        self.searches += 1

    def record_assembly(self, duration_ms: float) -> None:
        self.assemblies += 1
        self.total_assembly_ms += duration_ms

    def get_report(self) -> MemoryAnalyticsReport:
        avg_lat = self.total_assembly_ms / self.assemblies if self.assemblies > 0 else 0.0
        return MemoryAnalyticsReport(total_creations=self.creations, total_searches=self.searches, total_context_assemblies=self.assemblies, average_assembly_latency_ms=avg_lat)

# --- Consolidated from metrics.py ---
class MemoryMetrics(BaseModel):
    """Runtime execution metrics container for memory operations."""
    memory_count: int = Field(default=0, ge=0)
    hits: int = Field(default=0, ge=0)
    misses: int = Field(default=0, ge=0)
    cache_ratio: float = Field(default=1.0, ge=0.0, le=1.0)
    assembly_latency_ms: float = Field(default=0.0, ge=0.0)
    cleanup_count: int = Field(default=0, ge=0)

# --- Consolidated from statistics.py ---
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

# --- Consolidated from serializer.py ---
class MemorySerializer:
    """Serialization and export helpers formatting memory objects into JSON or Markdown."""

    @staticmethod
    def memory_to_json(memory: Memory) -> str:
        return memory.model_dump_json(indent=2)

    @staticmethod
    def context_to_markdown(context: MemoryContext) -> str:
        lines = [f'# Assembled Memory Context — {context.context_id}', f'- **Conversation ID**: `{context.conversation_id}`', f'- **Strategy Used**: `{context.strategy_used}`', f'- **Total Memories**: `{context.total_memories_count}` | **Token Estimate**: `{context.total_token_estimate}`', '', '## Content Preview', context.format_as_text()]
        return '\n'.join(lines)

# --- Consolidated from hooks.py ---
class BeforeCreateHook(ABC):

    @abstractmethod
    async def before_create(self, request: MemoryRequest) -> None:
        pass

class AfterCreateHook(ABC):

    @abstractmethod
    async def after_create(self, memory: Memory) -> None:
        pass

class BeforeSearchHook(ABC):

    @abstractmethod
    async def before_search(self, query: str) -> None:
        pass

class AfterSearchHook(ABC):

    @abstractmethod
    async def after_search(self, results: list[Memory]) -> None:
        pass

class BeforeCleanupHook(ABC):

    @abstractmethod
    async def before_cleanup(self) -> None:
        pass

class AfterCleanupHook(ABC):

    @abstractmethod
    async def after_cleanup(self, cleaned_count: int) -> None:
        pass

class BeforeContextBuildHook(ABC):

    @abstractmethod
    async def before_context_build(self) -> None:
        pass

class AfterContextBuildHook(ABC):

    @abstractmethod
    async def after_context_build(self, context: MemoryContext) -> None:
        pass

