"""Consolidated Telemetry Module for Tools Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABC, abstractmethod
from app.tools.manifest import ToolManifest
from app.tools.request import ToolRequest
from app.tools.result import ToolResult
from pydantic import BaseModel, Field
import json

# --- Consolidated from analytics.py ---
class ToolAnalyticsReport(BaseModel):
    """Telemetry report analyzing tool execution frequency and latency."""
    total_executions: int = Field(default=0, ge=0)
    top_executed_tool: str = Field(default='none')
    success_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    average_latency_ms: float = Field(default=0.0, ge=0.0)

class ToolAnalyticsManager:
    """Aggregates tool execution telemetry."""

    def __init__(self) -> None:
        self.executions = 0
        self.successes = 0
        self.total_latency_ms = 0.0
        self.tool_counts: dict[str, int] = {}

    def record_execution(self, tool_name: str, success: bool, latency_ms: float) -> None:
        self.executions += 1
        if success:
            self.successes += 1
        self.total_latency_ms += latency_ms
        self.tool_counts[tool_name] = self.tool_counts.get(tool_name, 0) + 1

    def get_report(self) -> ToolAnalyticsReport:
        top_tool = max(self.tool_counts, key=self.tool_counts.get) if self.tool_counts else 'none'
        avg_lat = self.total_latency_ms / self.executions if self.executions > 0 else 0.0
        rate = self.successes / self.executions if self.executions > 0 else 1.0
        return ToolAnalyticsReport(total_executions=self.executions, top_executed_tool=top_tool, success_rate=round(rate, 4), average_latency_ms=round(avg_lat, 2))

# --- Consolidated from metrics.py ---
class ToolMetrics(BaseModel):
    """Runtime execution metrics container for tool operations."""
    total_tool_calls: int = Field(default=0, ge=0)
    successful_calls: int = Field(default=0, ge=0)
    failed_calls: int = Field(default=0, ge=0)
    timed_out_calls: int = Field(default=0, ge=0)
    average_latency_ms: float = Field(default=0.0, ge=0.0)

# --- Consolidated from statistics.py ---
class ToolStatistics(BaseModel):
    """Snapshot container recording current state statistics of the tool repository."""
    total_registered_tools: int = Field(default=0, ge=0)
    active_tools: int = Field(default=0, ge=0)
    deprecated_tools: int = Field(default=0, ge=0)
    disabled_tools: int = Field(default=0, ge=0)
    total_executions: int = Field(default=0, ge=0)
    average_execution_latency_ms: float = Field(default=0.0, ge=0.0)

# --- Consolidated from events.py ---
class ToolRegisteredEvent(BaseModel):
    tool_name: str
    version: str

class ToolValidatedEvent(BaseModel):
    tool_name: str
    is_valid: bool

class ToolStartedEvent(BaseModel):
    tool_name: str
    execution_id: str

class ToolCompletedEvent(BaseModel):
    tool_name: str
    execution_id: str
    duration_ms: float

class ToolFailedEvent(BaseModel):
    tool_name: str
    execution_id: str
    error: str

class ToolTimedOutEvent(BaseModel):
    tool_name: str
    execution_id: str
    timeout_seconds: float

class ToolSkippedEvent(BaseModel):
    tool_name: str
    reason: str

class ToolCancelledEvent(BaseModel):
    tool_name: str
    reason: str

# --- Consolidated from hooks.py ---
class BeforeToolExecutionHook(ABC):

    @abstractmethod
    async def before_execution(self, request: ToolRequest) -> None:
        pass

class AfterToolExecutionHook(ABC):

    @abstractmethod
    async def after_execution(self, result: ToolResult) -> None:
        pass

# --- Consolidated from serializer.py ---
class ToolSerializer:
    """Serialization helpers for tool results and manifests."""

    @staticmethod
    def result_to_json(result: ToolResult) -> str:
        return result.model_dump_json(indent=2)

    @staticmethod
    def manifest_to_json(manifest: ToolManifest) -> str:
        return manifest.model_dump_json(indent=2)

