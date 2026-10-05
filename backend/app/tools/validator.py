from typing import Any
from app.tools.exceptions import ToolValidationError
from app.tools.manifest import ToolManifest


class ToolValidator:
    """Validates tool execution arguments against JSON Schema definitions."""

    def validate(self, manifest: ToolManifest, arguments: dict[str, Any]) -> bool:
        if not manifest or not manifest.schema_spec:
            return True

        req_params = manifest.schema_spec.input_schema.get("required", [])
        for req in req_params:
            if req not in arguments:
                raise ToolValidationError(f"Missing required parameter '{req}' for tool '{manifest.tool_name}'.")

        return True
