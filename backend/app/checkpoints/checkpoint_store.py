import uuid
from abc import ABC, abstractmethod
from typing import List

from app.checkpoints.checkpoint import Checkpoint
from app.checkpoints.exceptions import CheckpointNotFoundError


class CheckpointStore(ABC):
    """Abstract interface for checkpoint storage layers."""

    @abstractmethod
    def save(self, checkpoint: Checkpoint) -> None:
        """Persists a Checkpoint instance to the store."""
        pass

    @abstractmethod
    def load(self, checkpoint_id: uuid.UUID) -> Checkpoint:
        """Retrieves a Checkpoint instance by ID."""
        pass

    @abstractmethod
    def delete(self, checkpoint_id: uuid.UUID) -> None:
        """Removes a Checkpoint instance by ID."""
        pass

    @abstractmethod
    def exists(self, checkpoint_id: uuid.UUID) -> bool:
        """Returns True if checkpoint_id exists in the store."""
        pass

    @abstractmethod
    def list(self) -> List[Checkpoint]:
        """Lists all stored Checkpoint instances."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clears all stored Checkpoint instances."""
        pass


class InMemoryCheckpointStore(CheckpointStore):
    """In-memory reference implementation of CheckpointStore."""

    def __init__(self) -> None:
        self._store: dict[uuid.UUID, Checkpoint] = {}

    def save(self, checkpoint: Checkpoint) -> None:
        self._store[checkpoint.checkpoint_id] = checkpoint

    def load(self, checkpoint_id: uuid.UUID) -> Checkpoint:
        if checkpoint_id not in self._store:
            raise CheckpointNotFoundError(
                f"Checkpoint with ID '{checkpoint_id}' not found in store."
            )
        return self._store[checkpoint_id]

    def delete(self, checkpoint_id: uuid.UUID) -> None:
        if checkpoint_id not in self._store:
            raise CheckpointNotFoundError(
                f"Checkpoint with ID '{checkpoint_id}' not found in store."
            )
        del self._store[checkpoint_id]

    def exists(self, checkpoint_id: uuid.UUID) -> bool:
        return checkpoint_id in self._store

    def list(self) -> List[Checkpoint]:
        return list(self._store.values())

    def clear(self) -> None:
        self._store.clear()
