import ast
from typing import Any

import pytest

from app.context.state import ConversationState
from app.context.types import NodeType, WorkflowStatus
from app.graph import (
    BaseNode,
    BuilderError,
    DuplicateEdgeError,
    DuplicateNodeError,
    ExecutionResult,
    Graph,
    GraphBuilder,
    GraphBuildOptions,
    GraphEdge,
    GraphError,
    GraphMetadata,
    GraphRegistry,
    GraphValidationError,
    GraphValidationResult,
    IGraph,
    IGraphBuilder,
    IGraphEdge,
    IGraphNode,
    IGraphRegistry,
    NodeNotFoundError,
    RegistryError,
)


class DummyNode(BaseNode):
    """Concrete dummy node for testing graph framework abstractions."""

    async def execute(self, state: ConversationState) -> ConversationState:
        return state.with_update(
            workflow_step=self.node_id,
            node_results={self.node_id: {"executed": True}},
        )


def test_node_instantiation_and_contract():
    """Verify BaseNode fulfills IGraphNode interface contract."""
    node = DummyNode(
        node_id="test_node_1",
        node_name="Test Node 1",
        node_type=NodeType.INPUT,
        description="A test input node",
        metadata={"priority": 1},
    )

    assert isinstance(node, IGraphNode)
    assert node.node_id == "test_node_1"
    assert node.node_name == "Test Node 1"
    assert node.node_type == "input"
    assert node.description == "A test input node"
    assert node.metadata == {"priority": 1}


@pytest.mark.asyncio
async def test_node_execution():
    """Verify dummy node async execution updates ConversationState."""
    node = DummyNode(node_id="step_a", node_name="Step A")
    state = ConversationState()

    updated = await node.execute(state)
    assert updated.workflow_step == "step_a"
    assert updated.execution.node_results == {"step_a": {"executed": True}}


def test_edge_instantiation_and_evaluation():
    """Verify GraphEdge instantiation, contract, and condition evaluation."""
    edge = GraphEdge(
        source_node="node_a",
        target_node="node_b",
        priority=10,
        metadata={"weight": 1.5},
    )

    assert isinstance(edge, IGraphEdge)
    assert edge.source_node == "node_a"
    assert edge.target_node == "node_b"
    assert edge.priority == 10

    # Unconditional edge evaluates to True
    state = ConversationState()
    import asyncio
    res = asyncio.run(edge.evaluate(state))
    assert res is True


@pytest.mark.asyncio
async def test_conditional_edge_evaluation():
    """Verify sync and async callable condition predicates on GraphEdge."""
    sync_edge = GraphEdge(
        source_node="n1",
        target_node="n2",
        edge_condition=lambda s: s.user_id == "admin",
    )

    async def async_cond(s: ConversationState) -> bool:
        return s.workflow_step == "verified"

    async_edge = GraphEdge(
        source_node="n1",
        target_node="n3",
        edge_condition=async_cond,
    )

    state_admin = ConversationState().with_update(user_id="admin", workflow_step="verified")
    state_user = ConversationState().with_update(user_id="user_guest", workflow_step="unverified")

    assert await sync_edge.evaluate(state_admin) is True
    assert await sync_edge.evaluate(state_user) is False

    assert await async_edge.evaluate(state_admin) is True
    assert await async_edge.evaluate(state_user) is False


def test_graph_builder_and_building():
    """Verify building an immutable graph with nodes, edges, and entrypoint."""
    builder = GraphBuilder()
    n1 = DummyNode(node_id="n1", node_name="Node 1")
    n2 = DummyNode(node_id="n2", node_name="Node 2")
    edge = GraphEdge(source_node="n1", target_node="n2", priority=5)

    meta = GraphMetadata(name="test_flow", version="1.0.0", description="Test flow")
    builder.add_node(n1).add_node(n2).add_edge(edge).set_entry_node("n1").set_metadata(meta)
    graph = builder.build()

    assert isinstance(graph, IGraph)
    assert isinstance(graph, Graph)
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    assert graph.entry_node == "n1"
    assert graph.metadata.name == "test_flow"
    assert graph.get_node("n1").node_name == "Node 1"

    val_res = graph.validate()
    assert isinstance(val_res, GraphValidationResult)
    assert val_res.is_valid is True
    assert val_res.statistics["node_count"] == 2

    outgoing = graph.get_outgoing_edges("n1")
    assert len(outgoing) == 1
    assert outgoing[0].target_node == "n2"


def test_builder_rejects_duplicate_node_id():
    """Verify GraphBuilder raises DuplicateNodeError when registering duplicate node IDs."""
    builder = GraphBuilder()
    n1 = DummyNode(node_id="same_id", node_name="Node A")
    n2 = DummyNode(node_id="same_id", node_name="Node B")

    builder.add_node(n1)
    with pytest.raises(DuplicateNodeError):
        builder.add_node(n2)


def test_builder_rejects_duplicate_edge():
    """Verify GraphBuilder raises DuplicateEdgeError when registering identical edges."""
    builder = GraphBuilder()
    n1 = DummyNode(node_id="n1", node_name="Node 1")
    n2 = DummyNode(node_id="n2", node_name="Node 2")
    builder.add_node(n1).add_node(n2)

    edge1 = GraphEdge(source_node="n1", target_node="n2", priority=1)
    edge2 = GraphEdge(source_node="n1", target_node="n2", priority=1)

    builder.add_edge(edge1)
    with pytest.raises(DuplicateEdgeError):
        builder.add_edge(edge2)


