from pydantic import BaseModel, Field


class ToolPolicy(BaseModel):
    """Execution policy engine settings enforcing timeouts, retries, and concurrency limits."""

    timeout_seconds: float = Field(default=10.0, ge=0.1)
    max_retries: int = Field(default=0, ge=0)
    concurrency_limit: int = Field(default=10, ge=1)
    rate_limit_per_minute: int = Field(default=60, ge=1)
    allow_sandbox_eval: bool = True
