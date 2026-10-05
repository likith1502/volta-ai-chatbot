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


@pytest.mark.asyncio
async def test_prompt_api_sandbox_and_compare_e2e():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Scratch prompt sandbox
        sandbox_payload = {
            "system_instruction": "You are a ride booking assistant.",
            "user_prompt_template": "Book a ride to {destination}",
            "variables": {"destination": "Airport"},
            "provider": "mock",
        }
        res_sb = await ac.post("/api/v1/prompts/sandbox/execute", json=sandbox_payload)
        assert res_sb.status_code == 200
        assert res_sb.json()["success"] is True

        # 2. Side-by-side comparison
        compare_payload = {
            "template_id": "mobility_assistant_v1",
            "variables": {"city_name": "San Francisco"},
            "providers": ["mock"],
        }
        res_cmp = await ac.post("/api/v1/prompts/compare", json=compare_payload)
        assert res_cmp.status_code == 200
        assert "mock" in res_cmp.json()["data"]