def test_builder_detects_orphan_edges():
    """Verify GraphBuilder validation fails when edge references unregistered nodes."""
    builder = GraphBuilder()
    n1 = DummyNode(node_id="n1", node_name="Node 1")
    builder.add_node(n1)

    # Edge targeting non-existent node "n99"
    orphan_edge = GraphEdge(source_node="n1", target_node="n99")
    builder.add_edge(orphan_edge)

    with pytest.raises(GraphValidationError):
        builder.build()


def test_builder_cycle_detection():
    """Verify GraphBuilder cycle detection when allow_cycles=False."""
    builder = GraphBuilder()
    n1 = DummyNode(node_id="n1", node_name="Node 1")
    n2 = DummyNode(node_id="n2", node_name="Node 2")
    builder.add_node(n1).add_node(n2)

    # Create cycle: n1 -> n2 -> n1
    builder.add_edge(GraphEdge(source_node="n1", target_node="n2"))
    builder.add_edge(GraphEdge(source_node="n2", target_node="n1"))

    # Default build allows cycles
    g_cyclic = builder.build(options=GraphBuildOptions(allow_cycles=True))
    assert len(g_cyclic.edges) == 2

    # Disallowing cycles raises GraphValidationError
    with pytest.raises(GraphValidationError):
        builder.build(options=GraphBuildOptions(allow_cycles=False))


def test_graph_node_not_found_exception():
    """Verify Graph raises NodeNotFoundError when requesting non-existent node."""
    builder = GraphBuilder()
    n1 = DummyNode(node_id="n1", node_name="Node 1")
    builder.add_node(n1)
    graph = builder.build()

    with pytest.raises(NodeNotFoundError):
        graph.get_node("non_existent")

    with pytest.raises(NodeNotFoundError):
        graph.get_outgoing_edges("non_existent")


def test_graph_registry():
    """Verify GraphRegistry template registration, lookup, lazy building, and duplicate prevention."""
    registry = GraphRegistry()
    assert isinstance(registry, IGraphRegistry)

    def create_my_graph_builder() -> GraphBuilder:
        b = GraphBuilder()
        b.add_node(DummyNode(node_id="start", node_name="Start Node"))
        return b

    registry.register("main_flow", create_my_graph_builder)
    assert registry.list_graphs() == ["main_flow"]

    # Prevent duplicate registration without overwrite flag
    with pytest.raises(RegistryError):
        registry.register("main_flow", create_my_graph_builder, overwrite=False)

    # Retrieve graph template
    compiled_graph = registry.get("main_flow")
    assert isinstance(compiled_graph, Graph)
    assert compiled_graph.get_node("start").node_name == "Start Node"

    # Unregister
    registry.unregister("main_flow")
    assert registry.list_graphs() == []

    with pytest.raises(RegistryError):
        registry.get("main_flow")


def test_contract_dto_models():
    """Verify ExecutionResult, GraphBuildOptions, GraphMetadata, GraphValidationResult instantiation."""
    meta = GraphMetadata(name="test_graph", version="2.0.0")
    assert meta.name == "test_graph"
    assert meta.version == "2.0.0"

    opts = GraphBuildOptions(allow_cycles=False, strict_validation=True)
    assert opts.allow_cycles is False

    val_res = GraphValidationResult(is_valid=True, statistics={"nodes": 5})
    assert val_res.is_valid is True

    exec_res = ExecutionResult(status=WorkflowStatus.COMPLETED, duration_ms=45.2, visited_nodes=["a", "b"])
    assert exec_res.status == WorkflowStatus.COMPLETED
    assert exec_res.visited_nodes == ["a", "b"]


def test_exception_hierarchy():
    """Verify typed graph exception inheritance tree."""
    assert issubclass(BuilderError, GraphError)
    assert issubclass(DuplicateNodeError, BuilderError)
    assert issubclass(DuplicateEdgeError, BuilderError)
    assert issubclass(NodeNotFoundError, GraphError)
    assert issubclass(GraphValidationError, GraphError)
    assert issubclass(RegistryError, GraphError)


def test_import_isolation():
    """Verify that backend/app/graph/ has zero forbidden framework/LLM/DB/Redis dependencies."""
    forbidden_keywords = [
        "langgraph",
        "openai",
        "anthropic",
        "google",
        "redis",
        "sqlalchemy",
        "fastapi",
        "ollama",
    ]

    import app.graph.builder as builder_mod
    import app.graph.contracts as contracts_mod
    import app.graph.edge as edge_mod
    import app.graph.exceptions as exceptions_mod
    import app.graph.graph as graph_mod
    import app.graph.node as node_mod
    import app.graph.registry as registry_mod

    modules = [
        contracts_mod,
        exceptions_mod,
        node_mod,
        edge_mod,
        graph_mod,
        builder_mod,
        registry_mod,
    ]

    for mod in modules:
        with open(mod.__file__, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=mod.__file__)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for forbidden in forbidden_keywords:
                        assert forbidden not in alias.name.lower(), (
                            f"Forbidden import '{alias.name}' found in {mod.__file__}"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for forbidden in forbidden_keywords:
                        assert forbidden not in node.module.lower(), (
                            f"Forbidden import from '{node.module}' found in {mod.__file__}"
                        )
