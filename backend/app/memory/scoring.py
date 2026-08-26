from datetime import datetime, timezone

from app.memory.memory import Memory


class MemoryScorer:
    """Computes retrieval scores for memory elements using recency, importance, frequency, and manual boosts."""

    def __init__(
        self,
        recency_weight: float = 0.4,
        importance_weight: float = 0.4,
        frequency_weight: float = 0.2,
    ) -> None:
        self.recency_weight = recency_weight
        self.importance_weight = importance_weight
        self.frequency_weight = frequency_weight

    def score(self, memory: Memory, now: datetime = None) -> float:
        now = now or datetime.now(timezone.utc)

        # 1. Pinned memories receive maximum boost
        if memory.is_pinned:
            return 1.0

        # 2. Recency score (decay over seconds)
        age_seconds = max(0.0, (now - memory.created_at).total_seconds())
        recency_score = 1.0 / (1.0 + (age_seconds / 86400.0))  # 1-day half-life decay

        # 3. Importance score
        importance_score = memory.importance

        # 4. Frequency score
        access_count = memory.metadata.access_count
        frequency_score = min(1.0, access_count / 10.0)

        composite = (
            (self.recency_weight * recency_score)
            + (self.importance_weight * importance_score)
            + (self.frequency_weight * frequency_score)
        )
        return round(min(1.0, max(0.0, composite)), 4)
