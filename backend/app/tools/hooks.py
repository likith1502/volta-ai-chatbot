from abc import ABC, abstractmethod
from app.tools.request import ToolRequest
from app.tools.result import ToolResult


class BeforeToolExecutionHook(ABC):
    @abstractmethod
    async def before_execution(self, request: ToolRequest) -> None:
        pass


class AfterToolExecutionHook(ABC):
    @abstractmethod
    async def after_execution(self, result: ToolResult) -> None:
        pass
