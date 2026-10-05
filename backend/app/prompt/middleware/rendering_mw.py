import time
from typing import Awaitable, Callable
from app.prompt.contracts import PromptRequest
from app.prompt.middleware.base import PromptMiddleware
from app.prompt.result import PromptResult


class RenderingMiddleware(PromptMiddleware):
    """Pipeline middleware stage recording rendering stage latency."""

    async def process(
        self,
        request: PromptRequest,
        call_next: Callable[[PromptRequest], Awaitable[PromptResult]],
    ) -> PromptResult:
        t0 = time.perf_counter()
        result = await call_next(request)
        dt = (time.perf_counter() - t0) * 1000.0
        result.metrics.render_time_ms += dt
        result.trace.add_step("rendering", duration_ms=dt)
        return result
