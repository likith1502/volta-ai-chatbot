from typing import Optional

from app.ai.exceptions import AIProviderException
from app.ai.memory.base import MemoryStrategy
from app.ai.memory.recent import RecentConversationStrategy
from app.config.settings import settings


class MemoryStrategyFactory:
    """Factory instantiating MemoryStrategy implementations."""

    @staticmethod
    def get_strategy(strategy_name: Optional[str] = None) -> MemoryStrategy:
        """Instantiates and returns the configured MemoryStrategy."""
        target_name = (strategy_name or settings.MEMORY_STRATEGY).lower()

        if target_name == "recent":
            return RecentConversationStrategy()
        else:
            raise AIProviderException(f"Unsupported memory strategy '{target_name}'. Supported options: ['recent'].")
