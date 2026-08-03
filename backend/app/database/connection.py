from typing import Optional
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from app.config.settings import settings

_engine: Optional[AsyncEngine] = None


def create_engine_instance(database_url: Optional[str] = None) -> AsyncEngine:
    """Creates a new configured AsyncEngine instance."""
    url = database_url or settings.get_database_url()
    return create_async_engine(
        url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_recycle=settings.DATABASE_POOL_RECYCLE,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
    )


def get_engine(database_url: Optional[str] = None) -> AsyncEngine:
    """Returns a singleton AsyncEngine instance using lazy initialization."""
    global _engine

    if database_url:
        return create_engine_instance(database_url)

    if _engine is None:
        _engine = create_engine_instance()

    return _engine


async def dispose_engine() -> None:
    """Closes and disposes of the active AsyncEngine pool."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
