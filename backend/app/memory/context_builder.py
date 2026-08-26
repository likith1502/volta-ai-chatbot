from typing import Any, Optional

from app.memory.context import MemoryContext
from app.memory.strategy import ContextAssemblyStrategy, HybridStrategy
from app.prompt.contracts import PromptRequest
from app.prompt.variable_provider import VariableProvider


class MemoryContextBuilder:
    """Constructs MemoryContext payloads using ContextAssemblyStrategy."""

    def __init__(self, strategy: Optional[ContextAssemblyStrategy] = None) -> None:
        self.strategy = strategy or HybridStrategy()

    def build_context(self, memories: list, token_budget: int = 4000) -> MemoryContext:
        return self.strategy.assemble(memories, token_budget=token_budget)


class MemoryVariableProvider(VariableProvider):
    """Integrates Memory Runtime with Prompt Execution Engine by extending Prompt Engine's VariableProvider ABC."""

    def __init__(self, memory_manager) -> None:
        self.memory_manager = memory_manager

    async def resolve_variables(self, request: PromptRequest) -> dict[str, Any]:
        """Dynamically resolves `{conversation_memory}` variable for PromptManager."""
        vars_copy = request.variables.copy()
        if request.conversation_id:
            try:
                ctx = await self.memory_manager.assemble_context(
                    conversation_id=request.conversation_id
                )
                vars_copy["conversation_memory"] = ctx.format_as_text()
            except Exception:
                vars_copy["conversation_memory"] = ""
        else:
            vars_copy["conversation_memory"] = ""
        return vars_copy
