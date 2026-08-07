from abc import ABC, abstractmethod
from app.agents.agent import Agent
from app.agents.task import AgentTask, TaskResult


class BeforeAgentExecutionHook(ABC):
    @abstractmethod
    async def before_execution(self, agent: Agent, task: AgentTask) -> None:
        pass


class AfterAgentExecutionHook(ABC):
    @abstractmethod
    async def after_execution(self, agent: Agent, result: TaskResult) -> None:
        pass
