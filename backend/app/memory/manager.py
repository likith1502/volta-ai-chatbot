import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.events.event import WorkflowEvent
from app.events.event_bus import WorkflowEventBus
from app.memory.analytics import MemoryAnalyticsManager
from app.memory.config import MemoryConfiguration
from app.memory.context import MemoryContext
from app.memory.context_builder import MemoryContextBuilder
from app.memory.contracts import MemoryRequest, MemorySearchResult
from app.memory.exceptions import MemoryNotFoundError, MemoryValidationError
from app.memory.health import MemoryHealthManager
from app.memory.lifecycle import MemoryLifecycleManager, MemoryLifecycleState
from app.memory.memory import Memory
from app.memory.metadata import MemoryMetadata
from app.memory.metrics import MemoryMetrics
from app.memory.policy import MemoryPolicy
from app.memory.registry import MemoryRegistry
from app.memory.scoring import MemoryScorer
from app.memory.selector import MemorySelector
from app.memory.statistics import MemoryStatistics
from app.memory.status import MemoryStatus
from app.memory.strategy import ContextAssemblyStrategy, HybridStrategy, ImportanceStrategy, RecentStrategy, SlidingWindowStrategy
from app.memory.token_estimator import MemoryTokenEstimator

logger = logging.getLogger("app.memory.manager")


