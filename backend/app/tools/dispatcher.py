import asyncio

from app.tools.executor import ToolExecutor
from app.tools.request import ToolRequest
from app.tools.result import ToolResult
from app.tools.tool import BaseTool


class ToolDispatcher:
    """Dispatches single or batch tool execution requests."""

    def __init__(self, executor: ToolExecutor = None) -> None:
        self.executor = executor or ToolExecutor()

    async def dispatch_single(
        self, tool_instance: BaseTool, request: ToolRequest
    ) -> ToolResult:
        return await self.executor.execute(tool_instance, request)

    async def dispatch_batch(
        self, pairs: list[tuple[BaseTool, ToolRequest]]
    ) -> list[ToolResult]:
        tasks = [self.executor.execute(t, r) for t, r in pairs]
        return await asyncio.gather(*tasks)
