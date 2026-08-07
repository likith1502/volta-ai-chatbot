from pydantic import BaseModel, Field


class ContextWindowBudget(BaseModel):
    """Tracks token budget allocations for runtime model context windows."""

    max_model_tokens: int = Field(default=128000, description="Total token limit of the target model")
    reserved_system_tokens: int = Field(default=2000, ge=0)
    reserved_completion_tokens: int = Field(default=1000, ge=0)
    memory_token_budget: int = Field(default=4000, ge=100)
    current_memory_tokens: int = Field(default=0, ge=0)

    @property
    def available_prompt_tokens(self) -> int:
        return max(0, self.max_model_tokens - self.reserved_system_tokens - self.reserved_completion_tokens - self.current_memory_tokens)

    @property
    def is_over_budget(self) -> bool:
        return self.current_memory_tokens > self.memory_token_budget
