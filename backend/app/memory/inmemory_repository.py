import uuid
from typing import Optional
from app.memory.memory import Memory
from app.memory.repository import MemoryRepository
from app.memory.status import MemoryStatus


class InMemoryMemoryRepository(MemoryRepository):
    """In-memory thread-safe reference implementation of MemoryRepository."""

    def __init__(self, capacity: int = 2000) -> None:
        self.capacity = capacity
        self._memories: dict[uuid.UUID, Memory] = {}

    async def save(self, memory: Memory) -> None:
        self._memories[memory.memory_id] = memory
        if len(self._memories) > self.capacity:
            # Drop oldest non-pinned active memory
            oldest_id = None
            oldest_time = None
            for mid, m in self._memories.items():
                if m.status != MemoryStatus.PINNED:
                    if oldest_time is None or m.created_at < oldest_time:
                        oldest_time = m.created_at
                        oldest_id = mid
            if oldest_id:
                self._memories.pop(oldest_id, None)

    async def get_by_id(self, memory_id: uuid.UUID) -> Optional[Memory]:
        return self._memories.get(memory_id)

    async def delete(self, memory_id: uuid.UUID) -> bool:
        if memory_id in self._memories:
            self._memories.pop(memory_id)
            return True
        return False

    async def list_by_conversation(
        self,
        conversation_id: uuid.UUID,
        status: Optional[MemoryStatus] = None,
        limit: int = 100,
    ) -> list[Memory]:
        matches = [
            m for m in self._memories.values()
            if m.conversation_id == conversation_id and (status is None or m.status == status)
        ]
        matches.sort(key=lambda x: x.created_at, reverse=True)
        return matches[:limit]

    async def list_all(self, limit: int = 100) -> list[Memory]:
        all_mems = list(self._memories.values())
        all_mems.sort(key=lambda x: x.created_at, reverse=True)
        return all_mems[:limit]

    async def clear(self) -> None:
        self._memories.clear()
