from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class BackoffStrategy(str, Enum):
    """Backoff delay calculation strategy for retries."""

    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"
    NEVER = "never"


class RetryDecision(BaseModel):
    """Output decision indicating if an operation should be retried."""

    should_retry: bool
    delay_seconds: float = 0.0
    attempt_number: int = 1
    reason: Optional[str] = None


class RetryPolicy(BaseModel):
    """Configurable retry policy for Graph Runtime nodes."""

    max_retries: int = Field(default=3, ge=0)
    initial_delay_seconds: float = Field(default=1.0, ge=0.0)
    backoff_strategy: BackoffStrategy = Field(default=BackoffStrategy.EXPONENTIAL)
    backoff_factor: float = Field(default=2.0, ge=1.0)
    retryable_exceptions: list[str] = Field(default_factory=list)

    def evaluate(self, attempt: int, exception: Optional[Exception] = None) -> RetryDecision:
        if attempt >= self.max_retries or self.backoff_strategy == BackoffStrategy.NEVER:
            return RetryDecision(should_retry=False, attempt_number=attempt, reason="Max retries reached")

        if self.backoff_strategy == BackoffStrategy.FIXED:
            delay = self.initial_delay_seconds
        elif self.backoff_strategy == BackoffStrategy.LINEAR:
            delay = self.initial_delay_seconds * (attempt + 1)
        else:  # EXPONENTIAL
            delay = self.initial_delay_seconds * (self.backoff_factor ** attempt)

        return RetryDecision(
            should_retry=True,
            delay_seconds=round(delay, 2),
            attempt_number=attempt + 1,
            reason=f"Retry attempt {attempt + 1}",
        )
