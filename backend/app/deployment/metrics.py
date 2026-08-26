"""Deployment metrics collector."""

from app.deployment.statistics import DeploymentMetrics


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
