from typing import Any, Optional

from pydantic import BaseModel, Field

from app.tools.capabilities import ToolCapabilities
from app.tools.permission import ToolPermission
from app.tools.schema import ToolSchema


class ToolManifest(BaseModel):
    """Complete tool packaging manifest containing schema, permissions, capabilities, and deprecation metadata."""

    tool_name: str = Field(..., min_length=1)
    version: str = "1.0.0"
    schema_spec: ToolSchema
    required_permission: ToolPermission = Field(default=ToolPermission.ALLOW)
    capabilities: ToolCapabilities = Field(default_factory=ToolCapabilities)
    examples: list[dict[str, Any]] = Field(default_factory=list)
    deprecated: bool = False
    replacement_tool: Optional[str] = None
