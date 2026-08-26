class WorkflowNodeError(Exception):
    """Base exception for all workflow node errors."""

    pass


class DuplicateWorkflowNodeError(WorkflowNodeError):
    """Raised when registering a node with an ID that already exists in the registry."""

    pass


class WorkflowNodeNotFoundError(WorkflowNodeError):
    """Raised when looking up a node that does not exist in the registry."""

    pass


class WorkflowValidationError(WorkflowNodeError):
    """Raised when node input or output schema validation fails."""

    pass


class RegistryError(WorkflowNodeError):
    """Raised when a general node registry operation fails."""

    pass
