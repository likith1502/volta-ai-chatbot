"""Consolidated Telemetry Module for Streaming Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABC, abstractmethod
from app.streaming.exceptions import StreamSerializationException
from app.streaming.stream_message import StreamMessage
from datetime import datetime, timezone
from pydantic import BaseModel
from pydantic import BaseModel, Field
import json
import uuid

# --- Consolidated from stream_metrics.py ---
class StreamMetrics(BaseModel):
    """Telemetry metrics capturing stream message volume, dropped count, and throughput."""
    messages_sent: int = 0
    messages_dropped: int = 0
    subscribers: int = 0
    average_latency: float = 0.0
    throughput: float = 0.0
    errors: int = 0

    def record_sent(self, latency: float=0.0) -> None:
        """Records a successfully dispatched stream message."""
        self.messages_sent += 1
        if self.messages_sent == 1:
            self.average_latency = round(latency, 4)
        else:
            self.average_latency = round((self.average_latency * (self.messages_sent - 1) + latency) / self.messages_sent, 4)

    def record_dropped(self) -> None:
        """Records a dropped message due to backpressure or filtering."""
        self.messages_dropped += 1

    def record_error(self) -> None:
        """Records a stream dispatch error."""
        self.errors += 1

# --- Consolidated from stream_serializer.py ---
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
            return message.model_dump_json().encode('utf-8')
        except Exception as exc:
            raise StreamSerializationException(f'Failed to serialize StreamMessage to JSON: {exc}')

    def deserialize(self, data: bytes) -> StreamMessage:
        try:
            raw_str = data.decode('utf-8')
            raw_dict = json.loads(raw_str)
            return StreamMessage.model_validate(raw_dict)
        except Exception as exc:
            raise StreamSerializationException(f'Failed to deserialize JSON bytes to StreamMessage: {exc}')

class MessagePackStreamSerializer(StreamSerializer):
    """Contract placeholder for MessagePack stream serialization."""

    def serialize(self, message: StreamMessage) -> bytes:
        return message.model_dump_json().encode('utf-8')

    def deserialize(self, data: bytes) -> StreamMessage:
        return StreamMessage.model_validate(json.loads(data.decode('utf-8')))

class ProtobufStreamSerializer(StreamSerializer):
    """Contract placeholder for Protobuf stream serialization."""

    def serialize(self, message: StreamMessage) -> bytes:
        return message.model_dump_json().encode('utf-8')

    def deserialize(self, data: bytes) -> StreamMessage:
        return StreamMessage.model_validate(json.loads(data.decode('utf-8')))

# --- Consolidated from heartbeat.py ---
class StreamHeartbeat(BaseModel):
    """Heartbeat signal monitoring stream health and round-trip transport latency."""
    heartbeat_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    latency: float = 0.0
    status: str = 'healthy'

