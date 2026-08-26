from abc import ABC, abstractmethod

from app.memory.compactor import MemoryCompactor
from app.memory.context import MemoryContext
from app.memory.memory import Memory
from app.memory.selector import MemorySelector
from app.memory.token_estimator import MemoryTokenEstimator
from app.memory.types import MemoryType


class ContextAssemblyStrategy(ABC):
    """Abstract Base Class defining context assembly strategy interface."""

    @abstractmethod
    def assemble(
        self, memories: list[Memory], token_budget: int = 4000
    ) -> MemoryContext:
        """Assembles list of Memory objects into MemoryContext within token budget."""
        pass


class HybridStrategy(ContextAssemblyStrategy):
    """Default hybrid assembly strategy combining recency, importance, and token budgeting."""

    def __init__(self) -> None:
        self.selector = MemorySelector()
        self.compactor = MemoryCompactor()

    def assemble(
        self, memories: list[Memory], token_budget: int = 4000
    ) -> MemoryContext:
        compacted = self.compactor.compact(memories, token_budget=token_budget)
        selected = self.selector.select(compacted, strategy="hybrid", top_k=50)

        sys_mems = [m for m in selected if m.memory_type == MemoryType.SYSTEM]
        user_mems = [
            m
            for m in selected
            if m.memory_type
            in (MemoryType.USER, MemoryType.LONG_TERM, MemoryType.SEMANTIC)
        ]
        conv_mems = [
            m
            for m in selected
            if m.memory_type
            in (MemoryType.SHORT_TERM, MemoryType.EPISODIC, MemoryType.SESSION)
        ]
        work_mems = [m for m in selected if m.memory_type == MemoryType.WORKING]

        ctx = MemoryContext(
            conversation_id=memories[0].conversation_id if memories else None,
            system_memories=sys_mems,
            conversation_memories=conv_mems,
            working_memories=work_mems,
            user_memories=user_mems,
            total_memories_count=len(selected),
            strategy_used="hybrid",
        )
        ctx.total_token_estimate = MemoryTokenEstimator.estimate_context_tokens(ctx)
        return ctx


class RecentStrategy(ContextAssemblyStrategy):
    """Assembly strategy prioritizing recent short-term memories."""

    def assemble(
        self, memories: list[Memory], token_budget: int = 4000
    ) -> MemoryContext:
        sorted_mems = sorted(memories, key=lambda m: m.created_at, reverse=True)
        compacted = MemoryCompactor().compact(sorted_mems, token_budget=token_budget)

        ctx = MemoryContext(
            conversation_id=memories[0].conversation_id if memories else None,
            conversation_memories=compacted,
            total_memories_count=len(compacted),
            strategy_used="recent",
        )
        ctx.total_token_estimate = MemoryTokenEstimator.estimate_context_tokens(ctx)
        return ctx


class ImportanceStrategy(ContextAssemblyStrategy):
    """Assembly strategy prioritizing high-importance and pinned memories."""

    def assemble(
        self, memories: list[Memory], token_budget: int = 4000
    ) -> MemoryContext:
        sorted_mems = sorted(
            memories, key=lambda m: (m.is_pinned, m.importance), reverse=True
        )
        compacted = MemoryCompactor().compact(sorted_mems, token_budget=token_budget)

        ctx = MemoryContext(
            conversation_id=memories[0].conversation_id if memories else None,
            user_memories=compacted,
            total_memories_count=len(compacted),
            strategy_used="importance",
        )
        ctx.total_token_estimate = MemoryTokenEstimator.estimate_context_tokens(ctx)
        return ctx


class SlidingWindowStrategy(ContextAssemblyStrategy):
    """Assembly strategy maintaining a fixed sliding window of the last N turns."""

    def assemble(
        self, memories: list[Memory], token_budget: int = 4000
    ) -> MemoryContext:
        recent_window = sorted(memories, key=lambda m: m.created_at, reverse=True)[:20]
        compacted = MemoryCompactor().compact(recent_window, token_budget=token_budget)

        ctx = MemoryContext(
            conversation_id=memories[0].conversation_id if memories else None,
            conversation_memories=compacted,
            total_memories_count=len(compacted),
            strategy_used="sliding_window",
        )
        ctx.total_token_estimate = MemoryTokenEstimator.estimate_context_tokens(ctx)
        return ctx
