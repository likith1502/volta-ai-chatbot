from typing import Optional

from app.core.exceptions import AppError


class ToolError(AppError):
    """Base exception for all Tool Runtime failures."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, status_code=500, details=details)
        self.code = "TOOL_ERROR"


class ToolNotFoundError(ToolError):
    """Raised when a requested tool name is not registered."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "TOOL_NOT_FOUND"
        self.status_code = 404


class ToolValidationError(ToolError):
    """Raised when tool argument validation against JSON schema fails."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "TOOL_VALIDATION_ERROR"
        self.status_code = 400


class ToolExecutionError(ToolError):
    """Raised when tool body execution fails."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "TOOL_EXECUTION_ERROR"
        self.status_code = 500


class ToolPermissionDeniedError(ToolError):
    """Raised when caller lacks permission to execute the tool."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "TOOL_PERMISSION_DENIED"
        self.status_code = 403


class ToolPolicyViolationError(ToolError):
    """Raised when execution violates tool policy (timeout, rate limit, concurrency)."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "TOOL_POLICY_VIOLATION"
        self.status_code = 400
