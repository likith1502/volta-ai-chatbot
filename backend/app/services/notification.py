import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.domain import NotificationNotFoundException, UserNotFoundException
from app.models.enums import NotificationType
from app.models.notification import Notification
from app.repositories.base import BaseRepository
from app.repositories.user import UserRepository
from app.services.base import BaseService


class NotificationService(BaseService):
    """Application domain service for User Notifications and alert delivery management."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.notification_repo = BaseRepository(Notification, session)
        self.user_repo = UserRepository(session)

    async def create_notification(
        self,
        user_id: uuid.UUID,
        notification_type: NotificationType,
        title: str,
        body: str,
    ) -> Notification:
        """Creates and persists a new user notification after validating user existence."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID '{user_id}' not found.")

        notification = await self.notification_repo.create(
            {
                "user_id": user_id,
                "notification_type": notification_type,
                "title": title,
                "body": body,
                "is_read": False,
                "delivery_status": "sent",
            }
        )
        await self.commit()
        return notification

    async def mark_as_read(self, notification_id: uuid.UUID) -> Notification:
        """Marks a notification as read and records the read timestamp."""
        notification = await self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise NotificationNotFoundException(f"Notification with ID '{notification_id}' not found.")

        updated = await self.notification_repo.update(
            notification_id,
            {
                "is_read": True,
                "read_at": datetime.now(timezone.utc),
            },
        )
        if not updated:
            raise NotificationNotFoundException(f"Notification with ID '{notification_id}' not found.")

        await self.commit()
        return updated
