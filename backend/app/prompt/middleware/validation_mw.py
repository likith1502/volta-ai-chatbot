import time
from typing import Awaitable, Callable

from app.prompt.contracts import PromptRequest
from app.prompt.exceptions import PromptValidationError
from app.prompt.middleware.base import PromptMiddleware
from app.prompt.result import PromptResult


class ValidationMiddleware(PromptMiddleware):
    """Pipeline middleware stage validating request structure and template ID."""

    async def process(
        self,
        request: PromptRequest,
        call_next: Callable[[PromptRequest], Awaitable[PromptResult]],
    ) -> PromptResult:
        t0 = time.perf_counter()
        if not request.template_id or not request.template_id.strip():
            raise PromptValidationError(
                "PromptRequest must specify a valid non-empty 'template_id'."
            )

        result = await call_next(request)
        dt = (time.perf_counter() - t0) * 1000.0
        result.metrics.validation_time_ms += dt
        result.trace.add_step("validation", duration_ms=dt)
        return result
