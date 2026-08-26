from typing import Callable, List, Optional, Type, Union

from app.checkpoints.checkpoint_store import CheckpointStore
from app.checkpoints.exceptions import (
    CheckpointNotFoundError,
    CheckpointStoreError,
)


class CheckpointRegistry:
    """Registry for managing and discovering checkpoint stores and factories."""

    def __init__(self) -> None:
        self._stores: dict[
            str,
            Union[
                CheckpointStore, Type[CheckpointStore], Callable[[], CheckpointStore]
            ],
        ] = {}

    def register(
        self,
        store: Union[
            CheckpointStore, Type[CheckpointStore], Callable[[], CheckpointStore]
        ],
        store_id: Optional[str] = None,
        overwrite: bool = False,
    ) -> None:
        """Registers a CheckpointStore instance, class, or factory function."""
        target_id = store_id
        if target_id is None:
            if isinstance(store, CheckpointStore):
                target_id = store.__class__.__name__
            elif isinstance(store, type) and issubclass(store, CheckpointStore):
                target_id = store.__name__
            elif callable(store):
                target_id = getattr(store, "__name__", str(id(store)))
            else:
                target_id = str(store)

        if target_id in self._stores and not overwrite:
            raise CheckpointStoreError(
                f"Checkpoint store with ID '{target_id}' is already registered."
            )

        self._stores[target_id] = store

    def register_factory(
        self,
        store_id: str,
        factory: Callable[[], CheckpointStore],
        overwrite: bool = False,
    ) -> None:
        """Registers a lazy store factory function."""
        self.register(store=factory, store_id=store_id, overwrite=overwrite)

    def unregister(self, store_id: str) -> None:
        """Unregisters a store by ID."""
        if store_id not in self._stores:
            raise CheckpointNotFoundError(
                f"Checkpoint store with ID '{store_id}' not found."
            )
        del self._stores[store_id]

    def exists(self, store_id: str) -> bool:
        """Returns True if store_id is registered."""
        return store_id in self._stores

    def lookup(self, store_id: str) -> CheckpointStore:
        """Retrieves and instantiates a CheckpointStore by ID."""
        if store_id not in self._stores:
            raise CheckpointNotFoundError(
                f"Checkpoint store with ID '{store_id}' not found."
            )
        target = self._stores[store_id]

        if isinstance(target, CheckpointStore):
            return target
        elif isinstance(target, type) and issubclass(target, CheckpointStore):
            return target()
        elif callable(target):
            res = target()
            if isinstance(res, CheckpointStore):
                return res
            raise CheckpointStoreError(
                f"Factory function for store '{store_id}' did not return a CheckpointStore."
            )
        raise CheckpointStoreError(
            f"Invalid store registration type for '{store_id}'."
        )

    def list(self) -> List[str]:
        """Lists IDs of registered stores."""
        return list(self._stores.keys())

    def clear(self) -> None:
        """Clears all registered stores."""
        self._store.clear() if hasattr(self, "_store") else self._stores.clear()
