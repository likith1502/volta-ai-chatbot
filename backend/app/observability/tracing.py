"""Distributed tracing provider — OpenTelemetry reference implementation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
import uuid


@dataclass
class Span:
    span_id: str
    trace_id: str
    operation: str
    service: str = "volta-platform"
    duration_ms: float = 0.0
    status: str = "OK"
    attributes: dict[str, Any] = field(default_factory=dict)
    started_at: float = 1786088000.0


class TracingProvider(ABC):
    @abstractmethod
    def start_span(self, operation: str, trace_id: str | None = None) -> Span: ...

    @abstractmethod
    def finish_span(self, span: Span, duration_ms: float) -> None: ...

    @abstractmethod
    def get_traces(self) -> list[Span]: ...


class OpenTelemetryTracingProvider(TracingProvider):
    """Reference OpenTelemetry tracing provider (in-memory, no SDK required)."""

    provider_id = "tracing.opentelemetry"
    name = "OpenTelemetry Tracing Provider"

    def __init__(self, service: str = "volta-platform") -> None:
        self._service = service
        self._spans: list[Span] = []

    def start_span(self, operation: str, trace_id: str | None = None) -> Span:
        span = Span(
            span_id=uuid.uuid4().hex[:16],
            trace_id=trace_id or uuid.uuid4().hex[:32],
            operation=operation,
            service=self._service,
        )
        return span

    def finish_span(self, span: Span, duration_ms: float) -> None:
        span.duration_ms = duration_ms
        self._spans.append(span)

    def get_traces(self) -> list[Span]:
        return list(self._spans)
