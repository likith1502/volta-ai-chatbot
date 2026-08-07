from enum import Enum


class ToolType(str, Enum):
    """Categorical classification types for tools."""

    SYSTEM = "system"
    UTILITY = "utility"
    MATH = "math"
    TIME = "time"
    TEXT = "text"
    FILE = "file"
    NETWORK = "network"
    SEARCH = "search"
    CUSTOM = "custom"
