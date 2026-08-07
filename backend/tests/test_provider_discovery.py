import pytest
from app.integrations.registry import IntegrationRegistry
from app.integrations.factory import IntegrationFactory
from app.integrations.capabilities import IntegrationCapability


@pytest.mark.asyncio
async def test_provider_discovery_by_storage_capability():
    reg = IntegrationRegistry()
    for a in IntegrationFactory.create_reference_adapters():
        reg.register_provider(a)
    storage = reg.find_by_capability(IntegrationCapability.STORAGE)
    assert len(storage) >= 1
    assert all(a.category == IntegrationCapability.STORAGE for a in storage)


@pytest.mark.asyncio
async def test_provider_discovery_by_llm_capability():
    reg = IntegrationRegistry()
    for a in IntegrationFactory.create_reference_adapters():
        reg.register_provider(a)
    llm = reg.find_by_capability(IntegrationCapability.LLM)
    assert len(llm) >= 1
    assert all(a.category == IntegrationCapability.LLM for a in llm)


@pytest.mark.asyncio
async def test_provider_discovery_by_observability_capability():
    reg = IntegrationRegistry()
    for a in IntegrationFactory.create_reference_adapters():
        reg.register_provider(a)
    obs = reg.find_by_capability(IntegrationCapability.OBSERVABILITY)
    assert len(obs) >= 1


@pytest.mark.asyncio
async def test_provider_discovery_empty_for_missing_category():
    reg = IntegrationRegistry()
    search = reg.find_by_capability(IntegrationCapability.SEARCH)
    assert search == []


@pytest.mark.asyncio
async def test_provider_discovery_sorted_by_priority_desc():
    from app.integrations.adapters.storage.storage_adapter import FilesystemStorageAdapter
    from app.integrations.adapters.storage.placeholders import S3StorageAdapter
    reg = IntegrationRegistry()
    reg.register_provider(FilesystemStorageAdapter())  # priority 10
    reg.register_provider(S3StorageAdapter())          # priority 100
    results = reg.find_by_capability(IntegrationCapability.STORAGE)
    assert results[0].priority >= results[-1].priority
