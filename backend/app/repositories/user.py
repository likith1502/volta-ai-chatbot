from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Domain repository for User account entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_email(
        self, email: str, include_deleted: bool = False
    ) -> User | None:
        """Retrieves a user by unique email address."""
        stmt = select(User).where(User.email == email)
        stmt = self._apply_soft_delete_filter(stmt, include_deleted)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_phone(
        self, phone_number: str, include_deleted: bool = False
    ) -> User | None:
        """Retrieves a user by phone number."""
        stmt = select(User).where(User.phone_number == phone_number)
        stmt = self._apply_soft_delete_filter(stmt, include_deleted)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
