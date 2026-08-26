from app.memory.memory import Memory
from app.memory.token_estimator import MemoryTokenEstimator


class MemoryCompactor:
    """Performs non-AI deduplication, whitespace trimming, and token truncation to fit context window budget."""

    def compact(self, memories: list[Memory], token_budget: int = 4000) -> list[Memory]:
        if not memories:
            return []

        # 1. Deduplicate identical content
        seen_content = set()
        deduped: list[Memory] = []
        for m in memories:
            norm = m.content.strip().lower()
            if norm not in seen_content:
                seen_content.add(norm)
                deduped.append(m)

        # 2. Truncate list to fit token budget
        compacted: list[Memory] = []
        accumulated_tokens = 0
        for m in deduped:
            tokens = MemoryTokenEstimator.estimate_memory_tokens(m)
            if accumulated_tokens + tokens <= token_budget or m.is_pinned:
                compacted.append(m)
                accumulated_tokens += tokens

        return compacted
