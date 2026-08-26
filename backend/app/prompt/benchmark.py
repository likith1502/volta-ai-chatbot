import time

from pydantic import BaseModel

from app.prompt.contracts import PromptRequest


class PromptBenchmarkResult(BaseModel):
    """Benchmark performance report across N execution iterations."""

    iterations: int
    average_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    total_tokens_used: int
    estimated_total_cost_usd: float
    success_rate_pct: float = 100.0


class PromptBenchmarkRunner:
    """Executes benchmark iterations for prompt templates to measure performance and latency distribution."""

    def __init__(self, prompt_manager) -> None:
        self.prompt_manager = prompt_manager

    async def benchmark(
        self, request: PromptRequest, iterations: int = 5
    ) -> PromptBenchmarkResult:
        latencies: list[float] = []
        tokens = 0
        cost = 0.0
        successes = 0

        for _ in range(iterations):
            t0 = time.perf_counter()
            try:
                res = await self.prompt_manager.render(request)
                dt = (time.perf_counter() - t0) * 1000.0
                latencies.append(dt)
                tokens += res.metrics.token_estimate
                successes += 1
            except Exception:
                pass

        avg_lat = (sum(latencies) / len(latencies)) if latencies else 0.0
        min_lat = min(latencies) if latencies else 0.0
        max_lat = max(latencies) if latencies else 0.0
        success_pct = (successes / iterations) * 100.0 if iterations > 0 else 0.0

        return PromptBenchmarkResult(
            iterations=iterations,
            average_latency_ms=avg_lat,
            min_latency_ms=min_lat,
            max_latency_ms=max_lat,
            total_tokens_used=tokens,
            estimated_total_cost_usd=cost,
            success_rate_pct=success_pct,
        )
