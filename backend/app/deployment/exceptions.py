"""Deployment exceptions."""


class DeploymentException(Exception):
    """Base class for all deployment exceptions."""


class DeploymentValidationError(DeploymentException):
    """Raised when deployment validation fails."""


class DeploymentStrategyError(DeploymentException):
    """Raised when a deployment strategy cannot execute."""


class RollbackError(DeploymentException):
    """Raised when rollback execution fails."""


class ScalingError(DeploymentException):
    """Raised when a scaling operation fails."""


class BackupError(DeploymentException):
    """Raised when a backup operation fails."""


class RecoveryError(DeploymentException):
    """Raised when disaster recovery execution fails."""


class ReleaseCompatibilityError(DeploymentException):
    """Raised when two releases are incompatible."""


class EnvironmentNotFoundError(DeploymentException):
    """Raised when an unknown environment is referenced."""
