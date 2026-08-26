from app.tools.request import ToolRequest
from app.tools.result import ToolResult
from app.tools.tool import BaseTool
from app.tools.type import ToolType


class CalculatorTool(BaseTool):
    """In-memory calculation tool performing arithmetic operations (add, subtract, multiply, divide)."""

    def __init__(self) -> None:
        super().__init__(
            name="calculator",
            description="Performs arithmetic operations (add, subtract, multiply, divide) on two numbers.",
            tool_type=ToolType.MATH,
            input_schema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First operand"},
                    "b": {"type": "number", "description": "Second operand"},
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "Arithmetic operation",
                    },
                },
                "required": ["a", "b", "operation"],
            },
            output_schema={
                "type": "object",
                "properties": {
                    "result": {"type": "number"},
                    "operation": {"type": "string"},
                },
            },
        )

    async def execute(self, request: ToolRequest) -> ToolResult:
        a = float(request.arguments.get("a", 0))
        b = float(request.arguments.get("b", 0))
        op = str(request.arguments.get("operation", "add")).lower().strip()

        if op == "add":
            res = a + b
        elif op == "subtract":
            res = a - b
        elif op == "multiply":
            res = a * b
        elif op == "divide":
            if b == 0:
                return ToolResult(
                    tool_name=self.name,
                    execution_id=request.execution_id,
                    status="error",
                    success=False,
                    errors=["Division by zero error."],
                )
            res = a / b
        else:
            return ToolResult(
                tool_name=self.name,
                execution_id=request.execution_id,
                status="error",
                success=False,
                errors=[f"Unsupported operation '{op}'."],
            )

        return ToolResult(
            tool_name=self.name,
            execution_id=request.execution_id,
            status="success",
            success=True,
            output={"result": res, "operation": op},
        )
