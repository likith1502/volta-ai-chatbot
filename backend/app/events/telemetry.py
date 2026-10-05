"""Consolidated Telemetry Module for Events Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABC, abstractmethod
from app.events.event import WorkflowEvent
from app.events.exceptions import EventSerializationException
from pydantic import BaseModel
from pydantic import BaseModel, Field
from typing import Any
from typing import Union

# --- Consolidated from event_metrics.py ---
class WorkflowEventMetrics(BaseModel):
    """Runtime statistics tracking event dispatch throughput, latency, and success rates."""
    events_processed: int = 0
    events_failed: int = 0
    dispatch_time: float = 0.0
    listener_time: float = 0.0
    success_rate: float = 1.0
    average_latency: float = 0.0

    def compute_metrics(self) -> None:
        """Recalculates success rate and average latency metrics."""
        total = self.events_processed + self.events_failed
        if total == 0:
            self.success_rate = 1.0
            self.average_latency = 0.0
        else:
            self.success_rate = round(self.events_processed / total, 4)
            self.average_latency = round(self.dispatch_time / total, 6)

# --- Consolidated from event_serializer.py ---
class WorkflowEventSerializer(ABC):
    """Abstract interface for workflow event serialization layers."""

    @abstractmethod
    def serialize(self, event: WorkflowEvent) -> Union[str, bytes]:
        """Serializes a WorkflowEvent instance into a string or bytes payload."""
        pass

    @abstractmethod
    def deserialize(self, data: Union[str, bytes]) -> WorkflowEvent:
        """Deserializes a string or bytes payload back into a WorkflowEvent instance."""
        pass

class JSONEventSerializer(WorkflowEventSerializer):
    """JSON serialization implementation using Pydantic model serialization."""

    def serialize(self, event: WorkflowEvent) -> str:
        try:
            return event.model_dump_json()
        except Exception as exc:
            raise EventSerializationException(f'JSON serialization failed: {exc}') from exc

    def deserialize(self, data: Union[str, bytes]) -> WorkflowEvent:
        try:
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            return WorkflowEvent.model_validate_json(data)
        except Exception as exc:
            raise EventSerializationException(f'JSON deserialization failed: {exc}') from exc

class MessagePackEventSerializer(WorkflowEventSerializer):
    """Contract placeholder for future MessagePack event serialization."""

    def serialize(self, event: WorkflowEvent) -> bytes:
        return event.model_dump_json().encode('utf-8')

    def deserialize(self, data: Union[str, bytes]) -> WorkflowEvent:
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        return WorkflowEvent.model_validate_json(data)

class ProtobufEventSerializer(WorkflowEventSerializer):
    """Contract placeholder for future Protocol Buffers event serialization."""

    def serialize(self, event: WorkflowEvent) -> bytes:
        return event.model_dump_json().encode('utf-8')

    def deserialize(self, data: Union[str, bytes]) -> WorkflowEvent:
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        return WorkflowEvent.model_validate_json(data)

# --- Consolidated from event_result.py ---
class WorkflowEventResult(BaseModel):
    """Container summarizing the processing outcome of an event dispatch cycle."""
    success: bool = True
    processed: int = 0
    ignored: int = 0
    listener_count: int = 0
    processing_time: float = 0.0
    warnings: list[str] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)

