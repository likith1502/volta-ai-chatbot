class CheckpointException(Exception):
    """Base exception for all checkpoint and replay system errors."""

    pass


class CheckpointNotFoundException(CheckpointException):
    """Raised when looking up a checkpoint that does not exist."""

    pass


class CheckpointValidationException(CheckpointException):
    """Raised when checkpoint schema, snapshot, or integrity validation fails."""

    pass


class CheckpointStoreException(CheckpointException):
    """Raised when an error occurs within a checkpoint store operation."""

    pass


class ReplayException(CheckpointException):
    """Base exception for execution replay operations."""

    pass


class ReplayValidationException(ReplayException):
    """Raised when replay context, checkpoint compatibility, or strategy validation fails."""

    pass


class ReplayStrategyException(ReplayException):
    """Raised when an error occurs during replay strategy execution."""

    pass
