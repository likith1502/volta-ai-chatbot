from typing import Optional

from app.core.exceptions import AppError


class MemoryError(AppError):
    """Base exception for all Memory Runtime failures."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, status_code=500, details=details)
        self.code = "MEMORY_ERROR"


class MemoryNotFoundError(MemoryError):
    """Raised when a requested memory ID is not found."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "MEMORY_NOT_FOUND"
        self.status_code = 404


class MemoryValidationError(MemoryError):
    """Raised when memory validation fails."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "MEMORY_VALIDATION_ERROR"
        self.status_code = 400


class MemoryLimitExceededError(MemoryError):
    """Raised when memory storage limits or capacity budget are exceeded."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "MEMORY_LIMIT_EXCEEDED"
        self.status_code = 400


class ContextOverflowError(MemoryError):
    """Raised when memory context assembly exceeds token budget limit."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "CONTEXT_OVERFLOW"
        self.status_code = 400


class MemoryRepositoryError(MemoryError):
    """Raised when repository storage operations fail."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "MEMORY_REPOSITORY_ERROR"


class MemoryPolicyError(MemoryError):
    """Raised when policy evaluation fails."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "MEMORY_POLICY_ERROR"
