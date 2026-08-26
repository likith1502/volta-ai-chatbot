import pytest
from app.integrations.factory import IntegrationFactory
from app.integrations.capabilities import IntegrationCapability


def test_factory_creates_reference_adapters():
    adapters = IntegrationFactory.create_reference_adapters()
    assert len(adapters) == 8


def test_factory_includes_all_core_categories():
    adapters = IntegrationFactory.create_reference_adapters()
    categories = {a.category for a in adapters}
    expected = {
        IntegrationCapability.STORAGE,
        IntegrationCapability.VECTOR,
        IntegrationCapability.LLM,
        IntegrationCapability.AUTH,
        IntegrationCapability.DATABASE,
        IntegrationCapability.OBSERVABILITY,
        IntegrationCapability.MESSAGING,
        IntegrationCapability.SCHEDULER,
    }
    assert expected == categories


def test_factory_adapter_ids_are_stable():
    adapters = IntegrationFactory.create_reference_adapters()
    ids = {a.provider_id for a in adapters}
    assert "storage.filesystem" in ids
    assert "vector.inmemory" in ids
    assert "llm.gemini" in ids
    assert "auth.jwt" in ids
    assert "database.postgres" in ids
    assert "observability.prometheus" in ids
    assert "messaging.webhook" in ids
    assert "scheduler.cron" in ids
