from typing import Optional

from app.core.exceptions import AppError


class PromptError(AppError):
    """Base exception for all Prompt Execution Engine failures."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, status_code=500, details=details)
        self.code = "PROMPT_ERROR"


class TemplateNotFoundError(PromptError):
    """Raised when a requested prompt template or revision is not found."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "TEMPLATE_NOT_FOUND"
        self.status_code = 404


class PromptValidationError(PromptError):
    """Raised when prompt validation fails due to missing variables or constraint violations."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "PROMPT_VALIDATION_ERROR"
        self.status_code = 400


class PromptRenderError(PromptError):
    """Raised when template rendering fails during variable substitution."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "PROMPT_RENDER_ERROR"
        self.status_code = 500


class PromptOptimizationError(PromptError):
    """Raised when prompt optimization encounters structural invalidity."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "PROMPT_OPTIMIZATION_ERROR"
        self.status_code = 500


class PromptSecurityViolationError(PromptError):
    """Raised when prompt violates security policy (e.g. injection attempt detected)."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "PROMPT_SECURITY_VIOLATION"
        self.status_code = 403
