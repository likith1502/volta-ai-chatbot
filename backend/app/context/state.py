import copy
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.context.types import ExecutionMode, WorkflowStatus


class StateMetadata(BaseModel):
    """Metadata schema tracking state lineage, request tracing, and timestamps."""

    state_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    parent_state_id: Optional[uuid.UUID] = None
    correlation_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    request_id: Optional[uuid.UUID] = None
    session_id: Optional[uuid.UUID] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1


class ConversationData(BaseModel):
    """Conversational payload parameters including history and current user turn."""

    conversation_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: Optional[str] = None
    current_message: Optional[dict[str, Any]] = None
    history: list[dict[str, Any]] = Field(default_factory=list)


class RuntimeState(BaseModel):
    """Runtime execution metrics, active node step, status, and checkpoint identifiers."""

    workflow_step: str = "initialized"
    workflow_status: WorkflowStatus = WorkflowStatus.PENDING
    execution_mode: ExecutionMode = ExecutionMode.SYNC
    checkpoint_id: Optional[uuid.UUID] = None


class ExecutionState(BaseModel):
    """Execution state tracking tool calls, tool results, node outputs, node order, and error logs."""

    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    tool_results: list[dict[str, Any]] = Field(default_factory=list)
    node_results: dict[str, Any] = Field(default_factory=dict)
    executed_nodes: list[str] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)


class MemoryState(BaseModel):
    """Contextual memory store tracking short/long-term memory, intents, and entities."""

    short_term_memory: dict[str, Any] = Field(default_factory=dict)
    long_term_memory: dict[str, Any] = Field(default_factory=dict)
    detected_intent: Optional[dict[str, Any]] = None
    extracted_entities: dict[str, Any] = Field(default_factory=dict)


