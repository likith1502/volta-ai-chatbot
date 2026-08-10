"""Consolidated Telemetry Module for Agents Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABC, abstractmethod
from app.agents.agent import Agent
from app.agents.manifest import AgentManifest
from app.agents.role import AgentRole
from app.agents.task import AgentTask, TaskResult
from app.agents.task import TaskResult
from pydantic import BaseModel, Field
from typing import Any, Optional
import time
import uuid

# --- Consolidated from analytics.py ---
class AgentAnalyticsReport(BaseModel):
    total_task_executions: int = Field(default=0, ge=0)
    success_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    average_duration_ms: float = Field(default=0.0, ge=0.0)
    most_active_role: str = 'support'

class AgentAnalyticsManager:
    """Aggregates multi-agent telemetry and performance analytics."""

    def __init__(self) -> None:
        self.executions = 0
        self.successes = 0
        self.total_duration_ms = 0.0
        self.role_counts: dict[str, int] = {}

    def record_task_execution(self, duration_ms: float, success: bool, role: AgentRole) -> None:
        self.executions += 1
        if success:
            self.successes += 1
        self.total_duration_ms += duration_ms
        r_str = str(role)
        self.role_counts[r_str] = self.role_counts.get(r_str, 0) + 1

    def get_report(self) -> AgentAnalyticsReport:
        top_role = max(self.role_counts, key=self.role_counts.get) if self.role_counts else 'support'
        avg_dur = self.total_duration_ms / self.executions if self.executions > 0 else 0.0
        rate = self.successes / self.executions if self.executions > 0 else 1.0
        return AgentAnalyticsReport(total_task_executions=self.executions, success_rate=round(rate, 4), average_duration_ms=round(avg_dur, 2), most_active_role=top_role)

# --- Consolidated from metrics.py ---
class AgentMetrics(BaseModel):
    total_agents: int = Field(default=0, ge=0)
    active_workers: int = Field(default=0, ge=0)
    pending_tasks: int = Field(default=0, ge=0)
    average_latency_ms: float = Field(default=0.0, ge=0.0)

# --- Consolidated from statistics.py ---
class AgentStatistics(BaseModel):
    total_registered_agents: int = Field(default=0, ge=0)
    total_tasks_executed: int = Field(default=0, ge=0)
    total_delegations: int = Field(default=0, ge=0)
    total_messages_sent: int = Field(default=0, ge=0)
    active_workers_count: int = Field(default=0, ge=0)
    average_task_latency_ms: float = Field(default=0.0, ge=0.0)

# --- Consolidated from events.py ---
class AgentRegisteredEvent(BaseModel):
    agent_id: str
    name: str
    role: str

class AgentStartedEvent(BaseModel):
    agent_id: str
    task_id: str

class AgentDelegatedEvent(BaseModel):
    delegator_id: str
    delegatee_id: str
    task_id: str
    depth: int

class AgentTaskCompletedEvent(BaseModel):
    agent_id: str
    task_id: str
    latency_ms: float

# --- Consolidated from hooks.py ---
class BeforeAgentExecutionHook(ABC):

    @abstractmethod
    async def before_execution(self, agent: Agent, task: AgentTask) -> None:
        pass

class AfterAgentExecutionHook(ABC):

    @abstractmethod
    async def after_execution(self, agent: Agent, result: TaskResult) -> None:
        pass

# --- Consolidated from serializer.py ---
class AgentSerializer:

    @staticmethod
    def manifest_to_json(manifest: AgentManifest) -> str:
        return manifest.model_dump_json(indent=2)

    @staticmethod
    def task_result_to_json(result: TaskResult) -> str:
        return result.model_dump_json(indent=2)

# --- Consolidated from trace.py ---
class AgentTraceStep(BaseModel):
    step_id: str = Field(default_factory=lambda: f'step_{uuid.uuid4().hex[:8]}')
    agent_id: str
    action: str
    latency_ms: float
    output: dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=lambda: 1786088000.0)

class AgentTrace(BaseModel):
    trace_id: str = Field(default_factory=lambda: f'trace_{uuid.uuid4().hex[:8]}')
    steps: list[AgentTraceStep] = Field(default_factory=list)

    def add_step(self, agent_id: str, action: str, latency_ms: float, output: Optional[dict[str, Any]]=None) -> None:
        self.steps.append(AgentTraceStep(agent_id=agent_id, action=action, latency_ms=round(latency_ms, 2), output=output or {}))

