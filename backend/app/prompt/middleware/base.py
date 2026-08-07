from abc import ABC, abstractmethod
from typing import Awaitable, Callable
from app.prompt.contracts import PromptRequest
from app.prompt.result import PromptResult


class PromptMiddleware(ABC):
    """Abstract middleware stage interface for prompt processing pipeline."""

    @abstractmethod
    async def process(
        self,
        request: PromptRequest,
        call_next: Callable[[PromptRequest], Awaitable[PromptResult]],
    ) -> PromptResult:
        """Processes prompt request through middleware stage."""
        pass


class PromptPipeline:
    """Configurable pipeline orchestrator executing registered PromptMiddleware stages in sequence."""

    def __init__(self, middlewares: list[PromptMiddleware]) -> None:
        self.middlewares = middlewares

    async def execute(
        self,
        request: PromptRequest,
        core_handler: Callable[[PromptRequest], Awaitable[PromptResult]],
    ) -> PromptResult:
        handler = core_handler
        for middleware in reversed(self.middlewares):
            current_fn = handler
            current_mw = middleware

            async def _mw_wrapper(r: PromptRequest, mw=current_mw, fn=current_fn) -> PromptResult:
                return await mw.process(r, fn)

            handler = _mw_wrapper

        return await handler(request)
