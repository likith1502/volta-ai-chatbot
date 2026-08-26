import time

from app.tools.request import ToolRequest
from app.tools.result import ToolResult
from app.tools.tool import BaseTool


class ToolExecutor:
    """Executes BaseTool instances asynchronously with latency tracking and error boundary management."""

    async def execute(
        self, tool_instance: BaseTool, request: ToolRequest
    ) -> ToolResult:
        t0 = time.perf_counter()
        try:
            result = await tool_instance.execute(request)
            dt = (time.perf_counter() - t0) * 1000.0
            result.execution_time_ms = round(dt, 2)
            return result
        except Exception as exc:
            dt = (time.perf_counter() - t0) * 1000.0
            return ToolResult(
                tool_name=tool_instance.name,
                execution_id=request.execution_id,
                status="error",
                success=False,
                execution_time_ms=round(dt, 2),
                errors=[str(exc)],
            )
