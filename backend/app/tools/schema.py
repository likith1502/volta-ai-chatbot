from typing import Any

from pydantic import BaseModel, Field


class ToolSchema(BaseModel):
    """Structural schema specification contract defining JSON input/output parameters and examples."""

    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    input_schema: dict[str, Any] = Field(
        default_factory=dict, description="JSON Schema dict for parameters"
    )
    output_schema: dict[str, Any] = Field(
        default_factory=dict, description="JSON Schema dict for returns"
    )
    examples: list[dict[str, Any]] = Field(default_factory=list)
    version: str = "1.0.0"
