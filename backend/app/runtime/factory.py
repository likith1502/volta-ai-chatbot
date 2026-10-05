import logging
from app.config.settings import settings
from app.runtime.base import RuntimeProvider
from app.runtime.providers.gemini_provider import GeminiProvider
from app.runtime.providers.mock_provider import MockProvider

logger = logging.getLogger("app.runtime.factory")


class RuntimeFactory:
    """Factory responsible for constructing configured RuntimeProvider instances."""

    @staticmethod
    def create_provider(provider_name: str) -> RuntimeProvider:
        """Constructs and returns a RuntimeProvider instance for the requested provider name."""
        name = provider_name.lower().strip()
        if name == "gemini":
            return GeminiProvider(
                api_key=settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY,
                default_model=settings.GEMINI_MODEL,
            )
        elif name == "mock":
            return MockProvider(latency_ms=15.0)
        else:
            logger.warning(f"Unknown provider '{provider_name}' requested from RuntimeFactory. Falling back to MockProvider.")
            return MockProvider()
