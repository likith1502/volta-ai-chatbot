from typing import Optional
from app.tools.permission import ToolPermission
from app.tools.status import ToolStatus
from app.tools.type import ToolType


class ToolFilter:
    """Filter criteria container for querying registered tools."""

    def __init__(
        self,
        tool_type: Optional[ToolType] = None,
        status: Optional[ToolStatus] = None,
        permission: Optional[ToolPermission] = None,
        tags: Optional[list[str]] = None,
    ) -> None:
        self.tool_type = tool_type
        self.status = status
        self.permission = permission
        self.tags = tags or []

    def matches(self, manifest) -> bool:
        """Returns True if manifest matches all non-None criteria."""
        if self.status == ToolStatus.ACTIVE and manifest.deprecated:
            return False
        if self.permission and manifest.required_permission != self.permission:
            return False
        return True
