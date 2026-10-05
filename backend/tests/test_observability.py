"""Phase 7.8 — Observability Package Tests."""

import pytest
from app.observability.metrics import PrometheusMetricsProvider, MetricPoint
from app.observability.logging import StructuredLoggingProvider, LogEntry
from app.observability.tracing import OpenTelemetryTracingProvider, Span
from app.observability.alerts import EmailAlertProvider, Alert, AlertSeverity
from app.observability.dashboard import GrafanaDashboardProvider, Dashboard
from app.observability.manager import ObservabilityManager


class TestPrometheusMetricsProvider:
    def test_record_counter(self):
        p = PrometheusMetricsProvider()
        p.record_counter("test_requests", 1.0, {"method": "GET"})
        metrics = p.get_all_metrics()
        assert len(metrics) == 1
        assert "counter_test_requests" in metrics[0].name

    def test_record_gauge(self):
        p = PrometheusMetricsProvider()
        p.record_gauge("cpu_utilization", 75.0)
        metrics = p.get_all_metrics()
        assert metrics[0].value == 75.0

    def test_record_histogram(self):
        p = PrometheusMetricsProvider()
        p.record_histogram("response_latency_ms", 150.0)
        metrics = p.get_all_metrics()
        assert "histogram" in metrics[0].name

    def test_exposition_format(self):
        p = PrometheusMetricsProvider()
        p.record_counter("test", 5.0, {"env": "prod"})
        exposition = p.to_exposition_format()
        assert "counter_test" in exposition

    def test_multiple_metrics(self):
        p = PrometheusMetricsProvider()
        p.record_counter("a", 1.0)
        p.record_counter("b", 2.0)
        p.record_gauge("c", 3.0)
        assert len(p.get_all_metrics()) == 3


class TestStructuredLoggingProvider:
    def test_log_info(self):
        p = StructuredLoggingProvider()
        p.info("Test message")
        assert len(p.get_entries()) == 1
        assert p.get_entries()[0].level == "INFO"

    def test_log_warning(self):
        p = StructuredLoggingProvider()
        p.warning("Warning message")
        assert p.get_entries()[0].level == "WARNING"

    def test_log_error(self):
        p = StructuredLoggingProvider()
        p.error("Error message")
        assert p.get_entries()[0].level == "ERROR"

    def test_log_with_kwargs(self):
        p = StructuredLoggingProvider()
        p.info("Deploy event", deployment_id="d1", strategy="rolling")
        entry = p.get_entries()[0]
        assert entry.labels.get("deployment_id") == "d1"

    def test_multiple_entries(self):
        p = StructuredLoggingProvider()
        p.info("msg1")
        p.info("msg2")
        p.warning("warn1")
        assert len(p.get_entries()) == 3


class TestOpenTelemetryTracingProvider:
    def test_start_span(self):
        p = OpenTelemetryTracingProvider()
        span = p.start_span("deploy_operation")
        assert span.operation == "deploy_operation"
        assert span.span_id is not None

    def test_finish_span(self):
        p = OpenTelemetryTracingProvider()
        span = p.start_span("test_op")
        p.finish_span(span, duration_ms=120.5)
        traces = p.get_traces()
        assert len(traces) == 1
        assert traces[0].duration_ms == 120.5

    def test_span_with_custom_trace_id(self):
        p = OpenTelemetryTracingProvider()
        span = p.start_span("op", trace_id="abc123")
        assert span.trace_id == "abc123"

    def test_multiple_spans(self):
        p = OpenTelemetryTracingProvider()
        for i in range(5):
            span = p.start_span(f"op_{i}")
            p.finish_span(span, duration_ms=float(i * 10))
        assert len(p.get_traces()) == 5


class TestEmailAlertProvider:
    @pytest.mark.asyncio
    async def test_fire_alert(self):
        p = EmailAlertProvider()
        alert = Alert(alert_id="a1", title="Test Alert", severity=AlertSeverity.WARNING, message="Test")
        result = await p.fire(alert)
        assert result is True
        assert len(p.get_active_alerts()) == 1

    @pytest.mark.asyncio
    async def test_resolve_alert(self):
        p = EmailAlertProvider()
        alert = Alert(alert_id="a2", title="Critical Alert", severity=AlertSeverity.CRITICAL, message="Down")
        await p.fire(alert)
        await p.resolve("a2")
        assert len(p.get_active_alerts()) == 0

    @pytest.mark.asyncio
    async def test_resolve_nonexistent_alert(self):
        p = EmailAlertProvider()
        result = await p.resolve("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_multiple_alerts(self):
        p = EmailAlertProvider()
        for i in range(3):
            await p.fire(Alert(
                alert_id=f"a{i}", title=f"Alert {i}",
                severity=AlertSeverity.INFO, message="Test"
            ))
        assert len(p.get_active_alerts()) == 3


class TestGrafanaDashboardProvider:
    def test_list_dashboards(self):
        p = GrafanaDashboardProvider()
        dashboards = p.list_dashboards()
        assert len(dashboards) == 3

    def test_get_dashboard_platform_health(self):
        p = GrafanaDashboardProvider()
        d = p.get_dashboard("platform_health")
        assert d is not None
        assert d.title == "VOLTA Platform Health"

    def test_get_dashboard_rag_performance(self):
        p = GrafanaDashboardProvider()
        d = p.get_dashboard("rag_performance")
        assert d is not None
        assert len(d.panels) > 0

    def test_get_nonexistent_dashboard(self):
        p = GrafanaDashboardProvider()
        assert p.get_dashboard("nonexistent") is None


class TestObservabilityManager:
    def test_initialization(self):
        om = ObservabilityManager()
        assert om.metrics is not None
        assert om.logging is not None
        assert om.tracing is not None
        assert om.alerts is not None
        assert om.dashboard is not None

    def test_record_deployment_event(self):
        om = ObservabilityManager()
        om.record_deployment_event("deploy", "d1")
        metrics = om.metrics.get_all_metrics()
        log_entries = om.logging.get_entries()
        assert len(metrics) >= 1
        assert len(log_entries) >= 1

    def test_record_health_check(self):
        om = ObservabilityManager()
        om.record_health_check("green")
        metrics = om.metrics.get_all_metrics()
        assert any("health_level" in m.name for m in metrics)

    @pytest.mark.asyncio
    async def test_fire_critical_alert(self):
        om = ObservabilityManager()
        result = await om.fire_critical_alert("Platform Down", "Redis unreachable")
        assert result is True
        assert len(om.get_active_alerts()) == 1

    def test_get_dashboards(self):
        om = ObservabilityManager()
        dashboards = om.get_dashboards()
        assert len(dashboards) == 3

    def test_get_metrics_exposition(self):
        om = ObservabilityManager()
        om.metrics.record_counter("test", 1.0)
        exposition = om.get_metrics_exposition()
        assert "counter_test" in exposition
