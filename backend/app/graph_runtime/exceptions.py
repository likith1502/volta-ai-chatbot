from typing import Optional

from app.core.exceptions import AppError


class GraphRuntimeError(AppError):
    """Base exception for Graph Runtime errors."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, status_code=500, details=details)
        self.code = "GRAPH_RUNTIME_ERROR"


class GraphNodeNotFoundError(GraphRuntimeError):
    """Raised when a target graph node is missing."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "GRAPH_NODE_NOT_FOUND"
        self.status_code = 404


class GraphPlanningError(GraphRuntimeError):
    """Raised when graph execution plan generation fails."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "GRAPH_PLANNING_ERROR"
        self.status_code = 400


class GraphSchedulingError(GraphRuntimeError):
    """Raised when graph node scheduling fails."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "GRAPH_SCHEDULING_ERROR"
        self.status_code = 500


class GraphExecutionInterruptedError(GraphRuntimeError):
    """Raised when execution is interrupted by HITL or pause command."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "GRAPH_INTERRUPTED"
        self.status_code = 202
