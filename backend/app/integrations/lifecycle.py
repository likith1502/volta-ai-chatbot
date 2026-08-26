import logging
from enum import Enum

logger = logging.getLogger("app.integrations.lifecycle")


class IntegrationLifecycleState(str, Enum):
    """Lifecycle states of an integration provider."""

    REGISTERED = "registered"
    INITIALIZING = "initializing"
    CONNECTED = "connected"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


class IntegrationLifecycleManager:
    """Manages legal state machine transitions for integration adapters."""

    def __init__(
        self,
        initial_state: IntegrationLifecycleState = IntegrationLifecycleState.REGISTERED,
    ) -> None:
        self.current_state = initial_state

    def transition_to(self, target_state: IntegrationLifecycleState) -> bool:
        valid_transitions = {
            IntegrationLifecycleState.REGISTERED: [
                IntegrationLifecycleState.INITIALIZING,
                IntegrationLifecycleState.FAILED,
            ],
            IntegrationLifecycleState.INITIALIZING: [
                IntegrationLifecycleState.CONNECTED,
                IntegrationLifecycleState.FAILED,
            ],
            IntegrationLifecycleState.CONNECTED: [
                IntegrationLifecycleState.HEALTHY,
                IntegrationLifecycleState.DEGRADED,
                IntegrationLifecycleState.FAILED,
            ],
            IntegrationLifecycleState.HEALTHY: [
                IntegrationLifecycleState.DEGRADED,
                IntegrationLifecycleState.RECONNECTING,
                IntegrationLifecycleState.FAILED,
            ],
            IntegrationLifecycleState.DEGRADED: [
                IntegrationLifecycleState.HEALTHY,
                IntegrationLifecycleState.RECONNECTING,
                IntegrationLifecycleState.FAILED,
            ],
            IntegrationLifecycleState.RECONNECTING: [
                IntegrationLifecycleState.CONNECTED,
                IntegrationLifecycleState.HEALTHY,
                IntegrationLifecycleState.FAILED,
            ],
            IntegrationLifecycleState.FAILED: [IntegrationLifecycleState.INITIALIZING],
        }

        allowed = valid_transitions.get(self.current_state, [])
        if target_state in allowed:
            logger.info(
                f"Integration lifecycle transition: {self.current_state.value} -> {target_state.value}"
            )
            self.current_state = target_state
            return True
        else:
            logger.warning(
                f"Invalid integration lifecycle transition attempt: {self.current_state.value} -> {target_state.value}"
            )
            return False
