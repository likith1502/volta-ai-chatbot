from typing import Any, Optional


class AppException(Exception):
    """Base application exception for custom error handling."""

    def __init__(
        self,
        message: str = "An application error occurred",
        status_code: int = 400,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details
