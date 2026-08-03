import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.domain import ConversationNotFoundException, UserNotFoundException
from app.models.conversation import Conversation
from app.models.enums import ConversationSource, ConversationStatus
from app.repositories.conversation import ConversationRepository
from app.repositories.user import UserRepository
from app.services.base import BaseService


class ConversationService(BaseService):
    """Application domain service for Conversation sessions and dialogue lifecycle management."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.conversation_repo = ConversationRepository(session)
        self.user_repo = UserRepository(session)

    async def create_conversation(
        self,
        user_id: uuid.UUID,
        session_id: str,
        source: ConversationSource = ConversationSource.WEB,
        title: Optional[str] = None,
    ) -> Conversation:
        """Creates a new active conversation session after verifying user existence."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID '{user_id}' not found.")

        existing = await self.conversation_repo.get_by_session_id(session_id)
        if existing:
            return existing

        conversation = await self.conversation_repo.create(
            {
                "user_id": user_id,
                "session_id": session_id,
                "source": source,
                "title": title or "New Conversation",
                "status": ConversationStatus.ACTIVE,
            }
        )
        await self.commit()
        return conversation

    async def get_conversation(self, conversation_id: uuid.UUID) -> Conversation:
        """Retrieves a conversation session by UUID or raises ConversationNotFoundException."""
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise ConversationNotFoundException(f"Conversation with ID '{conversation_id}' not found.")
        return conversation

    async def get_latest_active_conversation(self, user_id: uuid.UUID) -> Conversation:
        """Retrieves the latest active conversation session for a user."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID '{user_id}' not found.")

        conversation = await self.conversation_repo.get_latest_active(user_id)
        if not conversation:
            raise ConversationNotFoundException(f"No active conversation session found for user '{user_id}'.")
        return conversation

    async def archive_conversation(self, conversation_id: uuid.UUID) -> Conversation:
        """Archives an active conversation session and sets its completion timestamp."""
        await self.get_conversation(conversation_id)

        archived = await self.conversation_repo.update(
            conversation_id,
            {
                "status": ConversationStatus.ARCHIVED,
                "ended_at": datetime.now(timezone.utc),
            },
        )
        if not archived:
            raise ConversationNotFoundException(f"Conversation with ID '{conversation_id}' not found.")
        await self.commit()
        return archived
