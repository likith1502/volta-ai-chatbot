import time
from typing import Awaitable, Callable

from app.prompt.contracts import PromptRequest
from app.prompt.middleware.base import PromptMiddleware
from app.prompt.result import PromptResult


class VariableInjectionMiddleware(PromptMiddleware):
    """Pipeline middleware stage injecting default and context variables."""

    async def process(
        self,
        request: PromptRequest,
        call_next: Callable[[PromptRequest], Awaitable[PromptResult]],
    ) -> PromptResult:
        t0 = time.perf_counter()
        # Ensure default metadata variables
        if "environment" not in request.variables:
            request.variables["environment"] = "development"

        result = await call_next(request)
        dt = (time.perf_counter() - t0) * 1000.0
        result.trace.add_step("injection", duration_ms=dt)
        return result
