class ExecutionError(Exception):
    """Base exception for all graph execution engine errors."""

    pass


class ExecutionTimeoutError(ExecutionError):
    """Raised when graph execution exceeds allowed maximum execution time."""

    pass


class ExecutionCancelledError(ExecutionError):
    """Raised when graph execution is cancelled."""

    pass


class ExecutionValidationError(ExecutionError):
    """Raised when graph structure validation fails prior to or during execution."""

    pass


class ExecutionStrategyError(ExecutionError):
    """Raised when an error occurs within an execution strategy."""

    pass
