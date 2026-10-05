from typing import Union
from app.memory.context import MemoryContext
from app.memory.memory import Memory


class MemoryTokenEstimator:
    """Estimates token usage for individual memories, memory lists, and assembled MemoryContext objects."""

    @staticmethod
    def estimate_memory_tokens(memory: Memory) -> int:
        """Estimates token count for a single Memory object."""
        char_count = len(memory.content)
        return max(1, char_count // 4)

    @staticmethod
    def estimate_list_tokens(memories: list[Memory]) -> int:
        """Estimates token count for a list of Memory objects."""
        return sum(MemoryTokenEstimator.estimate_memory_tokens(m) for m in memories)

    @staticmethod
    def estimate_context_tokens(context: MemoryContext) -> int:
        """Estimates total token count for assembled MemoryContext."""
        formatted_text = context.format_as_text()
        return max(1, len(formatted_text) // 4)
