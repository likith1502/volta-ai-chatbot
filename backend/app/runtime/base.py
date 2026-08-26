from abc import ABC, abstractmethod
from typing import AsyncIterator, Union

from app.runtime.contracts import (
    ChatMessage,
    ProviderCapabilities,
    RuntimeRequest,
    RuntimeResponse,
)
from app.streaming import StreamMessage


class RuntimeProvider(ABC):
    """Abstract Base Class defining standard, provider-independent LLM runtime execution contracts."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns provider identifier name (e.g. 'gemini', 'mock')."""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initializes client SDK connection and validates authentication credentials."""
        pass

    @abstractmethod
    async def generate(self, request: RuntimeRequest) -> RuntimeResponse:
        """Executes a single chat completion turn and returns standardized RuntimeResponse."""
        pass

    @abstractmethod
    async def generate_stream(
        self, request: RuntimeRequest
    ) -> AsyncIterator[StreamMessage]:
        """Executes a streaming response turn yielding StreamMessage tokens."""
        pass

    @abstractmethod
    def count_tokens(self, content: Union[str, list[ChatMessage]]) -> int:
        """Calculates or estimates token count for given text or list of ChatMessages."""
        pass

    @abstractmethod
    def get_capabilities(self) -> ProviderCapabilities:
        """Returns capability flags and supported models for this provider."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Performs active connectivity check and returns True if healthy."""
        pass
