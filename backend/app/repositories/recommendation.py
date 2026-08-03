import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import RecommendationStatus
from app.models.recommendation import Recommendation
from app.repositories.base import BaseRepository


class RecommendationRepository(BaseRepository[Recommendation]):
    """Domain repository for Recommendation entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Recommendation, session)

    async def get_active_recommendations(self, conversation_id: uuid.UUID) -> list[Recommendation]:
        """Retrieves all pending/active recommendations generated during a conversation session."""
        stmt = (
            select(Recommendation)
            .where(
                Recommendation.conversation_id == conversation_id,
                Recommendation.status == RecommendationStatus.PENDING,
            )
            .order_by(Recommendation.ranking.asc())
        )
        stmt = self._apply_soft_delete_filter(stmt, include_deleted=False)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
