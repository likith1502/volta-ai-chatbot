import uuid
from typing import Any, Generic, Type, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic asynchronous repository providing reusable CRUD data access operations."""

    def __init__(self, model_class: Type[T], session: AsyncSession) -> None:
        self.model_class = model_class
        self.session = session

    def _apply_soft_delete_filter(
        self, stmt: Select, include_deleted: bool = False
    ) -> Select:
        """Centralized query helper to apply soft-delete filtering if applicable."""
        if not include_deleted and hasattr(self.model_class, "is_deleted"):
            return stmt.where(self.model_class.is_deleted == False)  # noqa: E712
        return stmt

    async def get_by_id(self, id: uuid.UUID, include_deleted: bool = False) -> T | None:
        """Retrieves a single model instance by its primary key UUID."""
        stmt = select(self.model_class).where(self.model_class.id == id)
        stmt = self._apply_soft_delete_filter(stmt, include_deleted)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        offset: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[T]:
        """Lists model instances with offset/limit pagination support."""
        stmt = select(self.model_class)
        stmt = self._apply_soft_delete_filter(stmt, include_deleted)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, attributes: dict[str, Any]) -> T:
        """Instantiates and persists a new model instance in the active session."""
        instance = self.model_class(**attributes)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: uuid.UUID, attributes: dict[str, Any]) -> T | None:
        """Updates attributes of an existing model instance."""
        instance = await self.get_by_id(id, include_deleted=True)
        if not instance:
            return None
        for key, value in attributes.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: uuid.UUID, hard: bool = False) -> bool:
        """Deletes a model instance using soft delete by default or hard physical deletion."""
        instance = await self.get_by_id(id, include_deleted=True)
        if not instance:
            return False
        if (
            not hard
            and hasattr(instance, "soft_delete")
            and callable(getattr(instance, "soft_delete"))
        ):
            instance.soft_delete()
        else:
            await self.session.delete(instance)
        await self.session.flush()
        return True

    async def exists(self, id: uuid.UUID, include_deleted: bool = False) -> bool:
        """Checks whether a record exists for the specified primary key UUID."""
        stmt = select(func.count(self.model_class.id)).where(self.model_class.id == id)
        stmt = self._apply_soft_delete_filter(stmt, include_deleted)
        result = await self.session.execute(stmt)
        count_val = result.scalar() or 0
        return count_val > 0

    async def count(self, include_deleted: bool = False) -> int:
        """Counts the total number of records for the model class."""
        stmt = select(func.count(self.model_class.id))
        stmt = self._apply_soft_delete_filter(stmt, include_deleted)
        result = await self.session.execute(stmt)
        return result.scalar() or 0
