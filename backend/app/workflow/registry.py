from typing import Callable, List, Optional, Type, Union

from app.workflow.base import BaseWorkflowNode
from app.workflow.exceptions import (
    DuplicateWorkflowNodeException,
    WorkflowNodeNotFoundException,
)
from app.workflow.metadata import WorkflowNodeMetadata
from app.workflow.node_types import WorkflowNodeType


class WorkflowNodeRegistry:
    """Registry for managing and discovering reusable workflow nodes."""

    def __init__(self) -> None:
        self._nodes: dict[str, Union[BaseWorkflowNode, Type[BaseWorkflowNode], Callable[[], BaseWorkflowNode]]] = {}

    def register(
        self,
        node: Union[BaseWorkflowNode, Type[BaseWorkflowNode], Callable[[], BaseWorkflowNode]],
        node_id: Optional[str] = None,
        overwrite: bool = False,
    ) -> None:
        """Registers a workflow node instance, class, or factory function."""
        target_id = node_id
        if target_id is None:
            if isinstance(node, BaseWorkflowNode):
                target_id = node.node_id
            elif isinstance(node, type) and issubclass(node, BaseWorkflowNode):
                target_id = getattr(node, "node_id", node.__name__)
            elif callable(node):
                target_id = getattr(node, "__name__", str(id(node)))
            else:
                target_id = str(node)

        if target_id in self._nodes and not overwrite:
            raise DuplicateWorkflowNodeException(
                f"Workflow node with ID '{target_id}' is already registered."
            )

        self._nodes[target_id] = node

    def register_factory(
        self,
        node_id: str,
        factory: Callable[[], BaseWorkflowNode],
        overwrite: bool = False,
    ) -> None:
        """Registers a node factory function for lazy node instantiation."""
        self.register(node=factory, node_id=node_id, overwrite=overwrite)

    def unregister(self, node_id: str) -> None:
        """Unregisters a node by ID."""
        if node_id not in self._nodes:
            raise WorkflowNodeNotFoundException(
                f"Workflow node with ID '{node_id}' not found."
            )
        del self._nodes[node_id]

    def exists(self, node_id: str) -> bool:
        """Returns True if node_id is registered."""
        return node_id in self._nodes

    def lookup(self, node_id: str) -> BaseWorkflowNode:
        """Retrieves and instantiates (if lazy) a node by node_id."""
        if node_id not in self._nodes:
            raise WorkflowNodeNotFoundException(
                f"Workflow node with ID '{node_id}' not found."
            )
        target = self._nodes[node_id]

        if isinstance(target, BaseWorkflowNode):
            return target
        elif isinstance(target, type) and issubclass(target, BaseWorkflowNode):
            return target(node_id=node_id, node_name=target.__name__)
        elif callable(target):
            res = target()
            if isinstance(res, BaseWorkflowNode):
                return res
            raise WorkflowNodeNotFoundException(
                f"Factory function for node '{node_id}' did not return a BaseWorkflowNode."
            )
        raise WorkflowNodeNotFoundException(f"Invalid node registration type for '{node_id}'.")

    def list(self) -> List[str]:
        """Lists IDs of all registered workflow nodes."""
        return list(self._nodes.keys())

    def list_categories(self) -> List[WorkflowNodeType]:
        """Lists distinct categories present among registered nodes."""
        categories = set()
        for node_id in self._nodes:
            instance = self.lookup(node_id)
            categories.add(instance.node_category)
        return sorted(list(categories), key=lambda c: c.value)

    def list_types(self) -> List[str]:
        """Lists distinct class names of registered nodes."""
        types = set()
        for node_id in self._nodes:
            instance = self.lookup(node_id)
            types.add(instance.__class__.__name__)
        return sorted(list(types))

    def search(self, query: str) -> List[str]:
        """Searches registered node IDs, names, and descriptions matching query."""
        q = query.lower()
        results = []
        for node_id in self._nodes:
            instance = self.lookup(node_id)
            if (
                q in node_id.lower()
                or q in instance.node_name.lower()
                or q in instance.node_description.lower()
                or any(q in tag.lower() for tag in instance.node_metadata.tags)
            ):
                results.append(node_id)
        return results

    def list_by_category(self, category: WorkflowNodeType) -> List[BaseWorkflowNode]:
        """Retrieves all registered nodes matching the specified category."""
        matched = []
        for node_id in self._nodes:
            instance = self.lookup(node_id)
            if instance.node_category == category:
                matched.append(instance)
        return matched

    def get_metadata(self, node_id: str) -> WorkflowNodeMetadata:
        """Retrieves metadata for a registered node."""
        instance = self.lookup(node_id)
        return instance.node_metadata

    def clear(self) -> None:
        """Clears all registered nodes."""
        self._nodes.clear()
