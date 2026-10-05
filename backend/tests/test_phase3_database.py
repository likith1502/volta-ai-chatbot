import pytest
from app.integrations.adapters.database.postgres_adapter import PostgresDatabaseAdapter
from app.integrations.adapters.database.redis_adapter import RedisDatabaseAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.status import IntegrationStatus


@pytest.mark.asyncio
async def test_database_adapter_provider_ids_and_defaults():
    pg = PostgresDatabaseAdapter()
    redis = RedisDatabaseAdapter()

    assert pg.provider_id == "database.postgres"
    assert redis.provider_id == "database.redis"


@pytest.mark.asyncio
async def test_redis_capability_honesty_for_execute_query():
    redis = RedisDatabaseAdapter()
    res = await redis.execute_query("SELECT * FROM users")
    assert isinstance(res, dict)
    assert res.get("error") == "unsupported_operation"


@pytest.mark.asyncio
async def test_initialization_safety_and_health_without_credentials():
    ctx = IntegrationContext()

    pg = PostgresDatabaseAdapter()
    await pg.initialize(ctx)
    report_pg = await pg.check_health()
    assert report_pg.provider_id == "database.postgres"
    assert report_pg.is_healthy is True

    redis = RedisDatabaseAdapter()
    await redis.initialize(ctx)
    report_redis = await redis.check_health()
    assert report_redis.provider_id == "database.redis"
    assert report_redis.is_healthy is False


@pytest.mark.asyncio
async def test_resource_cleanup_disconnect():
    pg = PostgresDatabaseAdapter()
    await pg.disconnect()
    assert pg.status == IntegrationStatus.DISCONNECTED

    redis = RedisDatabaseAdapter()
    await redis.disconnect()
    assert redis.status == IntegrationStatus.DISCONNECTED
