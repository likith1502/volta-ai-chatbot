class AgentRuntimeException(Exception):
    """Base exception for all Agent Runtime errors."""

    pass


class AgentNotFoundError(AgentRuntimeException):
    """Raised when an agent ID or definition cannot be found."""

    pass


class AgentDelegationError(AgentRuntimeException):
    """Raised when task delegation fails or exceeds depth limit."""

    pass


class AgentTaskError(AgentRuntimeException):
    """Raised when task execution fails."""

    pass


class AgentCommunicationError(AgentRuntimeException):
    """Raised when inter-agent message delivery fails."""

    pass


class AgentBudgetExhaustedError(AgentRuntimeException):
    """Raised when an agent exhausts its execution budget."""

    pass


class AgentPermissionDeniedError(AgentRuntimeException):
    """Raised when an action is prohibited by agent permissions."""

    pass
