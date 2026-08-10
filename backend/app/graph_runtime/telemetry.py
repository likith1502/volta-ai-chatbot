"""Consolidated Telemetry Module for Graph_Runtime Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABC, abstractmethod
from app.graph_runtime.context import GraphRuntimeContext
from app.graph_runtime.execution_plan import GraphExecutionPlan
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Any, Optional
import uuid

if TYPE_CHECKING:
    from app.graph_runtime.execution_result import GraphExecutionResult


# --- Consolidated from analytics.py ---
class GraphRuntimeAnalyticsReport(BaseModel):
    """Telemetry report analyzing workflow execution frequency and node statistics."""
    total_graph_executions: int = Field(default=0, ge=0)
    most_visited_node: str = Field(default='llm_node')
    success_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    average_duration_ms: float = Field(default=0.0, ge=0.0)

class GraphRuntimeAnalyticsManager:
    """Aggregates telemetry and performance metrics for Graph Runtime."""

    def __init__(self) -> None:
        self.executions = 0
        self.successes = 0
        self.total_duration_ms = 0.0
        self.node_counts: dict[str, int] = {}

    def record_run(self, duration_ms: float, success: bool, visited_nodes: list[str]) -> None:
        self.executions += 1
        if success:
            self.successes += 1
        self.total_duration_ms += duration_ms
        for n in visited_nodes:
            self.node_counts[n] = self.node_counts.get(n, 0) + 1

    def get_report(self) -> GraphRuntimeAnalyticsReport:
        top_node = max(self.node_counts, key=self.node_counts.get) if self.node_counts else 'llm_node'
        avg_dur = self.total_duration_ms / self.executions if self.executions > 0 else 0.0
        rate = self.successes / self.executions if self.executions > 0 else 1.0
        return GraphRuntimeAnalyticsReport(total_graph_executions=self.executions, most_visited_node=top_node, success_rate=round(rate, 4), average_duration_ms=round(avg_dur, 2))

# --- Consolidated from metrics.py ---
class GraphRuntimeMetrics(BaseModel):
    """Runtime execution metrics container."""
    total_runs: int = Field(default=0, ge=0)
    active_sessions: int = Field(default=0, ge=0)
    paused_sessions: int = Field(default=0, ge=0)
    average_node_latency_ms: float = Field(default=0.0, ge=0.0)

# --- Consolidated from statistics.py ---
class GraphRuntimeStatistics(BaseModel):
    """Snapshot statistics of Graph Runtime operations."""
    total_executions: int = Field(default=0, ge=0)
    successful_executions: int = Field(default=0, ge=0)
    failed_executions: int = Field(default=0, ge=0)
    interrupted_executions: int = Field(default=0, ge=0)
    average_latency_ms: float = Field(default=0.0, ge=0.0)
    total_checkpoints_created: int = Field(default=0, ge=0)

# --- Consolidated from events.py ---
class GraphExecutionStartedEvent(BaseModel):
    execution_id: str
    workflow_id: str

class GraphNodeStartedEvent(BaseModel):
    execution_id: str
    node_id: str

class GraphNodeCompletedEvent(BaseModel):
    execution_id: str
    node_id: str
    latency_ms: float

class GraphExecutionCompletedEvent(BaseModel):
    execution_id: str
    workflow_id: str
    duration_ms: float

class GraphExecutionInterruptedEvent(BaseModel):
    execution_id: str
    node_id: str
    reason: str

# --- Consolidated from hooks.py ---
class BeforeGraphExecutionHook(ABC):

    @abstractmethod
    async def before_execution(self, context: GraphRuntimeContext) -> None:
        pass

class AfterGraphExecutionHook(ABC):

    @abstractmethod
    async def after_execution(self, result: GraphExecutionResult) -> None:
        pass

# --- Consolidated from serializer.py ---
class GraphRuntimeSerializer:
    """Serializes Graph Execution plans and results into JSON strings."""

    @staticmethod
    def result_to_json(result: GraphExecutionResult) -> str:
        return result.model_dump_json(indent=2)

    @staticmethod
    def plan_to_json(plan: GraphExecutionPlan) -> str:
        return plan.model_dump_json(indent=2)

# --- Consolidated from trace.py ---
class TraceStep(BaseModel):
    """Single step recorded in an ExecutionTrace."""
    step_index: int
    node_id: str
    action: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: float = 0.0
    payload: dict[str, Any] = Field(default_factory=dict)

class ExecutionTrace(BaseModel):
    """Execution trace recorder tracking step-by-step events for single execution debugging."""
    trace_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    workflow_id: str
    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    steps: list[TraceStep] = Field(default_factory=list)

    def add_step(self, node_id: str, action: str, latency_ms: float, payload: Optional[dict]=None) -> None:
        idx = len(self.steps) + 1
        self.steps.append(TraceStep(step_index=idx, node_id=node_id, action=action, latency_ms=round(latency_ms, 2), payload=payload or {}))

