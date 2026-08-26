import time
from typing import Awaitable, Callable, Optional

from app.prompt.contracts import PromptRequest
from app.prompt.exceptions import PromptSecurityViolationError
from app.prompt.middleware.base import PromptMiddleware
from app.prompt.result import PromptResult
from app.prompt.security import PromptSecurityPolicy


class SecurityMiddleware(PromptMiddleware):
    """Pipeline middleware stage inspecting variable inputs for security policy violations."""

    def __init__(self, policy: Optional[PromptSecurityPolicy] = None) -> None:
        self.policy = policy or PromptSecurityPolicy()

    async def process(
        self,
        request: PromptRequest,
        call_next: Callable[[PromptRequest], Awaitable[PromptResult]],
    ) -> PromptResult:
        t0 = time.perf_counter()
        for k, v in request.variables.items():
            if not self.policy.validate_variable_name(k):
                raise PromptSecurityViolationError(
                    f"Restricted variable name '{k}' is forbidden by security policy."
                )
            if isinstance(v, str):
                violation = self.policy.detect_injection(v)
                if violation:
                    raise PromptSecurityViolationError(violation)

        result = await call_next(request)
        dt = (time.perf_counter() - t0) * 1000.0
        result.trace.add_step("security", duration_ms=dt)
        return result
