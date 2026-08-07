import pytest
import uuid
from app.memory.lifecycle import MemoryLifecycleManager
from app.memory.manager import MemoryManager
from app.memory.memory import Memory
from app.memory.status import MemoryStatus


@pytest.mark.asyncio
async def test_memory_lifecycle_state_transitions():
    assert MemoryLifecycleManager.can_transition(MemoryStatus.ACTIVE, MemoryStatus.PINNED) is True
    assert MemoryLifecycleManager.can_transition(MemoryStatus.PINNED, MemoryStatus.ARCHIVED) is True
    assert MemoryLifecycleManager.can_transition(MemoryStatus.DELETED, MemoryStatus.ACTIVE) is False

    with pytest.raises(ValueError):
        MemoryLifecycleManager.validate_transition(MemoryStatus.DELETED, MemoryStatus.ACTIVE)


@pytest.mark.asyncio
async def test_memory_manager_pin_unpin_archive():
    manager = MemoryManager()
    from app.memory.contracts import MemoryRequest

    created = await manager.create_memory(MemoryRequest(content="Important user preference"))
    assert created.status == MemoryStatus.ACTIVE

    pinned = await manager.pin_memory(created.memory_id)
    assert pinned.status == MemoryStatus.PINNED
    assert pinned.is_pinned is True

    unpinned = await manager.unpin_memory(created.memory_id)
    assert unpinned.status == MemoryStatus.ACTIVE

    archived = await manager.archive_memory(created.memory_id)
    assert archived.status == MemoryStatus.ARCHIVED
