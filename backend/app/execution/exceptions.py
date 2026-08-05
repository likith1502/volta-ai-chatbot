class ExecutionException(Exception):
    """Base exception for all graph execution engine errors."""

    pass


class ExecutionTimeoutException(ExecutionException):
    """Raised when graph execution exceeds allowed maximum execution time."""

    pass


class ExecutionCancelledException(ExecutionException):
    """Raised when graph execution is cancelled."""

    pass


class ExecutionValidationException(ExecutionException):
    """Raised when graph structure validation fails prior to or during execution."""

    pass


class ExecutionStrategyException(ExecutionException):
    """Raised when an error occurs within an execution strategy."""

    pass
