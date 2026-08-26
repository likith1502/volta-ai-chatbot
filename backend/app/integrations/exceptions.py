class IntegrationError(Exception):
    """Base exception for all Enterprise Integration Platform errors."""

    pass


class ProviderNotFoundError(IntegrationError):
    """Raised when a requested provider ID is not registered."""

    pass


class ConnectionFailedError(IntegrationError):
    """Raised when adapter connectivity check fails."""

    pass


class SecretResolutionError(IntegrationError):
    """Raised when secret provider fails to resolve a required credential."""

    pass
