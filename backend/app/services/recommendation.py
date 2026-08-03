import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.domain import ConversationClosedException, ConversationNotFoundException, RecommendationNotFoundException
from app.models.enums import ConversationStatus, RecommendationStatus
from app.models.recommendation import Recommendation
from app.repositories.conversation import ConversationRepository
from app.repositories.recommendation import RecommendationRepository
from app.services.base import BaseService


class RecommendationService(BaseService):
    """Application domain service for AI ride recommendation generation and lifecycle operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.recommendation_repo = RecommendationRepository(session)
        self.conversation_repo = ConversationRepository(session)

    async def create_recommendation(
        self,
        conversation_id: uuid.UUID,
        recommendation_type: str,
        recommendation_data: dict[str, Any],
        confidence_score: float = 1.0,
        ranking: int = 1,
    ) -> Recommendation:
        """Creates and persists a new recommendation for an active conversation session."""
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise ConversationNotFoundException(f"Conversation with ID '{conversation_id}' not found.")

        if conversation.status != ConversationStatus.ACTIVE:
            raise ConversationClosedException("Cannot attach recommendations to a closed or archived conversation.")

        recommendation = await self.recommendation_repo.create(
            {
                "conversation_id": conversation_id,
                "recommendation_type": recommendation_type,
                "recommendation_data": recommendation_data,
                "status": RecommendationStatus.PENDING,
                "confidence_score": confidence_score,
                "ranking": ranking,
            }
        )
        await self.commit()
        return recommendation

    async def get_recommendation(self, recommendation_id: uuid.UUID) -> Recommendation:
        """Retrieves a recommendation by primary key UUID or raises RecommendationNotFoundException."""
        recommendation = await self.recommendation_repo.get_by_id(recommendation_id)
        if not recommendation:
            raise RecommendationNotFoundException(f"Recommendation with ID '{recommendation_id}' not found.")
        return recommendation

    async def get_active_recommendations(self, conversation_id: uuid.UUID) -> list[Recommendation]:
        """Retrieves all pending/active recommendations for a conversation session."""
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise ConversationNotFoundException(f"Conversation with ID '{conversation_id}' not found.")

        return await self.recommendation_repo.get_active_recommendations(conversation_id)

    async def expire_recommendation(self, recommendation_id: uuid.UUID) -> Recommendation:
        """Marks a pending recommendation as EXPIRED."""
        await self.get_recommendation(recommendation_id)

        expired = await self.recommendation_repo.update(
            recommendation_id,
            {"status": RecommendationStatus.EXPIRED},
        )
        if not expired:
            raise RecommendationNotFoundException(f"Recommendation with ID '{recommendation_id}' not found.")
        await self.commit()
        return expired
