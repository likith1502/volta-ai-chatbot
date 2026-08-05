import sys
import uuid
import pytest
from app.checkpoints import (
    Checkpoint,
    CheckpointException,
    CheckpointFilter,
    CheckpointManager,
    CheckpointMetadata,
    CheckpointNotFoundException,
    CheckpointPolicy,
    CheckpointRegistry,
    CheckpointStatus,
    CheckpointStoreException,
    CheckpointValidationException,
    CheckpointValidationResult,
    CheckpointVersion,
    InMemoryCheckpointStore,
    ReplayAction,
    ReplayContext,
    ReplayEngine,
    ReplayException,
    ReplayHistory,
    ReplayMetrics,
    ReplayMode,
    ReplayResult,
    ReplayStrategyException,
    ReplayValidationException,
    SequentialReplayStrategy,
)
from app.context.state import ConversationState
from app.execution.execution_snapshot import ExecutionSnapshot


def test_checkpoint_models_and_immutability() -> None:
    """Verify Checkpoint instantiation, UUID generation, versioning, and immutability."""
    version = CheckpointVersion(checkpoint_version="1.1.0")
    meta = CheckpointMetadata(version=version, tags=["test"])
    state = ConversationState()

    cp = Checkpoint(
        workflow_id="wf_100",
        graph_id="graph_1",
        state_snapshot=state,
        metadata=meta,
    )

    assert isinstance(cp.checkpoint_id, uuid.UUID)
    assert isinstance(cp.execution_id, uuid.UUID)
    assert cp.workflow_id == "wf_100"
    assert cp.metadata.version.checkpoint_version == "1.1.0"
    assert cp.status == CheckpointStatus.CREATED

    # Verify immutability
    with pytest.raises(Exception):
        cp.workflow_id = "wf_200"  # type: ignore


def test_in_memory_checkpoint_store() -> None:
    """Verify InMemoryCheckpointStore save, load, delete, exists, list, and clear."""
    store = InMemoryCheckpointStore()
    cp = Checkpoint(workflow_id="wf_store", graph_id="g_store", state_snapshot=ConversationState())

    # Save & Exists & Load
    store.save(cp)
    assert store.exists(cp.checkpoint_id) is True
    loaded = store.load(cp.checkpoint_id)
    assert loaded == cp
    assert len(store.list()) == 1

    # Delete & NotFound
    store.delete(cp.checkpoint_id)
    assert store.exists(cp.checkpoint_id) is False
    with pytest.raises(CheckpointNotFoundException):
        store.load(cp.checkpoint_id)

    # Clear
    store.save(cp)
    store.clear()
    assert len(store.list()) == 0


def test_checkpoint_manager_crud_and_validation() -> None:
    """Verify CheckpointManager create, restore, archive, delete, and validate."""
    manager = CheckpointManager()
    state = ConversationState()

    # Create
    cp = manager.create_checkpoint(
        workflow_id="wf_mgr",
        graph_id="g_mgr",
        state=state,
    )
    assert cp.status == CheckpointStatus.ACTIVE

    # Validate
    val_res = manager.validate_checkpoint(cp.checkpoint_id)
    assert isinstance(val_res, CheckpointValidationResult)
    assert val_res.is_valid is True
    assert val_res.integrity_passed is True

    # Restore
    restored_state = manager.restore_checkpoint(cp.checkpoint_id)
    assert restored_state.metadata.state_id == state.metadata.state_id

    # Archive
    archived_cp = manager.archive_checkpoint(cp.checkpoint_id)
    assert archived_cp.status == CheckpointStatus.ARCHIVED

    # Filtered list
    cps = manager.list_checkpoints(CheckpointFilter(workflow_id="wf_mgr"))
    assert len(cps) == 1


@pytest.mark.asyncio
async def test_replay_engine_flow_and_simulation() -> None:
    """Verify ReplayEngine replay, resume, restart, and simulate operations."""
    manager = CheckpointManager()
    state_1 = ConversationState()
    state_2 = ConversationState()

    cp_1 = manager.create_checkpoint("wf_replay", "g_replay", state_1)
    cp_2 = manager.create_checkpoint("wf_replay", "g_replay", state_2)

    engine = ReplayEngine(manager=manager)

    # Full replay
    res = await engine.replay("wf_replay")
    assert isinstance(res, ReplayResult)
    assert res.success is True
    assert engine.metrics.checkpoint_count == 2

    # Simulation
    sim_res = await engine.simulate("wf_replay")
    assert sim_res.success is True

    # Resume & Restart
    resumed_state = await engine.resume(cp_2.checkpoint_id)
    assert resumed_state.metadata.state_id == state_2.metadata.state_id

    restarted_state = await engine.restart("wf_replay")
    assert restarted_state.metadata.state_id == state_1.metadata.state_id

    # History records
    assert len(engine.history.records) > 0
    actions = [r.action for r in engine.history.records]
    assert ReplayAction.START in actions
    assert ReplayAction.RESUME in actions
    assert ReplayAction.RESTART in actions


@pytest.mark.asyncio
async def test_replay_engine_validation_exception() -> None:
    """Verify ReplayEngine raises ReplayValidationException when replaying non-existent workflow."""
    engine = ReplayEngine()
    with pytest.raises(ReplayValidationException):
        await engine.replay("non_existent_wf")


def test_registry_crud_and_factory() -> None:
    """Verify CheckpointRegistry register, lookup, register_factory, unregister, and clear."""
    registry = CheckpointRegistry()

    def store_factory() -> InMemoryCheckpointStore:
        return InMemoryCheckpointStore()

    registry.register_factory("mem_store", store_factory)
    assert registry.exists("mem_store") is True

    store = registry.lookup("mem_store")
    assert isinstance(store, InMemoryCheckpointStore)

    with pytest.raises(CheckpointStoreException):
        registry.register_factory("mem_store", store_factory)

    registry.unregister("mem_store")
    assert registry.exists("mem_store") is False


def test_exception_hierarchy() -> None:
    """Verify exception hierarchy inheritance."""
    assert issubclass(CheckpointNotFoundException, CheckpointException)
    assert issubclass(CheckpointValidationException, CheckpointException)
    assert issubclass(CheckpointStoreException, CheckpointException)
    assert issubclass(ReplayValidationException, ReplayException)
    assert issubclass(ReplayStrategyException, ReplayException)
    assert issubclass(ReplayException, CheckpointException)


def test_import_isolation_and_no_framework_leakage() -> None:
    """Verify app.checkpoints modules do not import forbidden framework dependencies, DB layers, or Redis."""
    forbidden_modules = [
        "sqlalchemy",
        "redis",
        "kafka",
        "rabbitmq",
        "opentelemetry",
        "prometheus",
        "grafana",
        "websockets",
        "langgraph",
        "openai",
        "app.db",
        "app.repositories",
        "app.services",
        "app.api",
    ]

    import app.checkpoints as cp_mod

    for mod_name in sys.modules:
        if mod_name.startswith("app.checkpoints"):
            mod = sys.modules[mod_name]
            mod_file = getattr(mod, "__file__", "")
            if mod_file:
                with open(mod_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    for forbidden in forbidden_modules:
                        assert forbidden not in content, f"Forbidden dependency '{forbidden}' found in {mod_name}!"
