import logging
from typing import Awaitable, Callable

from app.runtime.contracts import RuntimeRequest
from app.runtime.middleware.base import RuntimeMiddleware
from app.runtime.result import RuntimeResult

logger = logging.getLogger("app.runtime.middleware.logging")


class LoggingMiddleware(RuntimeMiddleware):
    """Runtime middleware logging execution start, provider selection, and latency/status."""

    async def process(
        self,
        request: RuntimeRequest,
        call_next: Callable[[RuntimeRequest], Awaitable[RuntimeResult]],
    ) -> RuntimeResult:
        logger.info(
            f"Starting runtime execution request '{request.request_id}' (Provider: {request.provider})"
        )
        result = await call_next(request)
        logger.info(
            f"Completed runtime execution request '{request.request_id}' "
            f"[Status: {result.execution_status}, Latency: {result.metrics.latency_ms:.2f}ms, Tokens: {result.metrics.tokens.total_tokens}]"
        )
        return result
