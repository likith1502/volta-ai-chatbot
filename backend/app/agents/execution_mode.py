from enum import Enum


class ExecutionMode(str, Enum):
    """Execution mode topologies for agent teams and workflows."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HYBRID = "hybrid"
    SUPERVISED = "supervised"
    MANUAL_APPROVAL = "manual_approval"
