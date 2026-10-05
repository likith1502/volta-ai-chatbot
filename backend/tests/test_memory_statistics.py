import pytest
from app.memory.contracts import MemoryRequest
from app.memory.cost import MemoryCostEstimator
from app.memory.manager import MemoryManager
from app.memory.token_estimator import MemoryTokenEstimator


@pytest.mark.asyncio
async def test_memory_statistics_and_telemetry():
    manager = MemoryManager()
    await manager.create_memory(MemoryRequest(content="Short memory 1", importance=0.8))
    await manager.create_memory(MemoryRequest(content="Short memory 2", importance=0.6))

    stats = await manager.get_statistics()
    assert stats.total_memories == 2
    assert stats.active_memories == 2
    assert stats.average_importance == 0.7

    health = await manager.health_manager.check_health()
    assert health.is_healthy is True
    assert health.repository_size == 2

    cost = MemoryCostEstimator.estimate(memory_count=2, total_tokens=100)
    assert cost.estimated_storage_bytes > 0
