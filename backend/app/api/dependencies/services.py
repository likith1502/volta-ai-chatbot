from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.services.booking import BookingService
from app.services.conversation import ConversationService
from app.services.notification import NotificationService
from app.services.recommendation import RecommendationService
from app.services.user import UserService


def get_user_service(session: AsyncSession = Depends(get_db_session)) -> UserService:
    """Dependency provider yielding a UserService instance."""
    return UserService(session)


def get_conversation_service(session: AsyncSession = Depends(get_db_session)) -> ConversationService:
    """Dependency provider yielding a ConversationService instance."""
    return ConversationService(session)


def get_recommendation_service(session: AsyncSession = Depends(get_db_session)) -> RecommendationService:
    """Dependency provider yielding a RecommendationService instance."""
    return RecommendationService(session)


def get_booking_service(session: AsyncSession = Depends(get_db_session)) -> BookingService:
    """Dependency provider yielding a BookingService instance."""
    return BookingService(session)


def get_notification_service(session: AsyncSession = Depends(get_db_session)) -> NotificationService:
    """Dependency provider yielding a NotificationService instance."""
    return NotificationService(session)
