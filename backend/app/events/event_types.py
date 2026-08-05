from enum import Enum


class WorkflowEventCategory(str, Enum):
    """Broad functional categories for workflow events."""

    EXECUTION = "execution"
    NODE = "node"
    GRAPH = "graph"
    STATE = "state"
    CHECKPOINT = "checkpoint"
    SYSTEM = "system"
    SECURITY = "security"
    CUSTOM = "custom"


class EventPriority(str, Enum):
    """Priority levels for event dispatching and processing."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class WorkflowEventType(str, Enum):
    """Specific event type identifiers generated throughout workflow lifecycle."""

    EXECUTION_STARTED = "execution_started"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"
    NODE_STARTED = "node_started"
    NODE_COMPLETED = "node_completed"
    NODE_FAILED = "node_failed"
    EDGE_EVALUATED = "edge_evaluated"
    BRANCH_SELECTED = "branch_selected"
    STATE_UPDATED = "state_updated"
    SNAPSHOT_CREATED = "snapshot_created"
    CHECKPOINT_REQUESTED = "checkpoint_requested"
    WARNING_RAISED = "warning_raised"
    ERROR_RAISED = "error_raised"
    CUSTOM = "custom"
