import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_runtime_api_chat_e2e():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "message": "Hello via REST API Runtime!",
            "provider": "mock",
            "model": "mock-model-v1",
            "temperature": 0.7,
            "max_tokens": 500,
        }
        res = await ac.post("/api/v1/runtime/chat", json=payload)
        assert res.status_code == 200
        json_data = res.json()
        assert json_data["success"] is True
        assert json_data["data"]["execution_status"] == "COMPLETED"
        assert json_data["data"]["response"]["provider"] == "mock"


@pytest.mark.asyncio
async def test_runtime_api_providers_and_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res_list = await ac.get("/api/v1/runtime/providers")
        assert res_list.status_code == 200
        assert "mock" in res_list.json()["data"]

        res_health = await ac.get("/api/v1/runtime/providers/mock/health")
        assert res_health.status_code == 200
        assert res_health.json()["data"]["is_healthy"] is True


@pytest.mark.asyncio
async def test_runtime_api_models_and_config():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res_models = await ac.get("/api/v1/runtime/models")
        assert res_models.status_code == 200
        assert len(res_models.json()["data"]) >= 3

        res_config = await ac.get("/api/v1/runtime/config")
        assert res_config.status_code == 200
        assert "default_provider" in res_config.json()["data"]


@pytest.mark.asyncio
async def test_runtime_api_executions_history():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Execute chat turn first
        await ac.post("/api/v1/runtime/chat", json={"message": "History turn"})

        res_hist = await ac.get("/api/v1/runtime/executions?limit=5")
        assert res_hist.status_code == 200
        assert len(res_hist.json()["data"]) >= 1
