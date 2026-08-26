from typing import Callable, List, Optional, Type, Union

from app.streaming.exceptions import StreamAdapterError
from app.streaming.stream_adapter import StreamAdapter


class StreamRegistry:
    """Registry for managing and discovering stream adapters and factory instantiations."""

    def __init__(self) -> None:
        self._adapters: dict[
            str, Union[StreamAdapter, Type[StreamAdapter], Callable[[], StreamAdapter]]
        ] = {}

    def register_adapter(
        self,
        adapter: Union[StreamAdapter, Type[StreamAdapter], Callable[[], StreamAdapter]],
        adapter_id: Optional[str] = None,
        overwrite: bool = False,
    ) -> None:
        """Registers a StreamAdapter instance, class, or factory."""
        target_id = adapter_id
        if target_id is None:
            if isinstance(adapter, StreamAdapter):
                target_id = adapter.__class__.__name__
            elif isinstance(adapter, type) and issubclass(adapter, StreamAdapter):
                target_id = adapter.__name__
            elif callable(adapter):
                target_id = getattr(adapter, "__name__", str(id(adapter)))
            else:
                target_id = str(adapter)

        if target_id in self._adapters and not overwrite:
            raise StreamAdapterError(
                f"Stream adapter '{target_id}' is already registered."
            )

        self._adapters[target_id] = adapter

    def register_factory(
        self,
        adapter_id: str,
        factory: Callable[[], StreamAdapter],
        overwrite: bool = False,
    ) -> None:
        """Registers a lazy adapter factory."""
        self.register_adapter(
            adapter=factory, adapter_id=adapter_id, overwrite=overwrite
        )

    def unregister(self, adapter_id: str) -> None:
        """Unregisters an adapter by ID."""
        if adapter_id not in self._adapters:
            raise StreamAdapterError(
                f"Stream adapter '{adapter_id}' not found in registry."
            )
        del self._adapters[adapter_id]

    def exists(self, adapter_id: str) -> bool:
        """Returns True if adapter_id is registered."""
        return adapter_id in self._adapters

    def lookup(self, adapter_id: str) -> StreamAdapter:
        """Retrieves and instantiates a StreamAdapter by ID."""
        if adapter_id not in self._adapters:
            raise StreamAdapterError(
                f"Stream adapter '{adapter_id}' not found in registry."
            )
        target = self._adapters[adapter_id]

        if isinstance(target, StreamAdapter):
            return target
        elif isinstance(target, type) and issubclass(target, StreamAdapter):
            return target()
        elif callable(target):
            res = target()
            if isinstance(res, StreamAdapter):
                return res
            raise StreamAdapterError(
                f"Factory for adapter '{adapter_id}' did not return StreamAdapter."
            )
        raise StreamAdapterError(
            f"Invalid adapter registration for '{adapter_id}'."
        )

    def list(self) -> List[str]:
        """Lists IDs of registered adapters."""
        return list(self._adapters.keys())

    def clear(self) -> None:
        """Clears all registered adapters."""
        self._adapters.clear()
