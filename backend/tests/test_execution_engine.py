import sys
import pytest
from app.context.state import ConversationState
from app.context.types import ExecutionMode
from app.execution import (
    ExecutionCancelledError,
    ExecutionContext,
    ExecutionDispatcher,
    ExecutionError,
    ExecutionMetrics,
    ExecutionPlanner,
    ExecutionPolicy,
    ExecutionResult,
    ExecutionScheduler,
    ExecutionSnapshot,
    ExecutionStatus,
    ExecutionStrategy,
    ExecutionStrategyError,
    ExecutionTimeoutError,
    ExecutionValidationError,
    GraphExecutor,
    SequentialStrategy,
)
from app.graph.builder import GraphBuilder
from app.graph.edge import GraphEdge
from app.workflow import EndNode, LLMNode, StartNode, WorkflowNodeConfig


@pytest.mark.asyncio
async def test_successful_graph_execution_traversal() -> None:
    """Verify full sequential graph traversal through StartNode -> LLMNode -> EndNode."""
    start_node = StartNode(node_id="start")
    llm_node = LLMNode(node_id="llm")
    end_node = EndNode(node_id="end")

    builder = GraphBuilder()
    builder.add_node(start_node).add_node(llm_node).add_node(end_node)
    builder.add_edge(GraphEdge(source_node="start", target_node="llm"))
    builder.add_edge(GraphEdge(source_node="llm", target_node="end"))
    builder.set_entry_node("start")

    graph = builder.build()
    executor = GraphExecutor()

    initial_state = ConversationState()
    result = await executor.execute(graph, initial_state)

    assert isinstance(result, ExecutionResult)
    assert result.execution_status == ExecutionStatus.COMPLETED
    assert result.visited_nodes == ["start", "llm", "end"]
    assert len(result.snapshots) == 3
    assert result.execution_metrics.node_count == 3
    assert result.execution_metrics.success_rate == 1.0
    assert len(executor.events) > 0


@pytest.mark.asyncio
async def test_conditional_edge_branching() -> None:
    """Verify graph traversal following conditional edge predicates."""
    start_node = StartNode(node_id="start")
    llm_node_a = LLMNode(node_id="llm_a")
    llm_node_b = LLMNode(node_id="llm_b")
    end_node = EndNode(node_id="end")

    # Condition favoring llm_b
    edge_a = GraphEdge(
        source_node="start",
        target_node="llm_a",
        edge_condition=lambda state: state.memory.extracted_entities.get("route") == "a",
        priority=1,
    )
    edge_b = GraphEdge(
        source_node="start",
        target_node="llm_b",
        edge_condition=lambda state: state.memory.extracted_entities.get("route") == "b",
        priority=2,
    )

    builder = GraphBuilder()
    builder.add_node(start_node).add_node(llm_node_a).add_node(llm_node_b).add_node(end_node)
    builder.add_edge(edge_a).add_edge(edge_b)
    builder.add_edge(GraphEdge(source_node="llm_b", target_node="end"))
    builder.set_entry_node("start")

    graph = builder.build()
    executor = GraphExecutor()

    state = ConversationState()
    state.memory.extracted_entities["route"] = "b"

    result = await executor.execute(graph, state)

    assert result.execution_status == ExecutionStatus.COMPLETED
    assert result.visited_nodes == ["start", "llm_b", "end"]
    assert "llm_a" not in result.visited_nodes


from app.graph.graph import Graph


@pytest.mark.asyncio
async def test_mandatory_graph_validation_failure() -> None:
    """Verify mandatory pre-execution graph validation halts un-compilable or invalid graphs."""
    start_node = StartNode(node_id="start")
    # Manually construct an invalid graph with a missing entry node
    invalid_graph = Graph(nodes={"start": start_node}, edges=[], entry_node="non_existent")
    executor = GraphExecutor()

    with pytest.raises(ExecutionValidationError):
        await executor.execute(invalid_graph, ConversationState())


