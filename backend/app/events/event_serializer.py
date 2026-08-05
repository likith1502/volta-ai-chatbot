from abc import ABC, abstractmethod
from typing import Union

from app.events.event import WorkflowEvent
from app.events.exceptions import EventSerializationException


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
            raise EventSerializationException(f"JSON serialization failed: {exc}") from exc

    def deserialize(self, data: Union[str, bytes]) -> WorkflowEvent:
        try:
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            return WorkflowEvent.model_validate_json(data)
        except Exception as exc:
            raise EventSerializationException(f"JSON deserialization failed: {exc}") from exc


class MessagePackEventSerializer(WorkflowEventSerializer):
    """Contract placeholder for future MessagePack event serialization."""

    def serialize(self, event: WorkflowEvent) -> bytes:
        return event.model_dump_json().encode("utf-8")

    def deserialize(self, data: Union[str, bytes]) -> WorkflowEvent:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        return WorkflowEvent.model_validate_json(data)


class ProtobufEventSerializer(WorkflowEventSerializer):
    """Contract placeholder for future Protocol Buffers event serialization."""

    def serialize(self, event: WorkflowEvent) -> bytes:
        return event.model_dump_json().encode("utf-8")

    def deserialize(self, data: Union[str, bytes]) -> WorkflowEvent:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        return WorkflowEvent.model_validate_json(data)
