import logging
from typing import Optional

from app.agents.task import AgentTask, TaskStatus

logger = logging.getLogger("app.agents.task_queue")


class TaskQueue:
    """Priority task queue managing task assignment and backlog."""

    def __init__(self) -> None:
        self._queue: list[AgentTask] = []
        self._completed: dict[str, AgentTask] = {}

    def enqueue(self, task: AgentTask) -> None:
        self._queue.append(task)
        # Sort by priority descending
        self._queue.sort(key=lambda t: t.priority, reverse=True)
        logger.debug(f"Enqueued task '{task.task_id}' with priority {task.priority}")

    def dequeue(self) -> Optional[AgentTask]:
        if self._queue:
            return self._queue.pop(0)
        return None

    def mark_completed(self, task: AgentTask) -> None:
        task.status = TaskStatus.COMPLETED
        self._completed[task.task_id] = task

    def list_pending(self) -> list[AgentTask]:
        return list(self._queue)

    def list_completed(self) -> list[AgentTask]:
        return list(self._completed.values())
