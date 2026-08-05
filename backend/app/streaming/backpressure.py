from pydantic import BaseModel

from app.streaming.stream_types import OverflowStrategy


class BackpressurePolicy(BaseModel):
    """Configuration governing queue limits and overflow strategies under high load."""

    max_queue_size: int = 1000
    overflow_strategy: OverflowStrategy = OverflowStrategy.DROP_OLDEST
    drop_policy: str = "oldest"
    timeout: float = 5.0