class ConversationState(BaseModel):
    """Strongly-typed, immutable-friendly single source of truth for workflow state."""

    state_version: int = 1
    metadata: StateMetadata = Field(default_factory=StateMetadata)
    conversation: ConversationData = Field(default_factory=ConversationData)
    runtime: RuntimeState = Field(default_factory=RuntimeState)
    execution: ExecutionState = Field(default_factory=ExecutionState)
    memory: MemoryState = Field(default_factory=MemoryState)

    # Top-level property getters for convenient backwards compatibility and access
    @property
    def state_id(self) -> uuid.UUID:
        return self.metadata.state_id

    @property
    def parent_state_id(self) -> Optional[uuid.UUID]:
        return self.metadata.parent_state_id

    @property
    def conversation_id(self) -> uuid.UUID:
        return self.conversation.conversation_id

    @property
    def user_id(self) -> Optional[str]:
        return self.conversation.user_id

    @property
    def current_message(self) -> Optional[dict[str, Any]]:
        return self.conversation.current_message

    @property
    def chat_history(self) -> list[dict[str, Any]]:
        return self.conversation.history

    @property
    def detected_intent(self) -> Optional[dict[str, Any]]:
        return self.memory.detected_intent

    @property
    def extracted_entities(self) -> dict[str, Any]:
        return self.memory.extracted_entities

    @property
    def tool_calls(self) -> list[dict[str, Any]]:
        return self.execution.tool_calls

    @property
    def tool_results(self) -> list[dict[str, Any]]:
        return self.execution.tool_results

    @property
    def executed_nodes(self) -> list[str]:
        return self.execution.executed_nodes

    @property
    def workflow_step(self) -> str:
        return self.runtime.workflow_step

    @property
    def workflow_status(self) -> WorkflowStatus:
        return self.runtime.workflow_status

    @property
    def execution_mode(self) -> ExecutionMode:
        return self.runtime.execution_mode

    @property
    def checkpoint_id(self) -> Optional[uuid.UUID]:
        return self.runtime.checkpoint_id

    @property
    def errors(self) -> list[dict[str, Any]]:
        return self.execution.errors

    def with_update(self, **kwargs: Any) -> "ConversationState":
        """
        Creates and returns a new ConversationState instance with the provided updates.
        Does NOT mutate the current instance (enforces immutability).
        Deep-copies nested structures, assigns parent_state_id to self.state_id,
        generates a new state_id, and refreshes updated_at timestamp.
        """
        # Deep copy dictionary model dump
        data = copy.deepcopy(self.model_dump())

        # Sub-model top-level overrides
        if "metadata" in kwargs:
            data["metadata"] = (
                kwargs["metadata"].model_dump()
                if isinstance(kwargs["metadata"], BaseModel)
                else kwargs["metadata"]
            )
        if "conversation" in kwargs:
            data["conversation"] = (
                kwargs["conversation"].model_dump()
                if isinstance(kwargs["conversation"], BaseModel)
                else kwargs["conversation"]
            )
        if "runtime" in kwargs:
            data["runtime"] = (
                kwargs["runtime"].model_dump()
                if isinstance(kwargs["runtime"], BaseModel)
                else kwargs["runtime"]
            )
        if "execution" in kwargs:
            data["execution"] = (
                kwargs["execution"].model_dump()
                if isinstance(kwargs["execution"], BaseModel)
                else kwargs["execution"]
            )
        if "memory" in kwargs:
            data["memory"] = (
                kwargs["memory"].model_dump()
                if isinstance(kwargs["memory"], BaseModel)
                else kwargs["memory"]
            )

        # Handle shortcut field updates
        if "user_id" in kwargs:
            data["conversation"]["user_id"] = kwargs["user_id"]
        if "current_message" in kwargs:
            data["conversation"]["current_message"] = kwargs["current_message"]
        if "chat_history" in kwargs or "history" in kwargs:
            data["conversation"]["history"] = kwargs.get(
                "chat_history", kwargs.get("history")
            )
        if "workflow_step" in kwargs:
            data["runtime"]["workflow_step"] = kwargs["workflow_step"]
            if kwargs["workflow_step"] not in data["execution"]["executed_nodes"]:
                data["execution"]["executed_nodes"].append(kwargs["workflow_step"])
        if "workflow_status" in kwargs:
            data["runtime"]["workflow_status"] = kwargs["workflow_status"]
        if "execution_mode" in kwargs:
            data["runtime"]["execution_mode"] = kwargs["execution_mode"]
        if "checkpoint_id" in kwargs:
            data["runtime"]["checkpoint_id"] = kwargs["checkpoint_id"]
        if "tool_calls" in kwargs:
            data["execution"]["tool_calls"] = kwargs["tool_calls"]
        if "tool_results" in kwargs:
            data["execution"]["tool_results"] = kwargs["tool_results"]
        if "node_results" in kwargs:
            data["execution"]["node_results"] = kwargs["node_results"]
        if "executed_nodes" in kwargs:
            data["execution"]["executed_nodes"] = kwargs["executed_nodes"]
        if "errors" in kwargs:
            data["execution"]["errors"] = kwargs["errors"]
        if "detected_intent" in kwargs:
            data["memory"]["detected_intent"] = kwargs["detected_intent"]
        if "extracted_entities" in kwargs:
            data["memory"]["extracted_entities"] = kwargs["extracted_entities"]
        if "short_term_memory" in kwargs:
            data["memory"]["short_term_memory"] = kwargs["short_term_memory"]
        if "long_term_memory" in kwargs:
            data["memory"]["long_term_memory"] = kwargs["long_term_memory"]
        if "state_version" in kwargs:
            data["state_version"] = kwargs["state_version"]

        # Lineage update: new state_id, link parent_state_id to current state_id
        if "state_id" in kwargs:
            data["metadata"]["state_id"] = kwargs["state_id"]
        else:
            data["metadata"]["parent_state_id"] = self.metadata.state_id
            data["metadata"]["state_id"] = uuid.uuid4()

        if "parent_state_id" in kwargs:
            data["metadata"]["parent_state_id"] = kwargs["parent_state_id"]

        # Touch timestamp
        data["metadata"]["updated_at"] = datetime.now(timezone.utc)

        return ConversationState.model_validate(data)

    def to_dict(self) -> dict[str, Any]:
        """Serializes the state to a JSON-compatible dictionary representation."""
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConversationState":
        """Deserializes state from a dictionary representation."""
        return cls.model_validate(data)
