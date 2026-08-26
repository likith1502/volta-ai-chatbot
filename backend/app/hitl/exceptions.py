class HumanLoopError(Exception):
    """Base exception for all human-in-the-loop (HITL) system errors."""

    pass


class ApprovalNotFoundError(HumanLoopError):
    """Raised when looking up an approval request that does not exist."""

    pass


class ApprovalValidationError(HumanLoopError):
    """Raised when approval request data, constraint, or policy validation fails."""

    pass


class ApprovalExpiredError(HumanLoopError):
    """Raised when attempting an operation on an expired approval request."""

    pass


class ApprovalAlreadyResolvedError(HumanLoopError):
    """Raised when attempting to approve, reject, or resolve an already completed request."""

    pass


class ApprovalRegistryError(HumanLoopError):
    """Raised when an error occurs in approval policy or handler registry operations."""

    pass


class HumanTaskError(HumanLoopError):
    """Raised when human task orchestration or lifecycle operations fail."""

    pass


class HumanTaskValidationError(HumanTaskError):
    """Raised when human task payload or boundary validation fails."""

    pass


class ResumeError(HumanLoopError):
    """Raised when execution resume operations from approval or checkpoint fail."""

    pass


class GovernanceError(HumanLoopError):
    """Raised when governance policies or separation of duties constraints are violated."""

    pass
