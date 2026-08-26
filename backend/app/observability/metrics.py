"""Metrics provider — abstract and Prometheus reference implementation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class MetricPoint:
    name: str
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: float = 1786088000.0


class MetricsProvider(ABC):
    """Abstract metrics provider."""

    @abstractmethod
    def record_counter(
        self, name: str, value: float = 1.0, labels: dict[str, str] | None = None
    ) -> None: ...

    @abstractmethod
    def record_gauge(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None: ...

    @abstractmethod
    def record_histogram(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None: ...

    @abstractmethod
    def get_all_metrics(self) -> list[MetricPoint]: ...


class PrometheusMetricsProvider(MetricsProvider):
    """Reference Prometheus metrics provider (in-memory, no external SDK required)."""

    provider_id = "metrics.prometheus"
    name = "Prometheus Metrics Provider"

    def __init__(self) -> None:
        self._metrics: list[MetricPoint] = []

    def record_counter(
        self, name: str, value: float = 1.0, labels: dict[str, str] | None = None
    ) -> None:
        self._metrics.append(
            MetricPoint(name=f"counter_{name}", value=value, labels=labels or {})
        )

    def record_gauge(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None:
        self._metrics.append(
            MetricPoint(name=f"gauge_{name}", value=value, labels=labels or {})
        )

    def record_histogram(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None:
        self._metrics.append(
            MetricPoint(name=f"histogram_{name}", value=value, labels=labels or {})
        )

    def get_all_metrics(self) -> list[MetricPoint]:
        return list(self._metrics)

    def to_exposition_format(self) -> str:
        lines = []
        for m in self._metrics:
            label_str = ",".join(f'{k}="{v}"' for k, v in m.labels.items())
            lines.append(f"{m.name}{{{label_str}}} {m.value}")
        return "\n".join(lines)
