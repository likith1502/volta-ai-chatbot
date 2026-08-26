from pydantic import BaseModel, Field


class AgentExecutionBudget(BaseModel):
    """Resource budget and safety limits for agent execution turns."""

    max_runtime_ms: float = Field(default=30000.0, ge=100.0)
    max_retries: int = Field(default=3, ge=0)
    max_tool_calls: int = Field(default=10, ge=0)
    max_delegation_depth: int = Field(default=3, ge=0)
    max_tokens: int = Field(default=4096, ge=1)
    max_cost_usd: float = Field(default=1.0, ge=0.0)
    max_memory_items: int = Field(default=20, ge=1)

    # Usage counters
    current_runtime_ms: float = Field(default=0.0, ge=0.0)
    current_retries: int = Field(default=0, ge=0)
    current_tool_calls: int = Field(default=0, ge=0)
    current_delegation_depth: int = Field(default=0, ge=0)

    def is_exhausted(self) -> bool:
        """Returns True if any budget limit is exceeded."""
        if self.current_runtime_ms >= self.max_runtime_ms:
            return True
        if self.current_retries >= self.max_retries:
            return True
        if self.current_tool_calls >= self.max_tool_calls:
            return True
        if self.current_delegation_depth > self.max_delegation_depth:
            return True
        return False
