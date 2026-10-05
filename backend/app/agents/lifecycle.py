import logging
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("app.agents.lifecycle")


class AgentLifecycleState(str, Enum):
    """Lifecycle state machine transitions for an agent instance."""

    CREATED = "created"
    REGISTERED = "registered"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    DELEGATING = "delegating"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"


class AgentLifecycleManager(BaseModel):
    """Manages state transitions and validates lifecycle rules for agent instances."""

    current_state: AgentLifecycleState = AgentLifecycleState.CREATED
    previous_state: Optional[AgentLifecycleState] = None

    def transition_to(self, target_state: AgentLifecycleState) -> bool:
        """Transitions agent to target state if transition rule is valid."""
        valid_transitions: dict[AgentLifecycleState, list[AgentLifecycleState]] = {
            AgentLifecycleState.CREATED: [AgentLifecycleState.REGISTERED, AgentLifecycleState.TERMINATED],
            AgentLifecycleState.REGISTERED: [AgentLifecycleState.READY, AgentLifecycleState.TERMINATED],
            AgentLifecycleState.READY: [AgentLifecycleState.RUNNING, AgentLifecycleState.PAUSED, AgentLifecycleState.TERMINATED],
            AgentLifecycleState.RUNNING: [AgentLifecycleState.WAITING, AgentLifecycleState.DELEGATING, AgentLifecycleState.COMPLETED, AgentLifecycleState.FAILED, AgentLifecycleState.PAUSED],
            AgentLifecycleState.WAITING: [AgentLifecycleState.RUNNING, AgentLifecycleState.FAILED, AgentLifecycleState.TERMINATED],
            AgentLifecycleState.DELEGATING: [AgentLifecycleState.RUNNING, AgentLifecycleState.WAITING, AgentLifecycleState.FAILED],
            AgentLifecycleState.PAUSED: [AgentLifecycleState.READY, AgentLifecycleState.RUNNING, AgentLifecycleState.TERMINATED],
            AgentLifecycleState.COMPLETED: [AgentLifecycleState.READY, AgentLifecycleState.TERMINATED],
            AgentLifecycleState.FAILED: [AgentLifecycleState.READY, AgentLifecycleState.TERMINATED],
            AgentLifecycleState.TERMINATED: [],
        }

        allowed = valid_transitions.get(self.current_state, [])
        if target_state not in allowed:
            logger.warning(f"Invalid lifecycle transition: {self.current_state} -> {target_state}")
            return False

        self.previous_state = self.current_state
        self.current_state = target_state
        return True
