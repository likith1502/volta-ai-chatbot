from abc import ABC, abstractmethod
from pydantic import BaseModel

from app.streaming.stream_message import StreamMessage
from app.streaming.heartbeat import StreamHeartbeat


class AdapterCapabilities(BaseModel):
    """Declared capabilities supported by a stream transport adapter implementation."""

    supports_binary: bool = False
    supports_batch: bool = False
    supports_heartbeat: bool = True
    supports_backpressure: bool = False
    supports_compression: bool = False
    supports_replay: bool = False


class StreamAdapter(ABC):
    """Abstract interface defining contracts for stream transport adapters."""

    @property
    def capabilities(self) -> AdapterCapabilities:
        """Returns adapter capabilities specification."""
        return AdapterCapabilities()

    @abstractmethod
    async def connect(self) -> None:
        """Establishes connection to external transport."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Closes connection to external transport."""
        pass

    @abstractmethod
    async def send(self, message: StreamMessage) -> bool:
        """Sends a StreamMessage through the adapter transport."""
        pass

    @abstractmethod
    async def flush(self) -> None:
        """Flushes buffered message queues."""
        pass

    @abstractmethod
    async def heartbeat(self) -> StreamHeartbeat:
        """Sends or checks transport heartbeat health."""
        pass
