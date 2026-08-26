import logging

from app.ai.models import AIToolCall, AIToolResult
from app.ai.tools.registry import AIToolRegistry

logger = logging.getLogger("app.ai.tools.dispatcher")


class AIToolDispatcher:
    """Dispatcher executing tool requests issued by AI Providers."""

    def __init__(self, registry: AIToolRegistry) -> None:
        self.registry = registry

    async def dispatch(self, tool_call: AIToolCall) -> AIToolResult:
        """Locates and executes a tool call using the registered AITool implementation."""
        tool = self.registry.get(tool_call.tool_name)
        if not tool:
            logger.warning(
                f"Attempted to dispatch unregistered tool: '{tool_call.tool_name}'"
            )
            return AIToolResult(
                tool_name=tool_call.tool_name,
                success=False,
                error=f"Unregistered tool '{tool_call.tool_name}'",
            )

        logger.info(f"Dispatching tool execution for '{tool_call.tool_name}'")
        return await tool.execute(tool_call.arguments)
