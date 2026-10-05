import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.prompt.result import PromptResult


class PromptSnapshot(BaseModel):
    """Immutable snapshot recording template versioning, variables, rendered prompt, and timestamp."""

    snapshot_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    template_id: str
    revision_id: str = "v1"
    variables: dict[str, Any] = Field(default_factory=dict)
    rendered_content: str
    execution_id: Optional[uuid.UUID] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PromptExecutionStore(ABC):
    """Abstract storage repository backing prompt execution history and snapshot queries."""

    @abstractmethod
    async def save_result(self, result: PromptResult) -> None:
        pass

    @abstractmethod
    async def save_snapshot(self, snapshot: PromptSnapshot) -> None:
        pass

    @abstractmethod
    async def get_result_by_id(self, prompt_id: uuid.UUID) -> Optional[PromptResult]:
        pass

    @abstractmethod
    async def list_recent_results(self, limit: int = 50) -> list[PromptResult]:
        pass

    @abstractmethod
    async def list_recent_snapshots(self, limit: int = 50) -> list[PromptSnapshot]:
        pass


class InMemoryPromptExecutionStore(PromptExecutionStore):
    """In-memory execution store for prompt results and snapshots."""

    def __init__(self, capacity: int = 200) -> None:
        self.capacity = capacity
        self._results: dict[uuid.UUID, PromptResult] = {}
        self._results_order: list[uuid.UUID] = []
        self._snapshots: list[PromptSnapshot] = []

    async def save_result(self, result: PromptResult) -> None:
        pid = result.context.prompt_id
        if pid not in self._results:
            self._results_order.append(pid)
        self._results[pid] = result

        if len(self._results_order) > self.capacity:
            old_id = self._results_order.pop(0)
            self._results.pop(old_id, None)

    async def save_snapshot(self, snapshot: PromptSnapshot) -> None:
        self._snapshots.append(snapshot)
        if len(self._snapshots) > self.capacity:
            self._snapshots.pop(0)

    async def get_result_by_id(self, prompt_id: uuid.UUID) -> Optional[PromptResult]:
        return self._results.get(prompt_id)

    async def list_recent_results(self, limit: int = 50) -> list[PromptResult]:
        recent_ids = list(reversed(self._results_order[-limit:]))
        return [self._results[pid] for pid in recent_ids if pid in self._results]

    async def list_recent_snapshots(self, limit: int = 50) -> list[PromptSnapshot]:
        return list(reversed(self._snapshots[-limit:]))
