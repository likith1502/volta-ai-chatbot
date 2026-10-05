class IntegrationException(Exception):
    """Base exception for all Enterprise Integration Platform errors."""

    pass


class ProviderNotFoundError(IntegrationException):
    """Raised when a requested provider ID is not registered."""

    pass


class ConnectionFailedError(IntegrationException):
    """Raised when adapter connectivity check fails."""

    pass


class SecretResolutionError(IntegrationException):
    """Raised when secret provider fails to resolve a required credential."""

    pass
