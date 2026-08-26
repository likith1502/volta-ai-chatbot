class CheckpointError(Exception):
    """Base exception for all checkpoint and replay system errors."""

    pass


class CheckpointNotFoundError(CheckpointError):
    """Raised when looking up a checkpoint that does not exist."""

    pass


class CheckpointValidationError(CheckpointError):
    """Raised when checkpoint schema, snapshot, or integrity validation fails."""

    pass


class CheckpointStoreError(CheckpointError):
    """Raised when an error occurs within a checkpoint store operation."""

    pass


class ReplayError(CheckpointError):
    """Base exception for execution replay operations."""

    pass


class ReplayValidationError(ReplayError):
    """Raised when replay context, checkpoint compatibility, or strategy validation fails."""

    pass


class ReplayStrategyError(ReplayError):
    """Raised when an error occurs during replay strategy execution."""

    pass
