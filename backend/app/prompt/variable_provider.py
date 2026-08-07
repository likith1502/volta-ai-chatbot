from abc import ABC, abstractmethod
from typing import Any
from app.prompt.contracts import PromptRequest


class VariableProvider(ABC):
    """Abstract Base Class for dynamic variable resolution (enables seamless injection from Phase 7.2 Memory Runtime, Phase 7.3 Tool Runtime, or external DB)."""

    @abstractmethod
    async def resolve_variables(self, request: PromptRequest) -> dict[str, Any]:
        """Resolves dynamic variable key-value pairs for given PromptRequest."""
        pass


class DefaultVariableProvider(VariableProvider):
    """Default variable provider returning variables directly from PromptRequest payload."""

    async def resolve_variables(self, request: PromptRequest) -> dict[str, Any]:
        return request.variables.copy()