class MemoryManager:
    """Central orchestrator for the Enterprise Memory Runtime handling memory CRUD, search, lifecycle state transitions, context assembly, and event bus notification dispatch."""

    def __init__(
        self,
        registry: Optional[MemoryRegistry] = None,
        config: Optional[MemoryConfiguration] = None,
        event_bus: Optional[WorkflowEventBus] = None,
    ) -> None:
        self.config = config or MemoryConfiguration()
        self.registry = registry or MemoryRegistry()
        self.event_bus = event_bus or WorkflowEventBus()

        self.policy = MemoryPolicy()
        self.scorer = MemoryScorer()
        self.selector = MemorySelector(scorer=self.scorer)
        self.builder = MemoryContextBuilder()
        self.health_manager = MemoryHealthManager(self.registry)
        self.analytics_manager = MemoryAnalyticsManager()
        self.metrics = MemoryMetrics()

    async def _emit_event(self, event_name: str, payload: dict) -> None:
        """Publishes event to Phase 6.5 WorkflowEventBus."""
        try:
            event = WorkflowEvent(
                event_name=f"memory.{event_name}",
                payload=payload,
                source="memory_manager",
            )
            await self.event_bus.publish(event)
        except Exception as exc:
            logger.debug(f"Memory event emission notice: {exc}")

    async def create_memory(self, request: MemoryRequest) -> Memory:
        """Creates and stores a new Memory instance."""
        if not request.content or not request.content.strip():
            raise MemoryValidationError("Memory content cannot be empty.")

        expires_at = None
        if request.ttl_seconds:
            expires_at = datetime.fromtimestamp(time.time() + request.ttl_seconds, tz=timezone.utc)

        metadata = MemoryMetadata(
            tags=request.tags,
            custom_attributes=request.custom_attributes,
        )

        memory = Memory(
            conversation_id=request.conversation_id,
            execution_id=request.execution_id,
            memory_type=request.memory_type,
            status=MemoryStatus.ACTIVE,
            content=request.content.strip(),
            importance=request.importance,
            expires_at=expires_at,
            metadata=metadata,
        )

        repo = self.registry.get_repository()
        await repo.save(memory)
        self.metrics.memory_count += 1

        await self._emit_event("created", {
            "memory_id": str(memory.memory_id),
            "conversation_id": str(memory.conversation_id) if memory.conversation_id else None,
            "memory_type": memory.memory_type.value,
        })
        return memory

    async def get_memory(self, memory_id: uuid.UUID) -> Memory:
        """Retrieves memory by ID or raises MemoryNotFoundError."""
        repo = self.registry.get_repository()
        memory = await repo.get_by_id(memory_id)
        if not memory:
            raise MemoryNotFoundError(f"Memory with ID '{memory_id}' not found.")
        return memory

    async def pin_memory(self, memory_id: uuid.UUID) -> Memory:
        """Pins a memory entry to prevent expiration or eviction."""
        memory = await self.get_memory(memory_id)
        MemoryLifecycleManager.validate_transition(memory.status, MemoryStatus.PINNED)
        memory.status = MemoryStatus.PINNED
        await self.registry.get_repository().save(memory)
        await self._emit_event("pinned", {"memory_id": str(memory_id)})
        return memory

    async def unpin_memory(self, memory_id: uuid.UUID) -> Memory:
        """Unpins a memory entry."""
        memory = await self.get_memory(memory_id)
        if memory.status == MemoryStatus.PINNED:
            memory.status = MemoryStatus.ACTIVE
            await self.registry.get_repository().save(memory)
        return memory

    async def archive_memory(self, memory_id: uuid.UUID) -> Memory:
        """Archives a memory entry."""
        memory = await self.get_memory(memory_id)
        MemoryLifecycleManager.validate_transition(memory.status, MemoryStatus.ARCHIVED)
        memory.status = MemoryStatus.ARCHIVED
        await self.registry.get_repository().save(memory)
        await self._emit_event("archived", {"memory_id": str(memory_id)})
        return memory

    async def delete_memory(self, memory_id: uuid.UUID) -> bool:
        """Deletes a memory entry."""
        repo = self.registry.get_repository()
        mem = await repo.get_by_id(memory_id)
        if mem:
            MemoryLifecycleManager.validate_transition(mem.status, MemoryStatus.DELETED)
            res = await repo.delete(memory_id)
            if res:
                await self._emit_event("deleted", {"memory_id": str(memory_id)})
                return True
        return False

    async def search_memories(
        self,
        query: str = "",
        conversation_id: Optional[uuid.UUID] = None,
        strategy: str = "hybrid",
        limit: int = 10,
    ) -> MemorySearchResult:
        """Searches and scores stored memories matching conversation criteria."""
        t0 = time.perf_counter()
        repo = self.registry.get_repository()

        if conversation_id:
            all_mems = await repo.list_by_conversation(conversation_id, limit=200)
        else:
            all_mems = await repo.list_all(limit=200)

        # Filter active or pinned memories
        active_mems = [m for m in all_mems if m.status in (MemoryStatus.ACTIVE, MemoryStatus.PINNED)]

        # Keyword filtering if query is provided
        if query and query.strip():
            q_lower = query.strip().lower()
            active_mems = [m for m in active_mems if q_lower in m.content.lower()]

        selected = self.selector.select(active_mems, strategy=strategy, top_k=limit)
        scores = [self.scorer.score(m) for m in selected]

        dt = (time.perf_counter() - t0) * 1000.0
        return MemorySearchResult(
            matched_memories=selected,
            scores=scores,
            execution_time_ms=dt,
            strategy_used=strategy,
            total_count=len(selected),
        )

    async def assemble_context(
        self,
        conversation_id: Optional[uuid.UUID] = None,
        strategy: str = "hybrid",
        token_budget: int = 4000,
    ) -> MemoryContext:
        """Assembles structured MemoryContext payload for prompt variable injection."""
        t0 = time.perf_counter()
        repo = self.registry.get_repository()

        if conversation_id:
            memories = await repo.list_by_conversation(conversation_id, limit=200)
        else:
            memories = await repo.list_all(limit=200)

        active_memories = [m for m in memories if m.status in (MemoryStatus.ACTIVE, MemoryStatus.PINNED) and not m.is_expired]

        # Choose strategy
        strat_lower = strategy.lower().strip()
        if strat_lower == "recent":
            strat_impl = RecentStrategy()
        elif strat_lower == "importance":
            strat_impl = ImportanceStrategy()
        elif strat_lower == "sliding_window":
            strat_impl = SlidingWindowStrategy()
        else:
            strat_impl = HybridStrategy()

        builder = MemoryContextBuilder(strategy=strat_impl)
        context = builder.build_context(active_memories, token_budget=token_budget)
        context.conversation_id = conversation_id

        dt = (time.perf_counter() - t0) * 1000.0
        self.metrics.assembly_latency_ms = dt

        await self._emit_event("context_built", {
            "context_id": str(context.context_id),
            "conversation_id": str(conversation_id) if conversation_id else None,
            "total_memories": context.total_memories_count,
        })
        return context

    async def cleanup_expired(self) -> int:
        """Executes retention policy cleanup for expired memories."""
        repo = self.registry.get_repository()
        all_mems = await repo.list_all(limit=1000)

        cleaned = 0
        for m in all_mems:
            if m.is_expired and m.status != MemoryStatus.PINNED:
                m.status = MemoryStatus.EXPIRED
                await repo.save(m)
                cleaned += 1

        self.metrics.cleanup_count += cleaned
        return cleaned

    async def get_statistics(self) -> MemoryStatistics:
        """Returns snapshot statistics of the memory repository state."""
        repo = self.registry.get_repository()
        all_mems = await repo.list_all(limit=2000)

        active = [m for m in all_mems if m.status == MemoryStatus.ACTIVE]
        pinned = [m for m in all_mems if m.status == MemoryStatus.PINNED]
        archived = [m for m in all_mems if m.status == MemoryStatus.ARCHIVED]
        expired = [m for m in all_mems if m.status == MemoryStatus.EXPIRED or m.is_expired]

        avg_imp = (sum(m.importance for m in all_mems) / len(all_mems)) if all_mems else 0.0
        tot_tokens = sum(MemoryTokenEstimator.estimate_memory_tokens(m) for m in all_mems)

        return MemoryStatistics(
            total_memories=len(all_mems),
            active_memories=len(active),
            pinned_memories=len(pinned),
            archived_memories=len(archived),
            expired_memories=len(expired),
            average_importance=round(avg_imp, 4),
            total_token_usage=tot_tokens,
        )
