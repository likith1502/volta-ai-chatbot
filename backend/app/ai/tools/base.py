from abc import ABC, abstractmethod
from typing import Any

from app.ai.models import AIToolResult


class AITool(ABC):
    """Abstract interface for provider-independent AI tools."""

    name: str = "base_tool"
    description: str = "Base AI tool interface"

    @abstractmethod
    async def execute(self, arguments: dict[str, Any]) -> AIToolResult:
        """Executes the tool with the provided arguments dictionary."""
        pass
