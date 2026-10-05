import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.tools.capabilities import ToolCapabilities
from app.tools.metadata import ToolMetadata
from app.tools.request import ToolRequest
from app.tools.result import ToolResult
from app.tools.schema import ToolSchema
from app.tools.status import ToolStatus
from app.tools.type import ToolType


class Tool(BaseModel):
    """Primary domain model representing a registered executable tool."""

    tool_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str = Field(..., min_length=1)
    version: str = "1.0.0"
    description: str = Field(..., min_length=1)
    tool_type: ToolType = Field(default=ToolType.UTILITY)
    status: ToolStatus = Field(default=ToolStatus.ACTIVE)
    metadata: ToolMetadata = Field(default_factory=ToolMetadata)
    capabilities: ToolCapabilities = Field(default_factory=ToolCapabilities)
    schema_spec: Optional[ToolSchema] = None


class BaseTool(ABC):
    """Abstract Base Class for all concrete tool implementations."""

    def __init__(
        self,
        name: str,
        description: str,
        tool_type: ToolType = ToolType.UTILITY,
        version: str = "1.0.0",
        input_schema: Optional[dict[str, Any]] = None,
        output_schema: Optional[dict[str, Any]] = None,
    ) -> None:
        self.name = name
        self.description = description
        self.tool_type = tool_type
        self.version = version

        self.schema_spec = ToolSchema(
            name=name,
            description=description,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            version=version,
        )

        self.tool = Tool(
            name=name,
            version=version,
            description=description,
            tool_type=tool_type,
            schema_spec=self.schema_spec,
        )

    @abstractmethod
    async def execute(self, request: ToolRequest) -> ToolResult:
        """Executes the tool logic asynchronously and returns ToolResult."""
        pass
