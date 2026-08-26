from abc import ABC, abstractmethod
from typing import Any, Optional

from app.integrations.capabilities import IntegrationCapability
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport, IntegrationProvider
from app.integrations.status import IntegrationStatus


class LLMAdapter(IntegrationProvider, ABC):
    """Abstract interface wrapping LLM model runtime providers."""

    def __init__(self, provider_id: str, name: str, priority: int = 10) -> None:
        super().__init__(
            provider_id=provider_id,
            name=name,
            category=IntegrationCapability.LLM,
            priority=priority,
        )

    @abstractmethod
    async def generate_response(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> str:
        pass


class GeminiLLMAdapter(LLMAdapter):
    """Reference LLM adapter wrapping Google Gemini SDK."""

    def __init__(self) -> None:
        super().__init__(
            provider_id="llm.gemini", name="Google Gemini LLM Adapter", priority=10
        )
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[Any] = None) -> None:
        self._status = IntegrationStatus.READY
        await self.connect()

    async def connect(self) -> bool:
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def generate_response(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> str:
        return f"[Gemini LLM Response to '{prompt[:30]}...']"

    async def check_health(self) -> IntegrationHealthReport:
        return IntegrationHealthReport(
            provider_id=self.provider_id,
            provider_name=self.name,
            provider_type="Gemini",
            is_healthy=True,
            health_level=HealthLevel.GREEN,
            status=self.status,
            latency_ms=45.0,
        )


class OpenAILLMAdapter(GeminiLLMAdapter):
    """Extension placeholder for OpenAI LLM Adapter."""

    def __init__(self) -> None:
        super().__init__()
        self._provider_id = "llm.openai"
        self._name = "OpenAI GPT-4 LLM Adapter"
        self._priority = 90


class AnthropicLLMAdapter(GeminiLLMAdapter):
    """Extension placeholder for Anthropic Claude LLM Adapter."""

    def __init__(self) -> None:
        super().__init__()
        self._provider_id = "llm.anthropic"
        self._name = "Anthropic Claude LLM Adapter"
        self._priority = 85


class OllamaLLMAdapter(GeminiLLMAdapter):
    """Extension placeholder for Ollama Local LLM Adapter."""

    def __init__(self) -> None:
        super().__init__()
        self._provider_id = "llm.ollama"
        self._name = "Ollama Local LLM Adapter"
        self._priority = 50
