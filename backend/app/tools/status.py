from enum import Enum


class ToolStatus(str, Enum):
    """Lifecycle status states for registered tools."""

    ACTIVE = "active"
    DEPRECATED = "deprecated"
    DISABLED = "disabled"
    ERROR = "error"
