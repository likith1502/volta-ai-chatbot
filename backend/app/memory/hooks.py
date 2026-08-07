from abc import ABC, abstractmethod
from app.memory.context import MemoryContext
from app.memory.contracts import MemoryRequest
from app.memory.memory import Memory


class BeforeCreateHook(ABC):
    @abstractmethod
    async def before_create(self, request: MemoryRequest) -> None:
        pass


class AfterCreateHook(ABC):
    @abstractmethod
    async def after_create(self, memory: Memory) -> None:
        pass


class BeforeSearchHook(ABC):
    @abstractmethod
    async def before_search(self, query: str) -> None:
        pass


class AfterSearchHook(ABC):
    @abstractmethod
    async def after_search(self, results: list[Memory]) -> None:
        pass


class BeforeCleanupHook(ABC):
    @abstractmethod
    async def before_cleanup(self) -> None:
        pass


class AfterCleanupHook(ABC):
    @abstractmethod
    async def after_cleanup(self, cleaned_count: int) -> None:
        pass


class BeforeContextBuildHook(ABC):
    @abstractmethod
    async def before_context_build(self) -> None:
        pass


class AfterContextBuildHook(ABC):
    @abstractmethod
    async def after_context_build(self, context: MemoryContext) -> None:
        pass
