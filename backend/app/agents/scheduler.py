import logging
from typing import Optional

from app.agents.agent import Agent
from app.agents.status import AgentStatus
from app.agents.strategy import SchedulingStrategy
from app.agents.task import AgentTask
from app.agents.task_queue import TaskQueue

logger = logging.getLogger("app.agents.scheduler")


class TaskScheduler:
    """Dispatches queued tasks to available agents based on scheduling strategy."""

    def __init__(self, task_queue: Optional[TaskQueue] = None) -> None:
        self.task_queue = task_queue or TaskQueue()

    def schedule_next(
        self,
        available_agents: list[Agent],
        strategy: SchedulingStrategy = SchedulingStrategy.PRIORITY_FIRST,
    ) -> Optional[tuple[AgentTask, Agent]]:
        task = self.task_queue.dequeue()
        if not task:
            return None

        idle_agents = [a for a in available_agents if a.status == AgentStatus.IDLE]
        if not idle_agents:
            # Re-enqueue if no agent available
            self.task_queue.enqueue(task)
            return None

        target_agent = idle_agents[0]
        task.assigned_agent_id = target_agent.agent_id
        target_agent.set_status(AgentStatus.BUSY)
        logger.info(f"Task '{task.task_id}' scheduled to Agent '{target_agent.name}'")
        return task, target_agent
