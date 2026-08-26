from abc import ABC, abstractmethod
from typing import Any

from app.graph_runtime.context import GraphRuntimeContext


class GraphRuntimeMiddleware(ABC):
    """Abstract Middleware interface for Graph Runtime execution pipeline."""

    @abstractmethod
    async def process(
        self, context: GraphRuntimeContext, next_handler: Any
    ) -> GraphRuntimeContext:
        """Processes runtime context and calls next_handler."""
        pass


class GraphRuntimePipeline:
    """Sequential pipeline executing: Validation -> Auth -> Memory -> Tool -> Prompt -> Runtime -> Checkpoint -> Stream -> Events."""

    def __init__(self, middlewares: list[GraphRuntimeMiddleware] = None) -> None:
        self.middlewares = middlewares or []

    def add_middleware(self, middleware: GraphRuntimeMiddleware) -> None:
        self.middlewares.append(middleware)

    async def execute_pipeline(
        self, context: GraphRuntimeContext
    ) -> GraphRuntimeContext:
        async def _chain(index: int, ctx: GraphRuntimeContext) -> GraphRuntimeContext:
            if index >= len(self.middlewares):
                return ctx
            mw = self.middlewares[index]
            return await mw.process(ctx, lambda c: _chain(index + 1, c))

        return await _chain(0, context)
