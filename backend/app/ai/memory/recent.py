import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.memory.base import MemoryStrategy
from app.models.memory import Memory


class RecentConversationStrategy(MemoryStrategy):
    """Retrieves recent active memories recorded for a conversation session."""

    async def retrieve_memories(
        self,
        session: AsyncSession,
        conversation_id: uuid.UUID,
        limit: int = 10,
    ) -> list[Memory]:
        """Fetches up to `limit` active memory records ordered by creation date."""
        stmt = (
            select(Memory)
            .where(
                Memory.conversation_id == conversation_id,
                Memory.is_deleted == False,  # noqa: E712
            )
            .order_by(Memory.created_at.desc())
            .limit(limit)
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())
