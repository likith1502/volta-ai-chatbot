import json
from abc import ABC, abstractmethod

from app.streaming.exceptions import StreamSerializationException
from app.streaming.stream_message import StreamMessage


class StreamSerializer(ABC):
    """Abstract interface for stream payload serialization and deserialization."""

    @abstractmethod
    def serialize(self, message: StreamMessage) -> bytes:
        """Serializes a StreamMessage into bytes."""
        pass

    @abstractmethod
    def deserialize(self, data: bytes) -> StreamMessage:
        """Deserializes bytes into a StreamMessage."""
        pass


class JSONStreamSerializer(StreamSerializer):
    """JSON implementation of StreamSerializer."""

    def serialize(self, message: StreamMessage) -> bytes:
        try:
            return message.model_dump_json().encode("utf-8")
        except Exception as exc:
            raise StreamSerializationException(f"Failed to serialize StreamMessage to JSON: {exc}")

    def deserialize(self, data: bytes) -> StreamMessage:
        try:
            raw_str = data.decode("utf-8")
            raw_dict = json.loads(raw_str)
            return StreamMessage.model_validate(raw_dict)
        except Exception as exc:
            raise StreamSerializationException(f"Failed to deserialize JSON bytes to StreamMessage: {exc}")


class MessagePackStreamSerializer(StreamSerializer):
    """Contract placeholder for MessagePack stream serialization."""

    def serialize(self, message: StreamMessage) -> bytes:
        return message.model_dump_json().encode("utf-8")

    def deserialize(self, data: bytes) -> StreamMessage:
        return StreamMessage.model_validate(json.loads(data.decode("utf-8")))


class ProtobufStreamSerializer(StreamSerializer):
    """Contract placeholder for Protobuf stream serialization."""

    def serialize(self, message: StreamMessage) -> bytes:
        return message.model_dump_json().encode("utf-8")

    def deserialize(self, data: bytes) -> StreamMessage:
        return StreamMessage.model_validate(json.loads(data.decode("utf-8")))
