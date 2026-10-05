import pytest
from app.integrations.registry import IntegrationRegistry
from app.integrations.adapters.storage.storage_adapter import FilesystemStorageAdapter
from app.integrations.adapters.vector.vector_adapter import InMemoryVectorAdapter
from app.integrations.adapters.llm.llm_adapter import GeminiLLMAdapter
from app.integrations.capabilities import IntegrationCapability
from app.integrations.status import IntegrationStatus


@pytest.mark.asyncio
async def test_registry_registers_providers():
    reg = IntegrationRegistry()
    adapter = FilesystemStorageAdapter()
    reg.register_provider(adapter)
    assert reg.get_provider("storage.filesystem") is not None


@pytest.mark.asyncio
async def test_registry_find_by_capability():
    reg = IntegrationRegistry()
    reg.register_provider(FilesystemStorageAdapter())
    reg.register_provider(InMemoryVectorAdapter())
    storage = reg.find_by_capability(IntegrationCapability.STORAGE)
    assert len(storage) == 1
    assert storage[0].provider_id == "storage.filesystem"


@pytest.mark.asyncio
async def test_registry_resolve_active_provider_returns_highest_priority():
    from app.integrations.adapters.storage.storage_adapter import FilesystemStorageAdapter
    from app.integrations.adapters.storage.placeholders import S3StorageAdapter

    reg = IntegrationRegistry()
    fs = FilesystemStorageAdapter()
    await fs.initialize()
    s3 = S3StorageAdapter()
    await s3.initialize()
    reg.register_provider(fs)
    reg.register_provider(s3)

    active = reg.resolve_active_provider(IntegrationCapability.STORAGE)
    # S3 has priority 100, Filesystem has priority 10 → S3 should win
    assert active is not None
    assert active.provider_id == "storage.s3"


@pytest.mark.asyncio
async def test_registry_list_all_providers():
    reg = IntegrationRegistry()
    reg.register_provider(FilesystemStorageAdapter())
    reg.register_provider(InMemoryVectorAdapter())
    reg.register_provider(GeminiLLMAdapter())
    all_providers = reg.list_providers()
    assert len(all_providers) == 3
