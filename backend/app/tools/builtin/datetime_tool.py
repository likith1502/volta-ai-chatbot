from datetime import datetime, timezone
from app.tools.request import ToolRequest
from app.tools.result import ToolResult
from app.tools.tool import BaseTool
from app.tools.type import ToolType


class DatetimeTool(BaseTool):
    """In-memory reference tool returning current UTC ISO timestamp."""

    def __init__(self) -> None:
        super().__init__(
            name="datetime",
            description="Returns current UTC ISO timestamp.",
            tool_type=ToolType.TIME,
            input_schema={"type": "object", "properties": {}},
            output_schema={
                "type": "object",
                "properties": {
                    "utc_timestamp": {"type": "string"}
                }
            }
        )

    async def execute(self, request: ToolRequest) -> ToolResult:
        now_str = datetime.now(timezone.utc).isoformat()
        return ToolResult(
            tool_name=self.name,
            execution_id=request.execution_id,
            status="success",
            success=True,
            output={"utc_timestamp": now_str},
        )
