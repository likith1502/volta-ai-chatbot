from enum import Enum


class ToolPermission(str, Enum):
    """Authorization permission levels required to execute tools."""

    ALLOW = "allow"
    DENY = "deny"
    READONLY = "readonly"
    ADMIN = "admin"
