import importlib
import sys
import pytest
from app.context.state import ConversationState
from app.graph.node import BaseNode
from app.workflow import (
    BaseWorkflowNode,
    DecisionNode,
    DuplicateWorkflowNodeError,
    EndNode,
    EntityNode,
    IntentNode,
    LLMNode,
    MemoryNode,
    NodeCapability,
    NodeExecutionContext,
    NodeExecutionConstraints,
    NodeResult,
    RegistryError,
    ResponseNode,
    StartNode,
    ToolNode,
    WorkflowNodeConfig,
    WorkflowNodeError,
    WorkflowNodeMetadata,
    WorkflowNodeNotFoundError,
    WorkflowNodeRegistry,
    WorkflowNodeType,
    WorkflowValidationError,
)


def test_base_node_inheritance() -> None:
    """Verify that BaseWorkflowNode inherits from BaseNode."""
    node = StartNode(node_id="start_1")
    assert isinstance(node, BaseNode)
    assert isinstance(node, BaseWorkflowNode)
    assert node.node_category == WorkflowNodeType.START
    assert node.node_name == "StartNode"


def test_node_metadata_and_versioning() -> None:
    """Verify metadata separation and versioning fields."""
    meta = WorkflowNodeMetadata(
        author="UnitTester",
        version="1.2.0",
        api_version="v2",
        schema_version="2.0",
        tags=["test", "core"],
        description="Test metadata node",
        category=WorkflowNodeType.LLM,
    )
    assert meta.author == "UnitTester"
    assert meta.version == "1.2.0"
    assert meta.api_version == "v2"
    assert meta.schema_version == "2.0"
    assert "test" in meta.tags
    assert meta.category == WorkflowNodeType.LLM


def test_node_config_and_capabilities() -> None:
    """Verify separation of node config, capabilities, and constraints."""
    config = WorkflowNodeConfig(timeout=45.0, checkpoint=True)
    caps = NodeCapability(supports_streaming=True, supports_human_review=True)
    constraints = NodeExecutionConstraints(max_execution_time=120.0, max_retries=5)

    node = LLMNode(
        node_id="llm_1",
        config=config,
        capabilities=caps,
        constraints=constraints,
    )

    assert node.config.timeout == 45.0
    assert node.config.checkpoint is True
    assert node.capabilities.supports_streaming is True
    assert node.capabilities.supports_human_review is True
    assert node.constraints.max_execution_time == 120.0
    assert node.constraints.max_retries == 5


@pytest.mark.asyncio
async def test_node_lifecycle_hooks() -> None:
    """Verify node before_execute, execute, after_execute, and on_error hooks."""
    node = StartNode(node_id="start_test")
    state = ConversationState()
    context = NodeExecutionContext(graph_id="g_1", node_id="start_test")

    # Lifecycle pass-through execution
    state = await node.before_execute(state, context)
    state = await node.execute(state, context)
    state = await node.after_execute(state, context)

    assert isinstance(state, ConversationState)

    # Test error hook
    err = ValueError("Test error")
    err_state = await node.on_error(state, err, context)
    assert err_state == state


@pytest.mark.asyncio
async def test_all_placeholder_nodes_execution() -> None:
    """Verify that all 9 concrete placeholder nodes execute asynchronously as pass-through contracts."""
    nodes: list[BaseWorkflowNode] = [
        StartNode(node_id="start_1"),
        EndNode(node_id="end_1"),
        DecisionNode(node_id="decision_1"),
        LLMNode(node_id="llm_1"),
        ToolNode(node_id="tool_1"),
        MemoryNode(node_id="memory_1"),
        IntentNode(node_id="intent_1"),
        EntityNode(node_id="entity_1"),
        ResponseNode(node_id="response_1"),
    ]

    state = ConversationState()
    context = NodeExecutionContext()

    for node in nodes:
        out_state = await node.execute(state, context)
        assert out_state is state
        assert node.validate_input(state) is True
        assert node.validate_output(state) is True


