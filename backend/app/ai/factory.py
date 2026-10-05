from typing import Optional

from app.ai.base import AIProvider
from app.ai.exceptions import AIProviderException
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.config.settings import settings


class AIProviderFactory:
    """Factory for instantiating provider-agnostic AIProvider implementations."""

    @staticmethod
    def get_provider(provider_name: Optional[str] = None) -> AIProvider:
        """Instantiates and returns the configured AIProvider instance."""
        target_provider = (provider_name or settings.AI_PROVIDER).lower()

        if target_provider == "openai":
            return OpenAIProvider()
        elif target_provider == "gemini":
            return GeminiProvider()
        else:
            raise AIProviderException(
                f"Unsupported AI provider '{target_provider}'. Supported options: ['openai', 'gemini']."
            )
