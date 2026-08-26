import pytest
from app.integrations.config import IntegrationConfig
from app.integrations.runtime_config import IntegrationRuntimeConfig
from app.integrations.provider_config import ProviderConfig
from app.integrations.policy import IntegrationPolicy


def test_integration_config_defaults():
    cfg = IntegrationConfig()
    assert cfg.default_secret_provider == "env"
    assert cfg.enable_auto_failover is True
    assert cfg.enable_audit_logging is True
    assert cfg.sandbox_mode is False


def test_runtime_config_defaults():
    cfg = IntegrationRuntimeConfig()
    assert cfg.connection_timeout_seconds == 5.0
    assert cfg.health_check_interval_seconds == 30.0
    assert cfg.max_reconnect_attempts == 3


def test_provider_config_defaults():
    cfg = ProviderConfig(provider_id="storage.filesystem")
    assert cfg.enabled is True
    assert cfg.priority == 10
    assert cfg.weight == 1.0
    assert cfg.preferred is False


def test_provider_config_high_priority():
    cfg = ProviderConfig(provider_id="storage.s3", priority=100, preferred=True)
    assert cfg.priority == 100
    assert cfg.preferred is True


def test_integration_policy_defaults():
    pol = IntegrationPolicy()
    assert pol.allow_sandbox_override is True
    assert pol.enforce_tls is True
    assert pol.require_secret_resolution is True
