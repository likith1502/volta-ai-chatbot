class WorkflowEventError(Exception):
    """Base exception for all workflow event system errors."""

    pass


class DuplicateEventError(WorkflowEventError):
    """Raised when registering an event ID that already exists."""

    pass


class DuplicateListenerError(WorkflowEventError):
    """Raised when registering a listener ID that is already registered."""

    pass


class EventListenerNotFoundError(WorkflowEventError):
    """Raised when looking up an unregistered listener ID."""

    pass


class EventDispatchError(WorkflowEventError):
    """Raised when an unhandled error occurs during event dispatching."""

    pass


class EventSerializationError(WorkflowEventError):
    """Raised when event serialization or deserialization fails."""

    pass


class EventValidationError(WorkflowEventError):
    """Raised when event payload or schema validation fails."""

    pass
