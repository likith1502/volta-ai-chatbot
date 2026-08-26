import logging
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.db.connection import get_engine

logger = logging.getLogger("app.db.health")


async def check_database_health(
    session: Optional[AsyncSession] = None,
    target_engine: Optional[AsyncEngine] = None,
) -> bool:
    """Executes 'SELECT 1' to verify PostgreSQL database connectivity."""
    eng = target_engine or get_engine()
    try:
        if session:
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
        else:
            async with eng.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                return result.scalar() == 1
    except Exception as exc:
        logger.warning(f"Database health check ping failed: {exc}")
        return False
