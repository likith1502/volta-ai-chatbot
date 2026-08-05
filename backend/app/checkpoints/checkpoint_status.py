from enum import Enum


class CheckpointStatus(str, Enum):
    """Lifecycle states of an execution checkpoint."""

    CREATED = "created"
    ACTIVE = "active"
    ARCHIVED = "archived"
    EXPIRED = "expired"
    CORRUPTED = "corrupted"
    RESTORED = "restored"


class ReplayMode(str, Enum):
    """Modes supported by the execution replay engine."""

    FULL = "full"
    STEP = "step"
    RESUME = "resume"
    SIMULATION = "simulation"
    DEBUG = "debug"


class ReplayAction(str, Enum):
    """Structured action identifiers recorded in replay history."""

    START = "start"
    STEP_FORWARD = "step_forward"
    STEP_BACKWARD = "step_backward"
    RESUME = "resume"
    RESTART = "restart"
    FINISH = "finish"
    CANCEL = "cancel"
