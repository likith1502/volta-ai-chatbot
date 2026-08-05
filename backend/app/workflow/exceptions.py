class WorkflowNodeException(Exception):
    """Base exception for all workflow node errors."""

    pass


class DuplicateWorkflowNodeException(WorkflowNodeException):
    """Raised when registering a node with an ID that already exists in the registry."""

    pass


class WorkflowNodeNotFoundException(WorkflowNodeException):
    """Raised when looking up a node that does not exist in the registry."""

    pass


class WorkflowValidationException(WorkflowNodeException):
    """Raised when node input or output schema validation fails."""

    pass


class RegistryException(WorkflowNodeException):
    """Raised when a general node registry operation fails."""

    pass
