from abc import ABC, abstractmethod

from app.prompt.contracts import PromptRequest, PromptResponse
from app.prompt.result import PromptResult


class PreRenderHook(ABC):
    """Hook contract executed before template rendering."""

    @abstractmethod
    async def pre_render(self, request: PromptRequest) -> None:
        pass


class PostRenderHook(ABC):
    """Hook contract executed after template rendering and optimization."""

    @abstractmethod
    async def post_render(self, response: PromptResponse) -> None:
        pass


class PreExecutionHook(ABC):
    """Hook contract executed before passing prompt to RuntimeManager."""

    @abstractmethod
    async def pre_execution(self, result: PromptResult) -> None:
        pass


class PostExecutionHook(ABC):
    """Hook contract executed after RuntimeManager completes LLM generation."""

    @abstractmethod
    async def post_execution(self, result: PromptResult) -> None:
        pass
