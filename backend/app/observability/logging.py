"""Structured logging provider."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LogEntry:
    level: str
    message: str
    service: str = "volta-platform"
    trace_id: str = ""
    span_id: str = ""
    labels: dict[str, Any] = field(default_factory=dict)
    timestamp: float = 1786088000.0


class LoggingProvider(ABC):
    @abstractmethod
    def log(self, level: str, message: str, **kwargs: Any) -> None: ...

    @abstractmethod
    def get_entries(self) -> list[LogEntry]: ...


class StructuredLoggingProvider(LoggingProvider):
    """Reference structured logging provider with JSON output."""

    provider_id = "logging.structured"
    name = "Structured Logging Provider"

    def __init__(self, service: str = "volta-platform") -> None:
        self._service = service
        self._entries: list[LogEntry] = []
        self._logger = logging.getLogger(f"observability.{service}")

    def log(self, level: str, message: str, **kwargs: Any) -> None:
        entry = LogEntry(
            level=level, message=message, service=self._service, labels=kwargs
        )
        self._entries.append(entry)
        getattr(self._logger, level.lower(), self._logger.info)(message, extra=kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self.log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self.log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self.log("ERROR", message, **kwargs)

    def get_entries(self) -> list[LogEntry]:
        return list(self._entries)
