import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.domain import UserAlreadyExistsError, UserNotFoundError
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.base import BaseService


class UserService(BaseService):
    """Application domain service for User account operations and lifecycle workflows."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.user_repo = UserRepository(session)

    async def create_user(
        self,
        full_name: str,
        email: str,
        phone_number: Optional[str] = None,
        preferred_language: str = "en",
    ) -> User:
        """Creates and persists a new user account if the email is not already registered."""
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError(
                f"User with email '{email}' already exists."
            )

        user = await self.user_repo.create(
            {
                "full_name": full_name,
                "email": email,
                "phone_number": phone_number,
                "preferred_language": preferred_language,
            }
        )
        await self.commit()
        return user

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        """Retrieves a user by primary key UUID or raises UserNotFoundError."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID '{user_id}' not found.")
        return user

    async def get_user_by_email(self, email: str) -> User:
        """Retrieves a user by unique email address or raises UserNotFoundError."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise UserNotFoundError(f"User with email '{email}' not found.")
        return user

    async def update_profile(
        self, user_id: uuid.UUID, attributes: dict[str, Any]
    ) -> User:
        """Updates user profile attributes after validating email uniqueness if updated."""
        await self.get_user_by_id(user_id)

        if "email" in attributes:
            new_email = attributes["email"]
            existing = await self.user_repo.get_by_email(new_email)
            if existing and existing.id != user_id:
                raise UserAlreadyExistsError(
                    f"User with email '{new_email}' already exists."
                )

        updated_user = await self.user_repo.update(user_id, attributes)
        if not updated_user:
            raise UserNotFoundError(f"User with ID '{user_id}' not found.")
        await self.commit()
        return updated_user

    async def deactivate_user(self, user_id: uuid.UUID, hard: bool = False) -> bool:
        """Deactivates (soft deletes) or hard deletes a user account."""
        await self.get_user_by_id(user_id)
        success = await self.user_repo.delete(user_id, hard=hard)
        await self.commit()
        return success
