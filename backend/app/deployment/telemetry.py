"""Consolidated Telemetry Module for Deployment Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from dataclasses import asdict, is_dataclass
from dataclasses import dataclass
from dataclasses import dataclass, field
from typing import Any
from typing import Any, Callable, Awaitable
import json

# --- Consolidated from analytics.py ---
class DeploymentAnalyticsEngine:

    def __init__(self) -> None:
        self._analytics = DeploymentAnalytics()

    def compute(self, total_deployments: int, failed_deployments: int, rollbacks: int, lead_time_hours: float=2.0) -> DeploymentAnalytics:
        if total_deployments > 0:
            self._analytics.change_failure_rate_pct = failed_deployments / total_deployments * 100
            self._analytics.rollback_rate_pct = rollbacks / total_deployments * 100
        self._analytics.lead_time_for_changes_hours = lead_time_hours
        return self._analytics

    @property
    def analytics(self) -> DeploymentAnalytics:
        return self._analytics

# --- Consolidated from metrics.py ---
class DeploymentMetricsCollector:

    def __init__(self) -> None:
        self._metrics = DeploymentMetrics()

    def record_latency(self, latency_ms: float) -> None:
        self._metrics.p95_latency_ms = max(self._metrics.p95_latency_ms, latency_ms)

    def record_cpu(self, pct: float) -> None:
        self._metrics.cpu_utilization_pct = pct

    def record_memory(self, pct: float) -> None:
        self._metrics.memory_utilization_pct = pct

    @property
    def metrics(self) -> DeploymentMetrics:
        return self._metrics

# --- Consolidated from statistics.py ---
@dataclass
class DeploymentStatistics:
    total_deployments: int = 0
    successful_deployments: int = 0
    failed_deployments: int = 0
    rollbacks_triggered: int = 0
    scaling_events: int = 0
    backups_completed: int = 0
    recovery_tests_run: int = 0
    validations_run: int = 0
    validations_passed: int = 0

@dataclass
class DeploymentMetrics:
    avg_deployment_duration_seconds: float = 0.0
    avg_validation_duration_seconds: float = 0.0
    p95_latency_ms: float = 0.0
    cpu_utilization_pct: float = 0.0
    memory_utilization_pct: float = 0.0
    error_rate_pct: float = 0.0

@dataclass
class DeploymentAnalytics:
    deployment_frequency_per_day: float = 0.0
    rollback_rate_pct: float = 0.0
    mean_time_to_recovery_minutes: float = 0.0
    mean_time_between_failures_hours: float = 0.0
    change_failure_rate_pct: float = 0.0
    lead_time_for_changes_hours: float = 0.0

# --- Consolidated from events.py ---
@dataclass
class DeploymentEvent:
    event_type: str
    deployment_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = 1786088000.0

class DeploymentEventBus:

    def __init__(self) -> None:
        self._events: list[DeploymentEvent] = []

    def emit(self, event: DeploymentEvent) -> None:
        self._events.append(event)

    def get_events(self, deployment_id: str | None=None) -> list[DeploymentEvent]:
        if deployment_id:
            return [e for e in self._events if e.deployment_id == deployment_id]
        return list(self._events)

# --- Consolidated from hooks.py ---
@dataclass
class DeploymentHookResult:
    hook_name: str
    passed: bool
    message: str = ''

class DeploymentHooks:
    """Registry for pre/post deployment lifecycle hooks."""

    def __init__(self) -> None:
        self._hooks: dict[str, list[Callable[..., Awaitable[bool]]]] = {}

    def register(self, event: str, fn: Callable[..., Awaitable[bool]]) -> None:
        self._hooks.setdefault(event, []).append(fn)

    async def run(self, event: str, context: dict[str, Any] | None=None) -> list[DeploymentHookResult]:
        results: list[DeploymentHookResult] = []
        for fn in self._hooks.get(event, []):
            try:
                passed = await fn(context or {})
                results.append(DeploymentHookResult(hook_name=fn.__name__, passed=passed))
            except Exception as exc:
                results.append(DeploymentHookResult(hook_name=fn.__name__, passed=False, message=str(exc)))
        return results

# --- Consolidated from serializer.py ---
class DeploymentSerializer:

    @staticmethod
    def to_dict(obj: Any) -> dict[str, Any]:
        if is_dataclass(obj):
            return asdict(obj)
        if hasattr(obj, 'model_dump'):
            return obj.model_dump()
        return dict(obj)

    @staticmethod
    def to_json(obj: Any) -> str:
        return json.dumps(DeploymentSerializer.to_dict(obj), default=str)

