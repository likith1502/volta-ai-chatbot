from typing import Optional

from app.ai.tools.base import AITool


class AIToolRegistry:
    """Registry managing available AITool implementations."""

    def __init__(self) -> None:
        self._tools: dict[str, AITool] = {}

    def register(self, tool: AITool) -> None:
        """Registers an AITool instance."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[AITool]:
        """Retrieves a registered AITool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[AITool]:
        """Returns all registered AITool instances."""
        return list(self._tools.values())
