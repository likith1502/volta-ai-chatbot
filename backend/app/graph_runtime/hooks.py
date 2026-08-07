from abc import ABC, abstractmethod
from app.graph_runtime.context import GraphRuntimeContext
from app.graph_runtime.execution_result import GraphExecutionResult


class BeforeGraphExecutionHook(ABC):
    @abstractmethod
    async def before_execution(self, context: GraphRuntimeContext) -> None:
        pass


class AfterGraphExecutionHook(ABC):
    @abstractmethod
    async def after_execution(self, result: GraphExecutionResult) -> None:
        pass
