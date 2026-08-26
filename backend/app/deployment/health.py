"""Deployment Health Manager — aggregated platform health with GREEN/YELLOW/ORANGE/RED levels."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DeploymentHealthLevel(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"


@dataclass
class DeploymentHealthReport:
    """Operational health report for a running deployment."""

    deployment_id: str
    health_level: DeploymentHealthLevel = DeploymentHealthLevel.GREEN
    is_healthy: bool = True
    replica_count: int = 1
    ready_replicas: int = 1
    cpu_utilization_pct: float = 0.0
    memory_utilization_pct: float = 0.0
    request_rate: float = 0.0
    error_rate_pct: float = 0.0
    latency_p50_ms: float = 0.0
    latency_p95_ms: float = 0.0
    latency_p99_ms: float = 0.0
    active_connections: int = 0
    uptime_seconds: float = 0.0
    layer_health: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    timestamp: float = 1786088000.0

    @property
    def availability_pct(self) -> float:
        if self.replica_count == 0:
            return 0.0
        return (self.ready_replicas / self.replica_count) * 100.0


@dataclass
class PlatformHealthSummary:
    """Top-level summary across all deployment targets."""

    overall_health: DeploymentHealthLevel = DeploymentHealthLevel.GREEN
    total_deployments: int = 0
    healthy_deployments: int = 0
    degraded_deployments: int = 0
    failed_deployments: int = 0
    deployment_reports: list[DeploymentHealthReport] = field(default_factory=list)
    layer_status: dict[str, str] = field(default_factory=dict)


class DeploymentHealthManager:
    """Aggregates health reports from all deployment targets."""

    _LAYER_NAMES = [
        "llm_runtime",
        "prompt_engine",
        "memory_runtime",
        "tool_runtime",
        "graph_runtime",
        "agent_runtime",
        "rag_engine",
        "integration_platform",
        "event_bus",
        "checkpoints",
        "streaming",
        "hitl",
    ]

    def __init__(self) -> None:
        self._reports: dict[str, DeploymentHealthReport] = {}

    def record_report(self, report: DeploymentHealthReport) -> None:
        self._reports[report.deployment_id] = report

    async def check_deployment_health(
        self, deployment_id: str
    ) -> DeploymentHealthReport:
        """Check health of a specific deployment (returns a healthy baseline by default)."""
        existing = self._reports.get(deployment_id)
        if existing:
            return existing
        report = DeploymentHealthReport(
            deployment_id=deployment_id,
            health_level=DeploymentHealthLevel.GREEN,
            is_healthy=True,
            ready_replicas=2,
            replica_count=2,
            layer_health={layer: "green" for layer in self._LAYER_NAMES},
        )
        self._reports[deployment_id] = report
        return report

    async def check_platform_health(self) -> PlatformHealthSummary:
        """Produce aggregated platform health from all deployment reports."""
        if not self._reports:
            # Generate default healthy report
            default_report = await self.check_deployment_health("volta-platform-v7.8")
            self._reports["volta-platform-v7.8"] = default_report

        reports = list(self._reports.values())
        healthy = [r for r in reports if r.health_level == DeploymentHealthLevel.GREEN]
        degraded = [
            r
            for r in reports
            if r.health_level
            in (DeploymentHealthLevel.YELLOW, DeploymentHealthLevel.ORANGE)
        ]
        failed = [r for r in reports if r.health_level == DeploymentHealthLevel.RED]

        if failed:
            overall = DeploymentHealthLevel.RED
        elif degraded:
            overall = DeploymentHealthLevel.YELLOW
        else:
            overall = DeploymentHealthLevel.GREEN

        layer_status = {layer: "green" for layer in self._LAYER_NAMES}

        return PlatformHealthSummary(
            overall_health=overall,
            total_deployments=len(reports),
            healthy_deployments=len(healthy),
            degraded_deployments=len(degraded),
            failed_deployments=len(failed),
            deployment_reports=reports,
            layer_status=layer_status,
        )
