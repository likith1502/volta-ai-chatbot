from pydantic import BaseModel, Field


class MemoryCostEstimate(BaseModel):
    """Cost estimation breakdown for memory storage and retrieval operations."""

    memory_count: int = Field(default=0, ge=0)
    total_token_count: int = Field(default=0, ge=0)
    estimated_storage_bytes: int = Field(default=0, ge=0)
    monthly_retrieval_cost_usd: float = Field(default=0.0, ge=0.0)


class MemoryCostEstimator:
    """Estimates storage and retrieval costs for memory objects."""

    @staticmethod
    def estimate(memory_count: int, total_tokens: int) -> MemoryCostEstimate:
        storage_bytes = total_tokens * 4
        cost_usd = (total_tokens / 1000.0) * 0.00001
        return MemoryCostEstimate(
            memory_count=memory_count,
            total_token_count=total_tokens,
            estimated_storage_bytes=storage_bytes,
            monthly_retrieval_cost_usd=cost_usd,
        )
