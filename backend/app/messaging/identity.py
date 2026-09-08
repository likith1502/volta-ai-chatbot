import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.messaging.models import ChannelType
from app.models.user import User
from app.repositories.user import UserRepository

logger = logging.getLogger("app.messaging.identity")


class ChannelIdentityResolver:
    """Resolves external messaging user IDs and phone numbers to canonical Volta User entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def resolve_or_create_user(
        self,
        channel: ChannelType,
        external_user_id: str,
        sender_name: str | None = None,
    ) -> User:
        """Resolves an existing Volta User or creates a new stable record for the channel identity."""
        cleaned_id = external_user_id.strip()

        if channel == ChannelType.WHATSAPP:
            # 1. Try finding existing user by verified phone number
            user = await self.user_repo.get_by_phone(cleaned_id)
            if user:
                return user

            # 2. Try finding by deterministic internal channel email
            email = f"wa_{cleaned_id}@volta.internal"
            user = await self.user_repo.get_by_email(email)
            if user:
                return user

            # 3. Create new user entity for WhatsApp customer
            logger.info("Creating new Volta user for WhatsApp identity: %s", cleaned_id)
            user = await self.user_repo.create(
                {
                    "full_name": sender_name or f"WhatsApp User {cleaned_id}",
                    "email": email,
                    "phone_number": cleaned_id,
                    "is_active": True,
                }
            )
            return user

        elif channel == ChannelType.TELEGRAM:
            # 1. Try finding by deterministic internal channel email
            email = f"tg_{cleaned_id}@volta.internal"
            user = await self.user_repo.get_by_email(email)
            if user:
                return user

            # 2. Create new user entity for Telegram customer
            logger.info("Creating new Volta user for Telegram identity: %s", cleaned_id)
            user = await self.user_repo.create(
                {
                    "full_name": sender_name or f"Telegram User {cleaned_id}",
                    "email": email,
                    "phone_number": None,
                    "is_active": True,
                }
            )
            return user

        else:
            raise ValueError(f"Unsupported messaging channel: {channel}")

    @staticmethod
    def get_session_id(channel: ChannelType, external_user_id: str) -> str:
        """Derives a stable, isolated conversation session identifier for multi-turn dialogue."""
        cleaned_id = external_user_id.strip()
        return f"{channel.value}_{cleaned_id}"
