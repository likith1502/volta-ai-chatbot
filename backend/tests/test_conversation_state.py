import ast
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import pytest

from app.context import (
    ConversationData,
    ConversationState,
    ConversationStateManager,
    ConversationStatus,
    ExecutionMode,
    ExecutionState,
    MemoryState,
    NodeType,
    RuntimeState,
    StateMetadata,
    WorkflowEvent,
    WorkflowEventType,
    WorkflowStatus,
)


def test_conversation_state_default_initialization():
    """Verify default instantiation of ConversationState and sub-models."""
    state = ConversationState()

    assert isinstance(state.state_id, uuid.UUID)
    assert state.parent_state_id is None
    assert isinstance(state.conversation_id, uuid.UUID)
    assert state.user_id is None
    assert state.current_message is None
    assert state.chat_history == []
    assert state.detected_intent is None
    assert state.extracted_entities == {}
    assert state.tool_calls == []
    assert state.tool_results == []
    assert state.executed_nodes == []
    assert state.workflow_step == "initialized"
    assert state.workflow_status == WorkflowStatus.PENDING
    assert state.errors == []

    # Verify version defaults & metadata
    assert state.state_version == 1
    assert state.metadata.version == 1
    assert isinstance(state.metadata.correlation_id, uuid.UUID)
    assert state.runtime.checkpoint_id is None
    assert state.execution.node_results == {}


def test_conversation_state_serialization_round_trip():
    """Verify serialization to dictionary/JSON and deserialization round-trip integrity."""
    test_id = uuid.uuid4()
    original_state = ConversationState(
        conversation=ConversationData(
            conversation_id=test_id,
            user_id="user_123",
            current_message={"role": "user", "content": "Book an EV charger slot"},
            history=[{"role": "user", "content": "Hello"}],
        ),
        runtime=RuntimeState(
            workflow_step="intent_detection",
            workflow_status=WorkflowStatus.RUNNING,
            execution_mode=ExecutionMode.ASYNC,
        ),
        execution=ExecutionState(
            tool_calls=[{"name": "search_chargers", "args": {"location": "Downtown"}}],
            node_results={"intent": {"name": "book_charger", "confidence": 0.98}},
            executed_nodes=["input_node", "intent_detection"],
        ),
        memory=MemoryState(
            detected_intent={"name": "book_charger"},
            extracted_entities={"location": "Downtown"},
        ),
    )

    # State to Dict
    state_dict = original_state.to_dict()
    assert isinstance(state_dict, dict)
    assert state_dict["conversation"]["user_id"] == "user_123"
    assert state_dict["runtime"]["workflow_step"] == "intent_detection"

    # Dict to JSON string
    json_str = json.dumps(state_dict)
    assert isinstance(json_str, str)

    # JSON string back to Dict and model
    deserialized_dict = json.loads(json_str)
    reconstructed_state = ConversationState.from_dict(deserialized_dict)

    assert reconstructed_state.conversation_id == test_id
    assert reconstructed_state.user_id == "user_123"
    assert reconstructed_state.workflow_step == "intent_detection"
    assert reconstructed_state.workflow_status == WorkflowStatus.RUNNING
    assert reconstructed_state.execution_mode == ExecutionMode.ASYNC
    assert reconstructed_state.executed_nodes == ["input_node", "intent_detection"]
    assert reconstructed_state.detected_intent == {"name": "book_charger"}
    assert reconstructed_state.execution.node_results == {
        "intent": {"name": "book_charger", "confidence": 0.98}
    }


def test_conversation_state_immutability_and_lineage_with_update():
    """Verify with_update() creates a new object, maintains parent lineage, deep-copies dictionaries, and leaves original state untouched."""
    initial_state = ConversationState(
        conversation=ConversationData(user_id="user_original"),
        runtime=RuntimeState(workflow_step="step_1"),
    )

    initial_state_id = initial_state.state_id
    original_user_id = initial_state.user_id
    original_step = initial_state.workflow_step
    original_updated_at = initial_state.metadata.updated_at

    # Execute update
    updated_state = initial_state.with_update(
        user_id="user_updated",
        workflow_step="step_2",
        detected_intent={"intent": "greeting"},
        node_results={"greeting_node": {"output": "Hi"}},
    )

    # Verify state lineage and distinct state_id
    assert updated_state.state_id != initial_state_id
    assert updated_state.parent_state_id == initial_state_id

    # Verify updated_state is a distinct object
    assert updated_state is not initial_state
    assert updated_state.conversation is not initial_state.conversation
    assert updated_state.runtime is not initial_state.runtime

    # Verify original state was NOT modified
    assert initial_state.user_id == original_user_id
    assert initial_state.workflow_step == original_step
    assert initial_state.detected_intent is None
    assert initial_state.execution.node_results == {}

    # Verify updated state has new values and updated node order
    assert updated_state.user_id == "user_updated"
    assert updated_state.workflow_step == "step_2"
    assert updated_state.executed_nodes == ["step_2"]
    assert updated_state.detected_intent == {"intent": "greeting"}
    assert updated_state.execution.node_results == {"greeting_node": {"output": "Hi"}}
    assert updated_state.metadata.updated_at >= original_updated_at


