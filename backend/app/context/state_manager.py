import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional

from app.context.state import ConversationState


class ConversationStateManager(ABC):
    """Abstract interface contract for persisting, loading, and managing ConversationState."""

    @abstractmethod
    async def create_state(
        self,
        conversation_id: Optional[uuid.UUID | str] = None,
        user_id: Optional[str] = None,
        **kwargs: Any,
    ) -> ConversationState:
        """Initializes and returns a new ConversationState object."""
        pass

    @abstractmethod
    async def load_state(
        self, conversation_id: uuid.UUID | str
    ) -> Optional[ConversationState]:
        """Retrieves active conversation state by conversation ID or returns None if omitted."""
        pass

    @abstractmethod
    async def save_state(self, state: ConversationState) -> None:
        """Persists or updates the conversation state object."""
        pass

    @abstractmethod
    async def update_state(
        self, conversation_id: uuid.UUID | str, updates: dict[str, Any]
    ) -> ConversationState:
        """Applies updates to an existing conversation state and persists the result."""
        pass

    @abstractmethod
    async def clear_state(self, conversation_id: uuid.UUID | str) -> None:
        """Clears or invalidates state for a conversation session."""
        pass

    @abstractmethod
    async def exists(self, conversation_id: uuid.UUID | str) -> bool:
        """Checks if a state record exists for the given conversation ID."""
        pass

    @abstractmethod
    async def delete(self, conversation_id: uuid.UUID | str) -> None:
        """Deletes state entry for the given conversation ID."""
        pass

    @abstractmethod
    async def list_states(self) -> list[uuid.UUID | str]:
        """Returns a list of all active conversation state identifiers."""
        pass
