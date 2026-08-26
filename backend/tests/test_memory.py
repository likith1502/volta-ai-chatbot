import pytest
import uuid
from app.memory.compactor import MemoryCompactor
from app.memory.config import MemoryConfiguration
from app.memory.context import MemoryContext
from app.memory.context_builder import MemoryContextBuilder, MemoryVariableProvider
from app.memory.context_window import ContextWindowBudget
from app.memory.contracts import MemoryRequest
from app.memory.factory import MemoryFactory
from app.memory.filter import MemoryFilter
from app.memory.health import MemoryHealthManager
from app.memory.inmemory_repository import InMemoryMemoryRepository
from app.memory.manager import MemoryManager
from app.memory.memory import Memory
from app.memory.registry import MemoryRegistry
from app.memory.scoring import MemoryScorer
from app.memory.selector import MemorySelector
from app.memory.status import MemoryStatus
from app.memory.strategy import HybridStrategy, ImportanceStrategy, RecentStrategy, SlidingWindowStrategy
from app.memory.token_estimator import MemoryTokenEstimator
from app.memory.types import MemoryType
from app.prompt.contracts import PromptRequest


@pytest.mark.asyncio
async def test_memory_creation_and_repository():
    repo = InMemoryMemoryRepository()
    mem = Memory(
        content="User prefers Sedan vehicles",
        memory_type=MemoryType.USER,
        importance=0.8,
    )
    await repo.save(mem)

    retrieved = await repo.get_by_id(mem.memory_id)
    assert retrieved is not None
    assert retrieved.content == "User prefers Sedan vehicles"
    assert retrieved.memory_type == MemoryType.USER


@pytest.mark.asyncio
async def test_memory_filter_and_scoring():
    scorer = MemoryScorer()
    mem1 = Memory(content="High importance memory", importance=0.9)
    mem2 = Memory(content="Low importance memory", importance=0.1)

    score1 = scorer.score(mem1)
    score2 = scorer.score(mem2)
    assert score1 > score2

    filter_obj = MemoryFilter(min_importance=0.5)
    assert filter_obj.matches(mem1) is True
    assert filter_obj.matches(mem2) is False


@pytest.mark.asyncio
async def test_memory_selector_and_compactor():
    mem1 = Memory(content="Same memory text")
    mem2 = Memory(content="Same memory text")  # Duplicate
    mem3 = Memory(content="Unique memory content")

    compactor = MemoryCompactor()
    compacted = compactor.compact([mem1, mem2, mem3], token_budget=4000)
    assert len(compacted) == 2  # Deduplicated duplicate

    selector = MemorySelector()
    selected = selector.select(compacted, strategy="recent", top_k=1)
    assert len(selected) == 1


@pytest.mark.asyncio
async def test_context_assembly_strategies():
    memories = [
        Memory(content="System prompt", memory_type=MemoryType.SYSTEM, importance=1.0),
        Memory(content="Recent user turn", memory_type=MemoryType.SHORT_TERM, importance=0.5),
    ]

    hybrid = HybridStrategy()
    ctx = hybrid.assemble(memories, token_budget=4000)
    assert ctx.total_memories_count == 2
    assert "System prompt" in ctx.format_as_text()


@pytest.mark.asyncio
async def test_memory_manager_and_variable_provider():
    manager = MemoryManager()
    req = MemoryRequest(
        content="Pickup location is SFO Airport",
        memory_type=MemoryType.SHORT_TERM,
        importance=0.7,
    )
    created = await manager.create_memory(req)
    assert created.memory_id is not None

    provider = MemoryVariableProvider(memory_manager=manager)
    prompt_req = PromptRequest(
        template_id="mobility_assistant_v1",
        conversation_id=uuid.uuid4(),
    )
    resolved = await provider.resolve_variables(prompt_req)
    assert "conversation_memory" in resolved
