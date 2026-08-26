class AgentRuntimeError(Exception):
    """Base exception for all Agent Runtime errors."""

    pass


class AgentNotFoundError(AgentRuntimeError):
    """Raised when an agent ID or definition cannot be found."""

    pass


class AgentDelegationError(AgentRuntimeError):
    """Raised when task delegation fails or exceeds depth limit."""

    pass


class AgentTaskError(AgentRuntimeError):
    """Raised when task execution fails."""

    pass


class AgentCommunicationError(AgentRuntimeError):
    """Raised when inter-agent message delivery fails."""

    pass


class AgentBudgetExhaustedError(AgentRuntimeError):
    """Raised when an agent exhausts its execution budget."""

    pass


class AgentPermissionDeniedError(AgentRuntimeError):
    """Raised when an action is prohibited by agent permissions."""

    pass
