import uuid

from app.tools.request import ToolRequest
from app.tools.result import ToolResult
from app.tools.tool import BaseTool
from app.tools.type import ToolType


class UUIDTool(BaseTool):
    """In-memory reference tool generating cryptographically secure UUIDv4 strings."""

    def __init__(self) -> None:
        super().__init__(
            name="uuid",
            description="Generates a cryptographically secure UUIDv4 string.",
            tool_type=ToolType.UTILITY,
            input_schema={"type": "object", "properties": {}},
            output_schema={
                "type": "object",
                "properties": {"uuid": {"type": "string"}},
            },
        )

    async def execute(self, request: ToolRequest) -> ToolResult:
        new_uuid = str(uuid.uuid4())
        return ToolResult(
            tool_name=self.name,
            execution_id=request.execution_id,
            status="success",
            success=True,
            output={"uuid": new_uuid},
        )
