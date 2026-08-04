from typing import Optional

from app.graph.contracts import (
    GraphBuildOptions,
    GraphMetadata,
    GraphValidationResult,
    IGraphBuilder,
    IGraphEdge,
    IGraphNode,
)
from app.graph.exceptions import (
    DuplicateEdgeException,
    DuplicateNodeException,
    GraphValidationException,
    NodeNotFoundException,
)
from app.graph.graph import Graph


class GraphBuilder(IGraphBuilder):
    """
    Builder implementation for constructing, validating, and compiling immutable Graph objects.
    Enforces uniqueness of node IDs and edges, orphan edge validation, and optional cycle detection.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, IGraphNode] = {}
        self._edges: list[IGraphEdge] = []
        self._entry_node: Optional[str] = None
        self._metadata: GraphMetadata = GraphMetadata()

    def add_node(self, node: IGraphNode) -> "GraphBuilder":
        """
        Registers a node in the graph builder.
        Raises DuplicateNodeException if a node with the same node_id is already registered.
        """
        if node.node_id in self._nodes:
            raise DuplicateNodeException(
                f"Node with node_id '{node.node_id}' is already registered in GraphBuilder."
            )
        self._nodes[node.node_id] = node
        return self

    def add_edge(self, edge: IGraphEdge) -> "GraphBuilder":
        """
        Registers a directed edge in the graph builder.
        Raises DuplicateEdgeException if an identical edge (same source, target, and condition) exists.
        """
        for existing in self._edges:
            if (
                existing.source_node == edge.source_node
                and existing.target_node == edge.target_node
                and existing.edge_condition == edge.edge_condition
                and existing.priority == edge.priority
            ):
                raise DuplicateEdgeException(
                    f"Duplicate edge from '{edge.source_node}' to '{edge.target_node}' with same condition/priority."
                )

        self._edges.append(edge)
        return self

    def set_entry_node(self, node_id: str) -> "GraphBuilder":
        """
        Sets the entrypoint node ID for graph execution.
        """
        self._entry_node = node_id
        return self

    def set_metadata(self, metadata: GraphMetadata) -> "GraphBuilder":
        """
        Sets standardized graph metadata.
        """
        self._metadata = metadata
        return self

    def validate(self, options: Optional[GraphBuildOptions] = None) -> GraphValidationResult:
        """
        Validates graph structural rules:
        1. Checks that all edge source and target node IDs exist in registered nodes (no orphan edges).
        2. Checks entry node existence if set.
        3. Runs DFS cycle detection if options.allow_cycles is False.
        """
        opts = options or GraphBuildOptions()
        errors: list[str] = []
        warnings: list[str] = []

        # Validate orphan edge references
        for edge in self._edges:
            if edge.source_node not in self._nodes:
                errors.append(f"Orphan edge detected: source node '{edge.source_node}' is not registered.")
            if edge.target_node not in self._nodes:
                errors.append(f"Orphan edge detected: target node '{edge.target_node}' is not registered.")

        # Validate entry node
        if self._entry_node and self._entry_node not in self._nodes:
            errors.append(f"Entry node '{self._entry_node}' is not registered in GraphBuilder.")

        if errors:
            raise GraphValidationException(f"Graph validation failed: {'; '.join(errors)}")

        # Cycle detection if disallowed
        if not opts.allow_cycles and self._detect_cycles():
            raise GraphValidationException("Cycle detected in graph while allow_cycles=False.")

        return GraphValidationResult(
            is_valid=True,
            warnings=warnings,
            errors=[],
            statistics={
                "node_count": len(self._nodes),
                "edge_count": len(self._edges),
                "entry_node": self._entry_node,
            },
        )

    def _detect_cycles(self) -> bool:
        """
        Performs Depth-First Search (DFS) state color traversal to detect cycles in directed graph.
        0 = Unvisited, 1 = Visiting (in current recursion stack), 2 = Visited.
        """
        state_map: dict[str, int] = {node_id: 0 for node_id in self._nodes}
        adj: dict[str, list[str]] = {node_id: [] for node_id in self._nodes}

        for edge in self._edges:
            if edge.source_node in adj:
                adj[edge.source_node].append(edge.target_node)

        def dfs(node_id: str) -> bool:
            state_map[node_id] = 1
            for neighbor in adj.get(node_id, []):
                if state_map.get(neighbor) == 1:
                    return True  # Found back-edge / cycle
                if state_map.get(neighbor) == 0:
                    if dfs(neighbor):
                        return True
            state_map[node_id] = 2
            return False

        for node_id in self._nodes:
            if state_map[node_id] == 0:
                if dfs(node_id):
                    return True

        return False

    def build(self, options: Optional[GraphBuildOptions] = None) -> Graph:
        """
        Validates graph rules and returns a compiled immutable Graph instance.
        """
        self.validate(options=options)
        return Graph(
            nodes=self._nodes,
            edges=self._edges,
            entry_node=self._entry_node,
            metadata=self._metadata,
        )
