import logging
from typing import Any, Optional
from app.agents.agent import Agent
from app.agents.definition import AgentDefinition
from app.agents.identity import AgentIdentity
from app.agents.permissions import AgentPermission
from app.agents.role import AgentRole
from app.agents.task import TaskResult, TaskStatus

logger = logging.getLogger("app.agents.supervisor")


class SupervisorAgent(Agent):
    """Specialized Agent overseeing multi-agent team execution, task assignment, and output validation."""

    def __init__(self, definition: Optional[AgentDefinition] = None) -> None:
        def_obj = definition or AgentDefinition(
            identity=AgentIdentity(name="Supervisor Agent"),
            role=AgentRole.SUPERVISOR,
        )
        def_obj.policy.permissions.grant(AgentPermission.CAN_SUPERVISE)
        def_obj.policy.permissions.grant(AgentPermission.CAN_APPROVE)
        def_obj.policy.permissions.grant(AgentPermission.CAN_DELEGATE)
        super().__init__(definition=def_obj)

    def validate_worker_results(self, results: list[TaskResult]) -> bool:
        """Validates worker results and checks for execution errors."""
        for r in results:
            if r.status != TaskStatus.COMPLETED:
                logger.warning(f"Supervisor found failed worker task: '{r.task_id}'")
                return False
        return True

    def synthesize_final_response(self, results: list[TaskResult]) -> dict[str, Any]:
        """Synthesizes final response output from completed worker results."""
        summary_items = []
        for r in results:
            summary_items.append(f"Task '{r.task_id}' by '{r.assigned_agent_id}': OK")

        return {
            "status": "success",
            "supervisor": self.name,
            "tasks_processed": len(results),
            "summary": summary_items,
            "final_answer": "Multi-agent team workflow completed successfully.",
        }
