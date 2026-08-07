"""Deployment Lifecycle State Machine.

Legal transitions:
CREATED → VALIDATED → BUILDING → DEPLOYING → VERIFYING → RUNNING
RUNNING → SCALING → RUNNING
RUNNING → ROLLING_BACK → RUNNING | FAILED
Any → TERMINATED
Any → FAILED
"""

from enum import Enum
from typing import Optional
import logging

logger = logging.getLogger("app.deployment.lifecycle")


class DeploymentLifecycleState(str, Enum):
    CREATED = "created"
    VALIDATED = "validated"
    BUILDING = "building"
    DEPLOYING = "deploying"
    VERIFYING = "verifying"
    RUNNING = "running"
    SCALING = "scaling"
    ROLLING_BACK = "rolling_back"
    FAILED = "failed"
    TERMINATED = "terminated"


_LEGAL_TRANSITIONS: dict[DeploymentLifecycleState, set[DeploymentLifecycleState]] = {
    DeploymentLifecycleState.CREATED: {
        DeploymentLifecycleState.VALIDATED,
        DeploymentLifecycleState.FAILED,
        DeploymentLifecycleState.TERMINATED,
    },
    DeploymentLifecycleState.VALIDATED: {
        DeploymentLifecycleState.BUILDING,
        DeploymentLifecycleState.FAILED,
        DeploymentLifecycleState.TERMINATED,
    },
    DeploymentLifecycleState.BUILDING: {
        DeploymentLifecycleState.DEPLOYING,
        DeploymentLifecycleState.FAILED,
        DeploymentLifecycleState.TERMINATED,
    },
    DeploymentLifecycleState.DEPLOYING: {
        DeploymentLifecycleState.VERIFYING,
        DeploymentLifecycleState.ROLLING_BACK,
        DeploymentLifecycleState.FAILED,
        DeploymentLifecycleState.TERMINATED,
    },
    DeploymentLifecycleState.VERIFYING: {
        DeploymentLifecycleState.RUNNING,
        DeploymentLifecycleState.ROLLING_BACK,
        DeploymentLifecycleState.FAILED,
        DeploymentLifecycleState.TERMINATED,
    },
    DeploymentLifecycleState.RUNNING: {
        DeploymentLifecycleState.SCALING,
        DeploymentLifecycleState.ROLLING_BACK,
        DeploymentLifecycleState.TERMINATED,
        DeploymentLifecycleState.FAILED,
    },
    DeploymentLifecycleState.SCALING: {
        DeploymentLifecycleState.RUNNING,
        DeploymentLifecycleState.FAILED,
        DeploymentLifecycleState.TERMINATED,
    },
    DeploymentLifecycleState.ROLLING_BACK: {
        DeploymentLifecycleState.RUNNING,
        DeploymentLifecycleState.FAILED,
        DeploymentLifecycleState.TERMINATED,
    },
    DeploymentLifecycleState.FAILED: {
        DeploymentLifecycleState.TERMINATED,
        DeploymentLifecycleState.VALIDATED,  # Allow re-attempt
    },
    DeploymentLifecycleState.TERMINATED: set(),
}


class DeploymentLifecycleManager:
    """Enforces legal deployment lifecycle state transitions."""

    def __init__(self) -> None:
        self._state = DeploymentLifecycleState.CREATED
        self._history: list[DeploymentLifecycleState] = [DeploymentLifecycleState.CREATED]

    @property
    def state(self) -> DeploymentLifecycleState:
        return self._state

    @property
    def history(self) -> list[DeploymentLifecycleState]:
        return list(self._history)

    def transition(self, target: DeploymentLifecycleState) -> bool:
        """Attempt a legal state transition. Returns True if successful."""
        allowed = _LEGAL_TRANSITIONS.get(self._state, set())
        if target not in allowed:
            logger.warning(
                "Illegal transition %s → %s (allowed: %s)",
                self._state.value,
                target.value,
                [s.value for s in allowed],
            )
            return False
        self._state = target
        self._history.append(target)
        return True

    def can_transition(self, target: DeploymentLifecycleState) -> bool:
        return target in _LEGAL_TRANSITIONS.get(self._state, set())
