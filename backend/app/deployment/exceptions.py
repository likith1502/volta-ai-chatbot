"""Deployment exceptions."""


class DeploymentError(Exception):
    """Base class for all deployment exceptions."""


class DeploymentValidationError(DeploymentError):
    """Raised when deployment validation fails."""


class DeploymentStrategyError(DeploymentError):
    """Raised when a deployment strategy cannot execute."""


class RollbackError(DeploymentError):
    """Raised when rollback execution fails."""


class ScalingError(DeploymentError):
    """Raised when a scaling operation fails."""


class BackupError(DeploymentError):
    """Raised when a backup operation fails."""


class RecoveryError(DeploymentError):
    """Raised when disaster recovery execution fails."""


class ReleaseCompatibilityError(DeploymentError):
    """Raised when two releases are incompatible."""


class EnvironmentNotFoundError(DeploymentError):
    """Raised when an unknown environment is referenced."""
