import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_prompt_api_render_e2e():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "template_id": "mobility_assistant_v1",
            "variables": {"city_name": "Chicago", "user_name": "Alex"},
        }
        res = await ac.post("/api/v1/prompts/render", json=payload)
        assert res.status_code == 200
        json_data = res.json()
        assert json_data["success"] is True
        assert json_data["data"]["execution_status"] == "COMPLETED"
        assert json_data["data"]["rendered_prompt"]["template_id"] == "mobility_assistant_v1"


@pytest.mark.asyncio
async def test_prompt_api_execute_e2e():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "template_id": "system_chat_v1",
            "variables": {"query": "Tell me about Volta rides"},
            "provider": "mock",
        }
        res = await ac.post("/api/v1/prompts/execute", json=payload)
        assert res.status_code == 200
        json_data = res.json()
        assert json_data["success"] is True
        assert json_data["data"]["runtime_result"]["execution_status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_prompt_api_templates_and_profiles():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res_t = await ac.get("/api/v1/prompts/templates")
        assert res_t.status_code == 200
        assert len(res_t.json()["data"]) >= 3

        res_p = await ac.get("/api/v1/prompts/profiles")
        assert res_p.status_code == 200
        assert len(res_p.json()["data"]) >= 2


@pytest.mark.asyncio
async def test_prompt_api_history_and_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res_h = await ac.get("/api/v1/prompts/health")
        assert res_h.status_code == 200
        assert res_h.json()["data"]["is_healthy"] is True

        res_hist = await ac.get("/api/v1/prompts/history")
        assert res_hist.status_code == 200
        assert "snapshots" in res_hist.json()["data"]
