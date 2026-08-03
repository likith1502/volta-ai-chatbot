from abc import ABC, abstractmethod

from app.ai.models import AIRequest, AIResponse


class AIProvider(ABC):
    """Abstract provider interface for conversational AI engines."""

    @abstractmethod
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generates an AI response from a standardized AIRequest payload."""
        pass
