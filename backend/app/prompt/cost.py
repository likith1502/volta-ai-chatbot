from pydantic import BaseModel, Field


class PromptCostEstimate(BaseModel):
    """Detailed cost calculation breakdown per request and projected monthly usage."""

    provider: str
    model: str
    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)
    estimated_request_cost_usd: float = Field(default=0.0, ge=0.0)
    projected_monthly_cost_usd: float = Field(default=0.0, ge=0.0, description="Based on 10,000 monthly request turns")


class PromptCostEstimator:
    """Estimates LLM request costs across registered models and providers."""

    @staticmethod
    def estimate(
        prompt_tokens: int,
        completion_tokens: int = 150,
        provider: str = "gemini",
        model: str = "gemini-2.5-flash",
    ) -> PromptCostEstimate:
        prov = provider.lower().strip()
        mod = model.lower().strip()

        # Rates per 1,000 tokens
        if "flash" in mod:
            input_rate = 0.000075
            output_rate = 0.0003
        elif "pro" in mod:
            input_rate = 0.00125
            output_rate = 0.005
        else:
            input_rate = 0.0001
            output_rate = 0.0004

        req_cost = ((prompt_tokens / 1000.0) * input_rate) + ((completion_tokens / 1000.0) * output_rate)
        monthly_cost = req_cost * 10000.0

        return PromptCostEstimate(
            provider=prov,
            model=mod,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_request_cost_usd=req_cost,
            projected_monthly_cost_usd=monthly_cost,
        )
