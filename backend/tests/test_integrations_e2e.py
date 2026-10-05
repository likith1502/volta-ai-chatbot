import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_integrations_list_providers_endpoint():
    res = client.get("/api/v1/integrations/providers")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 8


def test_integrations_get_provider_by_id_endpoint():
    res = client.get("/api/v1/integrations/providers/storage.filesystem")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["provider_id"] == "storage.filesystem"


def test_integrations_get_provider_not_found():
    res = client.get("/api/v1/integrations/providers/nonexistent.adapter")
    assert res.status_code == 404


def test_integrations_configure_provider_endpoint():
    payload = {"provider_id": "storage.filesystem", "options": {"root_dir": "./custom_data"}}
    res = client.post("/api/v1/integrations/providers/configure", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True


def test_integrations_test_connection_endpoint():
    payload = {"provider_id": "storage.filesystem", "sample_payload": {}}
    res = client.post("/api/v1/integrations/providers/test", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True


def test_integrations_statistics_endpoint():
    res = client.get("/api/v1/integrations/statistics")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "total_providers_registered" in data["data"]


def test_integrations_analytics_endpoint():
    res = client.get("/api/v1/integrations/analytics")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True


def test_integrations_health_endpoint():
    res = client.get("/api/v1/integrations/health")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "overall_health" in data["data"]
    assert data["data"]["active_providers_count"] >= 1
