from typing import Any, Optional

from app.graph.contracts import GraphMetadata, GraphValidationResult, IGraph, IGraphEdge, IGraphNode
from app.graph.exceptions import NodeNotFoundException, GraphValidationException


class Graph(IGraph):
    """
    Immutable representation of a compiled execution graph.
    Container for registered nodes and directed edges.
    """

    def __init__(
        self,
        nodes: dict[str, IGraphNode],
        edges: list[IGraphEdge],
        entry_node: Optional[str] = None,
        metadata: Optional[GraphMetadata] = None,
    ) -> None:
        self._nodes: dict[str, IGraphNode] = dict(nodes)
        self._edges: list[IGraphEdge] = list(edges)
        self._entry_node: Optional[str] = entry_node
        self._metadata: GraphMetadata = metadata or GraphMetadata()

        # Pre-index adjacency list for fast outgoing edge lookup
        self._adjacency: dict[str, list[IGraphEdge]] = {node_id: [] for node_id in self._nodes}
        for edge in self._edges:
            if edge.source_node in self._adjacency:
                self._adjacency[edge.source_node].append(edge)

        # Sort outgoing edges by priority descending (higher priority first)
        for node_id in self._adjacency:
            self._adjacency[node_id].sort(key=lambda e: e.priority, reverse=True)

    @property
    def nodes(self) -> dict[str, IGraphNode]:
        """Returns read-only copy of registered nodes."""
        return dict(self._nodes)

    @property
    def edges(self) -> list[IGraphEdge]:
        """Returns read-only copy of registered directed edges."""
        return list(self._edges)

    @property
    def entry_node(self) -> Optional[str]:
        """Returns designated entrypoint node ID."""
        return self._entry_node

    @property
    def metadata(self) -> GraphMetadata:
        """Returns graph metadata."""
        return self._metadata

    def get_node(self, node_id: str) -> IGraphNode:
        """
        Retrieves node by ID.
        Raises NodeNotFoundException if node ID is not present in graph.
        """
        if node_id not in self._nodes:
            raise NodeNotFoundException(f"Node '{node_id}' not found in Graph.")
        return self._nodes[node_id]

    def get_outgoing_edges(self, node_id: str) -> list[IGraphEdge]:
        """
        Retrieves all directed outgoing edges originating from specified node ID,
        ordered by priority descending.
        Raises NodeNotFoundException if node ID is not present in graph.
        """
        if node_id not in self._nodes:
            raise NodeNotFoundException(f"Node '{node_id}' not found in Graph.")
        return list(self._adjacency.get(node_id, []))

    def validate(self) -> GraphValidationResult:
        """
        Validates internal graph structural integrity.
        Verifies that all edge source and target nodes exist in the node set.
        """
        errors: list[str] = []

        for edge in self._edges:
            if edge.source_node not in self._nodes:
                errors.append(f"Edge source node '{edge.source_node}' does not exist in Graph nodes.")
            if edge.target_node not in self._nodes:
                errors.append(f"Edge target node '{edge.target_node}' does not exist in Graph nodes.")

        if self._entry_node and self._entry_node not in self._nodes:
            errors.append(f"Entry node '{self._entry_node}' does not exist in Graph nodes.")

        if errors:
            raise GraphValidationException(f"Graph validation failed: {'; '.join(errors)}")

        return GraphValidationResult(
            is_valid=True,
            statistics={
                "node_count": len(self._nodes),
                "edge_count": len(self._edges),
                "entry_node": self._entry_node,
            },
        )