@pytest.mark.asyncio
async def test_max_depth_protection() -> None:
    """Verify depth protection limits graph traversal steps and raises ExecutionValidationError."""
    start_node = StartNode(node_id="start")
    end_node = EndNode(node_id="end")

    builder = GraphBuilder()
    builder.add_node(start_node).add_node(end_node)
    builder.add_edge(GraphEdge(source_node="start", target_node="end"))
    builder.set_entry_node("start")

    graph = builder.build()

    # Set policy max_depth to 1 (which will fail when attempting to move from start to end)
    policy = ExecutionPolicy(max_depth=1)
    executor = GraphExecutor(policy=policy)

    with pytest.raises(ExecutionValidationError) as exc_info:
        await executor.execute(graph, ConversationState())

    assert "Maximum graph traversal depth" in str(exc_info.value)


@pytest.mark.asyncio
async def test_dispatcher_lifecycle_hooks() -> None:
    """Verify ExecutionDispatcher calls lifecycle hooks and handles errors."""
    dispatcher = ExecutionDispatcher()

    class FailingNode(StartNode):
        async def execute(self, state: ConversationState, context=None) -> ConversationState:
            raise RuntimeError("Node execution error")

    fail_node = FailingNode(node_id="fail_1")
    builder = GraphBuilder()
    builder.add_node(fail_node)
    builder.set_entry_node("fail_1")

    graph = builder.build()
    context = ExecutionContext(graph_id="g_fail")
    state = ConversationState()

    snapshot, out_state, err = await dispatcher.dispatch(graph, "fail_1", state, context)

    assert err is not None
    assert isinstance(err, RuntimeError)
    assert snapshot is not None
    assert snapshot.node_id == "fail_1"


@pytest.mark.asyncio
async def test_stop_on_error_policy() -> None:
    """Verify stop_on_error policy halts traversal when a node fails."""
    class ErrorNode(StartNode):
        async def execute(self, state: ConversationState, context=None) -> ConversationState:
            raise ValueError("Failure in node")

    err_node = ErrorNode(node_id="err_1")
    end_node = EndNode(node_id="end_1")

    builder = GraphBuilder()
    builder.add_node(err_node).add_node(end_node)
    builder.add_edge(GraphEdge(source_node="err_1", target_node="end_1"))
    builder.set_entry_node("err_1")

    graph = builder.build()
    policy = ExecutionPolicy(stop_on_error=True)
    executor = GraphExecutor(policy=policy)

    result = await executor.execute(graph, ConversationState())

    assert result.execution_status == ExecutionStatus.FAILED
    assert result.visited_nodes == ["err_1"]
    assert len(result.errors) == 1
    assert result.execution_metrics.success_rate == 0.0


def test_exception_hierarchy() -> None:
    """Verify execution exception hierarchy inheritance."""
    assert issubclass(ExecutionTimeoutError, ExecutionError)
    assert issubclass(ExecutionCancelledError, ExecutionError)
    assert issubclass(ExecutionValidationError, ExecutionError)
    assert issubclass(ExecutionStrategyError, ExecutionError)


def test_execution_planner_and_metrics() -> None:
    """Verify planner contract generation and metrics recalculation."""
    planner = ExecutionPlanner()
    builder = GraphBuilder()
    builder.add_node(StartNode(node_id="s1"))
    builder.set_entry_node("s1")
    graph = builder.build()

    plan = planner.plan_execution(graph, ConversationState())
    assert plan["entry_node"] == "s1"
    assert plan["strategy"] == "sequential"

    metrics = ExecutionMetrics(visited_nodes=["s1", "s2"], failed_nodes=["s2"])
    metrics.compute_success_rate()
    assert metrics.success_rate == 0.5


def test_import_isolation_and_no_framework_leakage() -> None:
    """Verify app.execution modules do not import forbidden framework dependencies or DB/API layers."""
    forbidden_modules = [
        "sqlalchemy",
        "redis",
        "langgraph",
        "openai",
        "google.generativeai",
        "anthropic",
        "app.db",
        "app.repositories",
        "app.services",
        "app.api",
    ]

    import app.execution as exc_mod

    for mod_name in sys.modules:
        if mod_name.startswith("app.execution"):
            mod = sys.modules[mod_name]
            mod_file = getattr(mod, "__file__", "")
            if mod_file:
                with open(mod_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    for forbidden in forbidden_modules:
                        assert forbidden not in content, f"Forbidden dependency '{forbidden}' found in {mod_name}!"
