from typing import Any, Optional
from app.core.exceptions import AppException


class AIProviderException(AppException):
    """Base exception for AI provider errors."""

    def __init__(self, message: str = "AI provider encountered an error", status_code: int = 500, details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=status_code, details=details)


class ModelUnavailableException(AIProviderException):
    """Raised when target AI model or provider endpoint is unreachable or unavailable."""

    def __init__(self, message: str = "AI model service is currently unavailable", details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=503, details=details)


class PromptTooLargeException(AIProviderException):
    """Raised when prompt context window size limit is exceeded."""

    def __init__(self, message: str = "Prompt exceeds maximum context token window limit", details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=400, details=details)


class RateLimitException(AIProviderException):
    """Raised when AI provider API rate limit or quota is exceeded."""

    def __init__(self, message: str = "AI provider API rate limit exceeded", details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=429, details=details)
