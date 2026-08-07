from enum import Enum


class HealthLevel(str, Enum):
    """Operational health level classification."""

    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"
