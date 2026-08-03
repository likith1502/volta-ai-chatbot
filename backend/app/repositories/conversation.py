import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.enums import ConversationStatus
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """Domain repository for Conversation session entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Conversation, session)

    async def get_latest_active(self, user_id: uuid.UUID) -> Conversation | None:
        """Retrieves the most recent active conversation session for a user."""
        stmt = (
            select(Conversation)
            .where(
                Conversation.user_id == user_id,
                Conversation.status == ConversationStatus.ACTIVE,
            )
            .order_by(Conversation.started_at.desc())
            .limit(1)
        )
        stmt = self._apply_soft_delete_filter(stmt, include_deleted=False)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_session_id(self, session_id: str, include_deleted: bool = False) -> Conversation | None:
        """Retrieves a conversation by external session ID."""
        stmt = select(Conversation).where(Conversation.session_id == session_id)
        stmt = self._apply_soft_delete_filter(stmt, include_deleted)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