def test_registry_crud_operations() -> None:
    """Verify registry register, lookup, unregister, exists, list, and clear methods."""
    registry = WorkflowNodeRegistry()
    node_1 = StartNode(node_id="start_node_1")
    node_2 = EndNode(node_id="end_node_1")

    # Register
    registry.register(node_1)
    registry.register(node_2)
    assert registry.exists("start_node_1") is True
    assert registry.exists("end_node_1") is True
    assert len(registry.list()) == 2

    # Lookup
    fetched = registry.lookup("start_node_1")
    assert fetched == node_1

    # Unregister
    registry.unregister("start_node_1")
    assert registry.exists("start_node_1") is False
    assert len(registry.list()) == 1

    # Clear
    registry.clear()
    assert len(registry.list()) == 0


def test_registry_duplicate_and_not_found_exceptions() -> None:
    """Verify registry exceptions for duplicate registration and missing nodes."""
    registry = WorkflowNodeRegistry()
    node = LLMNode(node_id="llm_test")
    registry.register(node)

    # Duplicate without overwrite raises DuplicateWorkflowNodeError
    with pytest.raises(DuplicateWorkflowNodeError):
        registry.register(node)

    # Duplicate with overwrite succeeds
    registry.register(node, overwrite=True)

    # Unregister missing raises WorkflowNodeNotFoundError
    with pytest.raises(WorkflowNodeNotFoundError):
        registry.unregister("non_existent_node")

    # Lookup missing raises WorkflowNodeNotFoundError
    with pytest.raises(WorkflowNodeNotFoundError):
        registry.lookup("non_existent_node")


def test_registry_discovery_methods() -> None:
    """Verify list_categories, list_types, search, and list_by_category."""
    registry = WorkflowNodeRegistry()
    registry.register(StartNode(node_id="start_1"))
    registry.register(LLMNode(node_id="llm_1"))
    registry.register(EndNode(node_id="end_1"))

    # list_categories
    categories = registry.list_categories()
    assert WorkflowNodeType.START in categories
    assert WorkflowNodeType.LLM in categories
    assert WorkflowNodeType.END in categories

    # list_types
    types = registry.list_types()
    assert "StartNode" in types
    assert "LLMNode" in types
    assert "EndNode" in types

    # search
    search_res = registry.search("Start")
    assert "start_1" in search_res

    # list_by_category
    llm_nodes = registry.list_by_category(WorkflowNodeType.LLM)
    assert len(llm_nodes) == 1
    assert llm_nodes[0].node_id == "llm_1"


def test_exception_hierarchy() -> None:
    """Verify exception inheritance tree."""
    assert issubclass(DuplicateWorkflowNodeError, WorkflowNodeError)
    assert issubclass(WorkflowNodeNotFoundError, WorkflowNodeError)
    assert issubclass(WorkflowValidationError, WorkflowNodeError)
    assert issubclass(RegistryError, WorkflowNodeError)


def test_import_isolation_and_no_framework_leakage() -> None:
    """Verify app.workflow modules do not import forbidden framework dependencies or DB/API layers."""
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

    import app.workflow as wf

    for mod_name in sys.modules:
        if mod_name.startswith("app.workflow"):
            mod = sys.modules[mod_name]
            mod_file = getattr(mod, "__file__", "")
            if mod_file:
                with open(mod_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    for forbidden in forbidden_modules:
                        assert forbidden not in content, f"Forbidden dependency '{forbidden}' found in {mod_name}!"


def test_node_result_contract() -> None:
    """Verify NodeResult model structure and default values."""
    res = NodeResult(
        next_node="next_step",
        execution_time=12.5,
        warnings=["minor latency"],
    )
    assert res.next_node == "next_step"
    assert res.execution_time == 12.5
    assert "minor latency" in res.warnings
    assert res.state is None


def test_system_node_category() -> None:
    """Verify SYSTEM node category presence in enum."""
    assert WorkflowNodeType.SYSTEM == "system"


def test_registry_register_factory() -> None:
    """Verify register_factory method lazily instantiates nodes when looked up."""
    registry = WorkflowNodeRegistry()

    def factory() -> BaseWorkflowNode:
        return StartNode(node_id="lazy_start")

    registry.register_factory("lazy_start", factory)
    assert registry.exists("lazy_start") is True

    node = registry.lookup("lazy_start")
    assert isinstance(node, StartNode)
    assert node.node_id == "lazy_start"

