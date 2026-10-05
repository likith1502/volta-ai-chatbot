from abc import ABC, abstractmethod


class RetryPolicy(ABC):
    """Abstract retry strategy interface for adapter execution calls."""

    @abstractmethod
    def should_retry(self, attempt: int, exception: Exception) -> bool:
        pass

    @abstractmethod
    def get_delay_seconds(self, attempt: int) -> float:
        pass


class NoRetry(RetryPolicy):
    def should_retry(self, attempt: int, exception: Exception) -> bool:
        return False

    def get_delay_seconds(self, attempt: int) -> float:
        return 0.0


class LinearBackoff(RetryPolicy):
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0) -> None:
        self.max_attempts = max_attempts
        self.base_delay = base_delay

    def should_retry(self, attempt: int, exception: Exception) -> bool:
        return attempt < self.max_attempts

    def get_delay_seconds(self, attempt: int) -> float:
        return self.base_delay * attempt


class ExponentialBackoff(RetryPolicy):
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, factor: float = 2.0) -> None:
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.factor = factor

    def should_retry(self, attempt: int, exception: Exception) -> bool:
        return attempt < self.max_attempts

    def get_delay_seconds(self, attempt: int) -> float:
        return self.base_delay * (self.factor ** (attempt - 1))


class CircuitBreaker(RetryPolicy):
    """Circuit breaker pattern preventing cascading adapter failures."""

    def __init__(self, failure_threshold: int = 5, recovery_time_seconds: float = 30.0) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_time_seconds = recovery_time_seconds
        self.failure_count = 0
        self.is_open = False

    def record_failure() -> None:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.is_open = True

    def record_success() -> None:
        self.failure_count = 0
        self.is_open = False

    def should_retry(self, attempt: int, exception: Exception) -> bool:
        return not self.is_open and attempt < 3

    def get_delay_seconds(self, attempt: int) -> float:
        return 1.0
