from app.tools.request import ToolRequest
from app.tools.result import ToolResult
from app.tools.tool import BaseTool
from app.tools.type import ToolType


class EchoTool(BaseTool):
    """In-memory utility tool echoing input message payload."""

    def __init__(self) -> None:
        super().__init__(
            name="echo",
            description="Echoes back the input message argument.",
            tool_type=ToolType.TEXT,
            input_schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Text message to echo"}
                },
                "required": ["message"],
            },
            output_schema={
                "type": "object",
                "properties": {"echo": {"type": "string"}},
            },
        )

    async def execute(self, request: ToolRequest) -> ToolResult:
        msg = request.arguments.get("message", "")
        return ToolResult(
            tool_name=self.name,
            execution_id=request.execution_id,
            status="success",
            success=True,
            output={"echo": str(msg)},
        )
