import logging
from typing import Any, Optional
from app.agents.agent import Agent
from app.agents.definition import AgentDefinition
from app.agents.identity import AgentIdentity
from app.agents.role import AgentRole
from app.agents.task import AgentTask

logger = logging.getLogger("app.agents.planner")


class PlannerAgent(Agent):
    """Specialized Agent responsible for task decomposition and execution planning."""

    def __init__(self, definition: Optional[AgentDefinition] = None) -> None:
        def_obj = definition or AgentDefinition(
            identity=AgentIdentity(name="Planner Agent"),
            role=AgentRole.PLANNER,
        )
        super().__init__(definition=def_obj)

    def plan_task(self, goal: str, inputs: dict[str, Any]) -> list[AgentTask]:
        """Decomposes high-level goal into structured sub-tasks."""
        t1 = AgentTask(title="research_goal", description=f"Gather research for: {goal}", priority=2, inputs=inputs)
        t2 = AgentTask(title="execute_tools", description=f"Execute required tools for: {goal}", priority=1, inputs=inputs)
        t3 = AgentTask(title="synthesize_results", description=f"Synthesize output for: {goal}", priority=1, inputs=inputs)

        t2.parent_task_id = t1.task_id
        t3.parent_task_id = t2.task_id

        logger.info(f"PlannerAgent decomposed goal '{goal}' into 3 tasks.")
        return [t1, t2, t3]
