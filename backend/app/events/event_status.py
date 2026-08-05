from enum import Enum


class WorkflowEventStatus(str, Enum):
    """Lifecycle states of a workflow event during routing and processing."""

    CREATED = "created"
    QUEUED = "queued"
    DISPATCHED = "dispatched"
    PROCESSED = "processed"
    FAILED = "failed"
    IGNORED = "ignored"
