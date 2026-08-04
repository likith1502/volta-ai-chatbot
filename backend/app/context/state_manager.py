import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


class ConversationState(BaseModel):
    """Data transfer object representing the runtime conversation state for workflow orchestration."""

    conversation_id: uuid.UUID
    session_id: str
    current_step: str = "initialized"
    status: str = "active"
    session_variables: dict[str, Any] = Field(default_factory=dict)
    pending_tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    temporary_runtime_state: dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConversationStateManager(ABC):
    """Abstract manager interface for retrieving, persisting, and clearing session workflow states."""

    @abstractmethod
    async def get_state(self, conversation_id: uuid.UUID) -> Optional[ConversationState]:
        """Retrieves active conversation state or returns None if omitted."""
        pass

    @abstractmethod
    async def save_state(self, state: ConversationState) -> None:
        """Persists or updates the conversation state payload."""
        pass

    @abstractmethod
    async def clear_state(self, conversation_id: uuid.UUID) -> None:
        """Clears or invalidates state for a completed conversation session."""
        pass
