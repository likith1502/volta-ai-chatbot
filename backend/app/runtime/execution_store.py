import uuid
from abc import ABC, abstractmethod
from typing import Optional

from app.runtime.result import RuntimeResult


class RuntimeExecutionStore(ABC):
    """Abstract storage repository backing runtime execution history queries."""

    @abstractmethod
    async def save(self, result: RuntimeResult) -> None:
        """Persists a RuntimeResult snapshot."""
        pass

    @abstractmethod
    async def get_by_id(self, runtime_id: uuid.UUID) -> Optional[RuntimeResult]:
        """Retrieves a RuntimeResult by runtime_id."""
        pass

    @abstractmethod
    async def list_recent(self, limit: int = 50) -> list[RuntimeResult]:
        """Retrieves recent execution records ordered by timestamp descending."""
        pass


class InMemoryExecutionStore(RuntimeExecutionStore):
    """In-memory thread-safe execution store for fast execution history querying."""

    def __init__(self, capacity: int = 200) -> None:
        self.capacity = capacity
        self._store: dict[uuid.UUID, RuntimeResult] = {}
        self._order: list[uuid.UUID] = []

    async def save(self, result: RuntimeResult) -> None:
        rid = result.context.runtime_id
        if rid not in self._store:
            self._order.append(rid)
        self._store[rid] = result

        # Enforce ring buffer capacity
        if len(self._order) > self.capacity:
            oldest_id = self._order.pop(0)
            self._store.pop(oldest_id, None)

    async def get_by_id(self, runtime_id: uuid.UUID) -> Optional[RuntimeResult]:
        return self._store.get(runtime_id)

    async def list_recent(self, limit: int = 50) -> list[RuntimeResult]:
        recent_ids = list(reversed(self._order[-limit:]))
        return [self._store[rid] for rid in recent_ids if rid in self._store]
