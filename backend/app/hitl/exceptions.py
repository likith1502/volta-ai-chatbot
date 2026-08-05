class HumanLoopException(Exception):
    """Base exception for all human-in-the-loop (HITL) system errors."""

    pass


class ApprovalNotFoundException(HumanLoopException):
    """Raised when looking up an approval request that does not exist."""

    pass


class ApprovalValidationException(HumanLoopException):
    """Raised when approval request data, constraint, or policy validation fails."""

    pass


class ApprovalExpiredException(HumanLoopException):
    """Raised when attempting an operation on an expired approval request."""

    pass


class ApprovalAlreadyResolvedException(HumanLoopException):
    """Raised when attempting to approve, reject, or resolve an already completed request."""

    pass


class ApprovalRegistryException(HumanLoopException):
    """Raised when an error occurs in approval policy or handler registry operations."""

    pass


class HumanTaskException(HumanLoopException):
    """Raised when human task orchestration or lifecycle operations fail."""

    pass


class HumanTaskValidationException(HumanTaskException):
    """Raised when human task payload or boundary validation fails."""

    pass


class ResumeException(HumanLoopException):
    """Raised when execution resume operations from approval or checkpoint fail."""

    pass


class GovernanceException(HumanLoopException):
    """Raised when governance policies or separation of duties constraints are violated."""

    pass
