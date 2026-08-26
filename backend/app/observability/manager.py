"""Observability Manager — central orchestrator for metrics, logging, tracing, alerting."""

from __future__ import annotations

import uuid

from app.observability.alerts import (
    Alert,
    AlertProvider,
    AlertSeverity,
    EmailAlertProvider,
)
from app.observability.dashboard import (
    Dashboard,
    DashboardProvider,
    GrafanaDashboardProvider,
)
from app.observability.logging import LoggingProvider, StructuredLoggingProvider
from app.observability.metrics import MetricsProvider, PrometheusMetricsProvider
from app.observability.tracing import OpenTelemetryTracingProvider, TracingProvider


class ObservabilityManager:
    """Central orchestrator for platform observability."""

    def __init__(
        self,
        metrics: MetricsProvider | None = None,
        logging: LoggingProvider | None = None,
        tracing: TracingProvider | None = None,
        alerts: AlertProvider | None = None,
        dashboard: DashboardProvider | None = None,
    ) -> None:
        self.metrics = metrics or PrometheusMetricsProvider()
        self.logging = logging or StructuredLoggingProvider()
        self.tracing = tracing or OpenTelemetryTracingProvider()
        self.alerts = alerts or EmailAlertProvider()
        self.dashboard = dashboard or GrafanaDashboardProvider()

    def record_deployment_event(self, event_type: str, deployment_id: str) -> None:
        self.metrics.record_counter(
            "deployment_events_total",
            labels={"event": event_type, "deployment_id": deployment_id},
        )
        self.logging.info(
            f"Deployment event: {event_type}", deployment_id=deployment_id
        )

    def record_health_check(self, health_level: str) -> None:
        value = {"green": 0, "yellow": 1, "orange": 2, "red": 3}.get(
            health_level.lower(), 0
        )
        self.metrics.record_gauge("platform_health_level", value)

    async def fire_critical_alert(
        self, title: str, message: str, service: str = "volta-platform"
    ) -> bool:
        alert = Alert(
            alert_id=uuid.uuid4().hex[:8],
            title=title,
            severity=AlertSeverity.CRITICAL,
            message=message,
            service=service,
        )
        return await self.alerts.fire(alert)

    def get_active_alerts(self) -> list[Alert]:
        return self.alerts.get_active_alerts()

    def get_dashboards(self) -> list[Dashboard]:
        return self.dashboard.list_dashboards()

    def get_metrics_exposition(self) -> str:
        if hasattr(self.metrics, "to_exposition_format"):
            return self.metrics.to_exposition_format()
        return ""
