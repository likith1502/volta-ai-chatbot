class WorkflowEventException(Exception):
    """Base exception for all workflow event system errors."""

    pass


class DuplicateEventException(WorkflowEventException):
    """Raised when registering an event ID that already exists."""

    pass


class DuplicateListenerException(WorkflowEventException):
    """Raised when registering a listener ID that is already registered."""

    pass


class EventListenerNotFoundException(WorkflowEventException):
    """Raised when looking up an unregistered listener ID."""

    pass


class EventDispatchException(WorkflowEventException):
    """Raised when an unhandled error occurs during event dispatching."""

    pass


class EventSerializationException(WorkflowEventException):
    """Raised when event serialization or deserialization fails."""

    pass


class EventValidationException(WorkflowEventException):
    """Raised when event payload or schema validation fails."""

    pass
