from typing import Optional

from app.core.exceptions import AppError


class RuntimeError(AppError):
    """Base exception for all Enterprise LLM Runtime Engine failures."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, status_code=500, details=details)
        self.code = "RUNTIME_ERROR"


class ProviderNotFoundError(RuntimeError):
    """Raised when a requested AI provider is not registered in RuntimeRegistry."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "PROVIDER_NOT_FOUND"
        self.status_code = 444


class ProviderInitializationError(RuntimeError):
    """Raised when an AI provider fails during initialization or SDK setup."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "PROVIDER_INIT_ERROR"
        self.status_code = 502


class RuntimeExecutionError(RuntimeError):
    """Raised during LLM generation failure."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "RUNTIME_EXECUTION_ERROR"
        self.status_code = 502


class RuntimeTimeoutError(RuntimeError):
    """Raised when provider execution exceeds specified timeout."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "RUNTIME_TIMEOUT"
        self.status_code = 504


class RuntimeRetryExhaustedError(RuntimeError):
    """Raised when max retry attempts are exhausted without successful provider response."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "RETRY_EXHAUSTED"
        self.status_code = 504


class ProviderHealthCheckError(RuntimeError):
    """Raised when a provider health check fails."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "PROVIDER_UNHEALTHY"
        self.status_code = 503


class ProviderAuthenticationError(RuntimeError):
    """Raised when provider API key or credential authentication fails."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "PROVIDER_AUTH_ERROR"
        self.status_code = 401


class ProviderRateLimitError(RuntimeError):
    """Raised when provider rate limits are exceeded (HTTP 429)."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "PROVIDER_RATE_LIMIT"
        self.status_code = 429


class ProviderUnavailableError(RuntimeError):
    """Raised when remote provider API endpoint is unreachable or returning 5xx errors."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "PROVIDER_UNAVAILABLE"
        self.status_code = 503


class ProviderConfigurationError(RuntimeError):
    """Raised when invalid or missing provider configuration parameters are supplied."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message=message, details=details)
        self.code = "PROVIDER_CONFIG_INVALID"
        self.status_code = 400
