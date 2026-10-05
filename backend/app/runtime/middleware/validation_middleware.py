from typing import Awaitable, Callable
from app.runtime.contracts import RuntimeRequest
from app.runtime.exceptions import ProviderConfigurationError
from app.runtime.middleware.base import RuntimeMiddleware
from app.runtime.result import RuntimeResult


class ValidationMiddleware(RuntimeMiddleware):
    """Runtime middleware validating request payload structure and message role constraints."""

    async def process(
        self,
        request: RuntimeRequest,
        call_next: Callable[[RuntimeRequest], Awaitable[RuntimeResult]],
    ) -> RuntimeResult:
        if not request.messages:
            raise ProviderConfigurationError("RuntimeRequest must contain at least one ChatMessage.")

        for idx, msg in enumerate(request.messages):
            if not msg.content or not msg.content.strip():
                raise ProviderConfigurationError(f"ChatMessage at index {idx} contains empty content payload.")

        return await call_next(request)
