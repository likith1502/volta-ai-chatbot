from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    """Base application service providing session management and transaction ownership helpers."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def commit(self) -> None:
        """Commits the active database session transaction."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Rolls back the active database session transaction."""
        await self.session.rollback()
