import time
from typing import Awaitable, Callable

from app.runtime.contracts import RuntimeRequest
from app.runtime.middleware.base import RuntimeMiddleware
from app.runtime.result import RuntimeResult


class MetricsMiddleware(RuntimeMiddleware):
    """Runtime middleware measuring wall-clock execution latency and calculating telemetry metrics."""

    async def process(
        self,
        request: RuntimeRequest,
        call_next: Callable[[RuntimeRequest], Awaitable[RuntimeResult]],
    ) -> RuntimeResult:
        start_time = time.perf_counter()
        result = await call_next(request)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        result.metrics.total_execution_time_ms = elapsed_ms
        if result.metrics.latency_ms == 0.0:
            result.metrics.latency_ms = elapsed_ms
        return result
