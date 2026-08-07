import pytest
from app.integrations.secrets import EnvSecretProvider


def test_env_secret_provider_get_secret_resolves_env(monkeypatch):
    monkeypatch.setenv("VOLTA_TEST_KEY", "super_secret_value")
    sp = EnvSecretProvider()
    val = sp.get_secret("VOLTA_TEST_KEY")
    assert val == "super_secret_value"


def test_env_secret_provider_get_secret_returns_default_when_missing():
    sp = EnvSecretProvider()
    val = sp.get_secret("NONEXISTENT_KEY_XYZ", default="fallback_val")
    assert val == "fallback_val"


def test_env_secret_provider_secret_version_starts_at_v1(monkeypatch):
    monkeypatch.setenv("VOLTA_VER_KEY", "test_val")
    sp = EnvSecretProvider()
    sp.get_secret("VOLTA_VER_KEY")
    assert sp.secret_version("VOLTA_VER_KEY") == "v1"


def test_env_secret_provider_rotate_increments_version(monkeypatch):
    monkeypatch.setenv("VOLTA_ROTATE_KEY", "original")
    sp = EnvSecretProvider()
    sp.get_secret("VOLTA_ROTATE_KEY")
    result = sp.rotate("VOLTA_ROTATE_KEY", "new_secret_value")
    assert result is True
    assert sp.secret_version("VOLTA_ROTATE_KEY") == "v2"
    assert sp.get_secret("VOLTA_ROTATE_KEY") == "new_secret_value"


def test_env_secret_provider_invalidate_cache_clears_state(monkeypatch):
    monkeypatch.setenv("VOLTA_CACHE_KEY", "cached_val")
    sp = EnvSecretProvider()
    sp.get_secret("VOLTA_CACHE_KEY")
    assert "VOLTA_CACHE_KEY" in sp._cache
    sp.invalidate_cache()
    assert len(sp._cache) == 0


def test_env_secret_provider_refresh_resolves_fresh_value(monkeypatch):
    monkeypatch.setenv("VOLTA_REFRESH_KEY", "initial")
    sp = EnvSecretProvider()
    v1 = sp.get_secret("VOLTA_REFRESH_KEY")
    monkeypatch.setenv("VOLTA_REFRESH_KEY", "updated")
    v2 = sp.refresh_secret("VOLTA_REFRESH_KEY")
    assert v2 == "updated"
