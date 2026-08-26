from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.connection import get_engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Returns an async_sessionmaker factory bound to the active singleton engine."""
    return async_sessionmaker(
        bind=get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for injecting transactional AsyncSession instances."""
    sessionmaker_factory = get_sessionmaker()
    async with sessionmaker_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