def test_workflow_event_model():
    """Verify WorkflowEvent instantiation and serialization."""
    cid = uuid.uuid4()
    event = WorkflowEvent(
        event_type=WorkflowEventType.WORKFLOW_STARTED,
        conversation_id=cid,
        payload={"trigger": "user_input"},
    )

    assert isinstance(event.event_id, uuid.UUID)
    assert event.event_type == WorkflowEventType.WORKFLOW_STARTED
    assert event.conversation_id == cid
    assert event.payload == {"trigger": "user_input"}

    event_dict = event.model_dump(mode="json")
    assert event_dict["event_type"] == "workflow_started"
    assert event_dict["conversation_id"] == str(cid)


def test_enums_validity():
    """Verify enum options and values across types and events."""
    assert WorkflowStatus.RUNNING.value == "running"
    assert ConversationStatus.ACTIVE.value == "active"
    assert NodeType.LLM.value == "llm"
    assert ExecutionMode.STREAMING.value == "streaming"
    assert WorkflowEventType.TOOL_STARTED.value == "tool_started"


@pytest.mark.asyncio
async def test_state_manager_interface_enforcement():
    """Verify ConversationStateManager cannot be instantiated directly and enforcing concrete implementations."""
    with pytest.raises(TypeError):
        # Directly instantiating abstract interface must fail
        ConversationStateManager()

    class DummyStateManager(ConversationStateManager):
        def __init__(self):
            self._store: dict[str, ConversationState] = {}

        async def create_state(
            self,
            conversation_id: Optional[uuid.UUID | str] = None,
            user_id: Optional[str] = None,
            **kwargs: Any,
        ) -> ConversationState:
            cid = uuid.UUID(str(conversation_id)) if conversation_id else uuid.uuid4()
            state = ConversationState(
                conversation=ConversationData(conversation_id=cid, user_id=user_id)
            )
            self._store[str(cid)] = state
            return state

        async def load_state(self, conversation_id: uuid.UUID | str) -> Optional[ConversationState]:
            return self._store.get(str(conversation_id))

        async def save_state(self, state: ConversationState) -> None:
            self._store[str(state.conversation_id)] = state

        async def update_state(
            self, conversation_id: uuid.UUID | str, updates: dict[str, Any]
        ) -> ConversationState:
            current = self._store[str(conversation_id)]
            updated = current.with_update(**updates)
            self._store[str(conversation_id)] = updated
            return updated

        async def clear_state(self, conversation_id: uuid.UUID | str) -> None:
            self._store.pop(str(conversation_id), None)

        async def exists(self, conversation_id: uuid.UUID | str) -> bool:
            return str(conversation_id) in self._store

        async def delete(self, conversation_id: uuid.UUID | str) -> None:
            self._store.pop(str(conversation_id), None)

        async def list_states(self) -> list[uuid.UUID | str]:
            return list(self._store.keys())

    # Instantiate concrete dummy manager
    manager = DummyStateManager()
    state = await manager.create_state(user_id="usr_test")
    cid = state.conversation_id

    assert await manager.exists(cid) is True
    assert (await manager.load_state(cid)).user_id == "usr_test"

    updated = await manager.update_state(cid, {"workflow_step": "completed"})
    assert updated.workflow_step == "completed"

    states_list = await manager.list_states()
    assert str(cid) in states_list

    await manager.delete(cid)
    assert await manager.exists(cid) is False


def test_import_isolation():
    """Verify that backend/app/context/ has zero dependencies on LLM providers, DB, Redis, or LangGraph."""
    forbidden_keywords = [
        "langgraph",
        "openai",
        "anthropic",
        "google",
        "redis",
        "sqlalchemy",
        "fastapi",
    ]

    import app.context.events as events_mod
    import app.context.state as state_mod
    import app.context.state_manager as sm_mod
    import app.context.types as types_mod

    modules_to_check = [types_mod, events_mod, state_mod, sm_mod]

    for mod in modules_to_check:
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
