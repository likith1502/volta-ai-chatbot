import pytest
from app.integrations.manifest import PluginManifest
from app.integrations.capabilities import IntegrationCapability
from app.integrations.validator import IntegrationValidator
from app.integrations.exceptions import IntegrationError


def test_plugin_manifest_loads_correctly():
    m = PluginManifest(
        id="storage.filesystem",
        name="Filesystem Storage Adapter",
        version="1.0.0",
        api_version="v1",
        runtime_version="7.7.0",
        category=IntegrationCapability.STORAGE,
        author="VOLTA Core Team",
        depends_on=[],
        conflicts_with=[],
    )
    assert m.id == "storage.filesystem"
    assert m.category == IntegrationCapability.STORAGE
    assert m.api_version == "v1"
    assert m.runtime_version == "7.7.0"


def test_plugin_manifest_depends_on():
    m = PluginManifest(
        id="observability.prometheus",
        name="Prometheus Observability Adapter",
        category=IntegrationCapability.OBSERVABILITY,
        depends_on=["storage.filesystem"],
    )
    assert "storage.filesystem" in m.depends_on


def test_plugin_manifest_conflicts_with():
    m = PluginManifest(
        id="messaging.kafka",
        name="Kafka Event Bus Adapter",
        category=IntegrationCapability.MESSAGING,
        conflicts_with=["messaging.rabbitmq"],
    )
    assert "messaging.rabbitmq" in m.conflicts_with


def test_plugin_manifest_validator_accepts_valid_manifest():
    m = PluginManifest(
        id="storage.s3",
        name="AWS S3 Storage Adapter",
        category=IntegrationCapability.STORAGE,
    )
    result = IntegrationValidator.validate_manifest(m)
    assert result is True


def test_plugin_manifest_validator_rejects_empty_id():
    with pytest.raises(Exception):
        m = PluginManifest(
            id="",
            name="Invalid Adapter",
            category=IntegrationCapability.STORAGE,
        )
        IntegrationValidator.validate_manifest(m)
