import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.saved_location import SavedLocation
from app.repositories.base import BaseRepository


class SavedLocationRepository(BaseRepository[SavedLocation]):
    """Domain repository for SavedLocation entities providing multi-tenant scoped access."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(SavedLocation, session)

    async def get_by_user_and_label(
        self,
        user_id: uuid.UUID,
        label: str,
        include_deleted: bool = False,
    ) -> SavedLocation | None:
        """Retrieves a saved location for a user matching label case-insensitively."""
        normalized_query = label.strip().lower()
        stmt = select(SavedLocation).where(
            SavedLocation.user_id == user_id,
            func.lower(SavedLocation.label) == normalized_query,
        )
        stmt = self._apply_soft_delete_filter(stmt, include_deleted)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        offset: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[SavedLocation]:
        """Lists active saved locations belonging strictly to the specified user."""
        stmt = select(SavedLocation).where(SavedLocation.user_id == user_id)
        stmt = self._apply_soft_delete_filter(stmt, include_deleted)
        stmt = stmt.order_by(SavedLocation.created_at.asc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id_and_user(
        self,
        id: uuid.UUID,
        user_id: uuid.UUID,
        include_deleted: bool = False,
    ) -> SavedLocation | None:
        """Retrieves a saved location by primary key scoped strictly to owner user ID."""
        stmt = select(SavedLocation).where(
            SavedLocation.id == id,
            SavedLocation.user_id == user_id,
        )
        stmt = self._apply_soft_delete_filter(stmt, include_deleted)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
