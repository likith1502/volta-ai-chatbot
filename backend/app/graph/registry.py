from typing import Callable, Union

from app.graph.builder import GraphBuilder
from app.graph.contracts import IGraph, IGraphBuilder, IGraphRegistry
from app.graph.exceptions import RegistryException


class GraphRegistry(IGraphRegistry):
    """
    Registry for managing and resolving reusable graph templates and builders.
    Supports lazy instantiation and duplicate registration prevention.
    """

    def __init__(self) -> None:
        self._registry: dict[str, Union[IGraphBuilder, Callable[[], IGraphBuilder]]] = {}

    def register(
        self,
        name: str,
        builder_or_factory: Union[IGraphBuilder, Callable[[], IGraphBuilder]],
        overwrite: bool = False,
    ) -> None:
        """
        Registers a graph builder or factory function under the specified template name.
        Raises RegistryException if template name is already registered and overwrite is False.
        """
        if name in self._registry and not overwrite:
            raise RegistryException(
                f"Graph template '{name}' is already registered in GraphRegistry."
            )
        self._registry[name] = builder_or_factory

    def get(self, name: str) -> IGraph:
        """
        Retrieves and compiles a registered graph template by name.
        Lazy-evaluates factory functions if provided.
        Raises RegistryException if template name is not registered.
        """
        if name not in self._registry:
            raise RegistryException(f"Graph template '{name}' is not registered in GraphRegistry.")

        item = self._registry[name]

        if callable(item) and not isinstance(item, IGraphBuilder):
            builder = item()
        else:
            builder = item

        if isinstance(builder, IGraphBuilder):
            return builder.build()
        elif isinstance(builder, IGraph):
            return builder
        else:
            raise RegistryException(f"Registered item '{name}' did not produce a valid IGraph instance.")

    def list_graphs(self) -> list[str]:
        """
        Returns a sorted list of registered graph template names.
        """
        return sorted(list(self._registry.keys()))

    def unregister(self, name: str) -> None:
        """
        Unregisters a graph template by name if present.
        """
        self._registry.pop(name, None)

    def clear(self) -> None:
        """
        Clears all registered graph templates.
        """
        self._registry.clear()
