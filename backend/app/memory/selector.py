from app.memory.memory import Memory
from app.memory.scoring import MemoryScorer


class MemorySelector:
    """Selects top memories using specified selection strategies (TopK, Recent, Importance, Hybrid)."""

    def __init__(self, scorer: MemoryScorer = None) -> None:
        self.scorer = scorer or MemoryScorer()

    def select(self, memories: list[Memory], strategy: str = "hybrid", top_k: int = 10) -> list[Memory]:
        if not memories:
            return []

        strat = strategy.lower().strip()
        if strat == "recent":
            sorted_mems = sorted(memories, key=lambda m: m.created_at, reverse=True)
        elif strat == "importance":
            sorted_mems = sorted(memories, key=lambda m: (m.is_pinned, m.importance), reverse=True)
        else:  # hybrid or sliding_window
            sorted_mems = sorted(memories, key=lambda m: self.scorer.score(m), reverse=True)

        return sorted_mems[:top_k]
