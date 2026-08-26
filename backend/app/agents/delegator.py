import logging
from typing import Any

from app.agents.agent import Agent
from app.agents.exceptions import (
    AgentBudgetExhaustedError,
    AgentDelegationError,
    AgentPermissionDeniedError,
)
from app.agents.permissions import AgentPermission
from app.agents.status import AgentStatus
from app.agents.task import AgentTask, TaskStatus

logger = logging.getLogger("app.agents.delegator")


class DelegationManager:
    """Manages sub-task delegation from delegator agent to delegatee agent with depth & budget checking."""

    def __init__(self) -> None:
        pass

    def delegate_task(
        self,
        delegator: Agent,
        delegatee: Agent,
        task_title: str,
        inputs: dict[str, Any],
        current_depth: int = 1,
    ) -> AgentTask:
        # 1. Permission check
        if not delegator.has_permission(AgentPermission.CAN_DELEGATE):
            raise AgentPermissionDeniedError(
                f"Agent '{delegator.name}' lacks CAN_DELEGATE permission."
            )

        # 2. Budget & Delegation Depth check
        max_depth = delegator.definition.policy.budget.max_delegation_depth
        if current_depth > max_depth:
            raise AgentDelegationError(
                f"Delegation depth {current_depth} exceeds limit {max_depth} (delegation loop prevented)."
            )

        if delegator.is_budget_exhausted():
            raise AgentBudgetExhaustedError(
                f"Agent '{delegator.name}' has exhausted its execution budget."
            )

        # 3. Create subtask
        task = AgentTask(
            title=task_title,
            assigned_agent_id=delegatee.agent_id,
            inputs=inputs,
            status=TaskStatus.PENDING,
        )

        delegator.set_status(AgentStatus.DELEGATING)
        delegatee.set_status(AgentStatus.BUSY)
        logger.info(
            f"Agent '{delegator.name}' delegated '{task_title}' to '{delegatee.name}' (depth {current_depth})"
        )

        return task
