import pytest
from app.integrations.registry import IntegrationRegistry
from app.integrations.capabilities import IntegrationCapability
from app.integrations.adapters.storage.storage_adapter import FilesystemStorageAdapter
from app.integrations.adapters.storage.placeholders import S3StorageAdapter
from app.integrations.status import IntegrationStatus


@pytest.mark.asyncio
async def test_failover_selects_highest_priority_provider():
    """Filesystem (p=10) and S3 (p=100) registered — S3 should win."""
    reg = IntegrationRegistry()
    fs = FilesystemStorageAdapter()
    await fs.initialize()
    s3 = S3StorageAdapter()
    await s3.initialize()
    reg.register_provider(fs)
    reg.register_provider(s3)

    active = reg.resolve_active_provider(IntegrationCapability.STORAGE)
    assert active is not None
    assert active.provider_id == "storage.s3"


@pytest.mark.asyncio
async def test_failover_falls_back_to_lower_priority_when_primary_disconnected():
    """When S3 is DISCONNECTED, resolve_active_provider should return Filesystem instead."""
    reg = IntegrationRegistry()
    fs = FilesystemStorageAdapter()
    await fs.initialize()
    s3 = S3StorageAdapter()
    await s3.initialize()
    # Simulate S3 failure
    s3._status = IntegrationStatus.FAILED
    reg.register_provider(fs)
    reg.register_provider(s3)

    active = reg.resolve_active_provider(IntegrationCapability.STORAGE)
    assert active is not None
    assert active.provider_id == "storage.filesystem"


@pytest.mark.asyncio
async def test_failover_returns_none_if_no_providers_in_category():
    reg = IntegrationRegistry()
    active = reg.resolve_active_provider(IntegrationCapability.VECTOR)
    assert active is None


@pytest.mark.asyncio
async def test_failover_find_by_capability_sorted_by_priority_desc():
    reg = IntegrationRegistry()
    fs = FilesystemStorageAdapter(priority=10)
    s3 = S3StorageAdapter()  # priority 100
    reg.register_provider(fs)
    reg.register_provider(s3)

    results = reg.find_by_capability(IntegrationCapability.STORAGE)
    assert results[0].priority > results[1].priority
