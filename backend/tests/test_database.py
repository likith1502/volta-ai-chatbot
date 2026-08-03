import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from app.database.base import Base
from app.database.connection import get_engine
from app.database.health import check_database_health
from app.database.session import get_db_session, get_sessionmaker


def test_engine_creation():
    """Verify that get_engine returns an AsyncEngine instance."""
    engine = get_engine()
    assert isinstance(engine, AsyncEngine)
    assert engine.dialect.name == "postgresql"
    assert engine.dialect.driver == "asyncpg"


def test_sessionmaker_configuration():
    """Verify get_sessionmaker returns AsyncSession instances."""
    sessionmaker_factory = get_sessionmaker()
    session = sessionmaker_factory()
    assert isinstance(session, AsyncSession)


def test_base_metadata():
    """Verify DeclarativeBase metadata initialization."""
    assert hasattr(Base, "metadata")
    assert Base.metadata is not None


@pytest.mark.asyncio
async def test_get_db_session_dependency():
    """Verify get_db_session yields an AsyncSession instance."""
    gen = get_db_session()
    session = await gen.__anext__()
    assert isinstance(session, AsyncSession)
    try:
        await gen.__anext__()
    except StopAsyncIteration:
        pass


@pytest.mark.asyncio
async def test_check_database_health_failure_on_invalid_url():
    """Verify check_database_health returns False gracefully on invalid host/url."""
    invalid_url = "postgresql+asyncpg://invalid_user:invalid_pass@127.0.0.1:59999/nonexistent_db"
    bad_engine = get_engine(database_url=invalid_url)
    is_healthy = await check_database_health(target_engine=bad_engine)
    assert is_healthy is False
    await bad_engine.dispose()
