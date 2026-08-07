import time
from typing import Awaitable, Callable
from app.prompt.contracts import PromptRequest
from app.prompt.middleware.base import PromptMiddleware
from app.prompt.result import PromptResult


class OptimizationMiddleware(PromptMiddleware):
    """Pipeline middleware stage recording optimization stage latency."""

    async def process(
        self,
        request: PromptRequest,
        call_next: Callable[[PromptRequest], Awaitable[PromptResult]],
    ) -> PromptResult:
        t0 = time.perf_counter()
        result = await call_next(request)
        dt = (time.perf_counter() - t0) * 1000.0
        result.metrics.optimization_time_ms += dt
        result.trace.add_step("optimization", duration_ms=dt)
        return result
