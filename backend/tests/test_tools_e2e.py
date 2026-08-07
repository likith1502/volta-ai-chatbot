import pytest
import uuid
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_tools_api_crud_and_execute_e2e():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. List tools
        res_list = await ac.get("/api/v1/tools")
        assert res_list.status_code == 200
        json_l = res_list.json()
        assert json_l["success"] is True
        assert len(json_l["data"]) >= 4

        # 2. Get tool details
        res_get = await ac.get("/api/v1/tools/calculator")
        assert res_get.status_code == 200
        assert res_get.json()["data"]["tool_name"] == "calculator"

        # 3. Execute tool
        exec_payload = {"tool_name": "calculator", "arguments": {"a": 20, "b": 4, "operation": "divide"}}
        res_exec = await ac.post("/api/v1/tools/execute", json=exec_payload)
        assert res_exec.status_code == 200
        json_e = res_exec.json()
        assert json_e["success"] is True
        assert json_e["data"]["output"]["result"] == 5.0

        # 4. Validate tool arguments
        val_payload = {"tool_name": "echo", "arguments": {"message": "hello"}}
        res_val = await ac.post("/api/v1/tools/validate", json=val_payload)
        assert res_val.status_code == 200
        assert res_val.json()["data"]["valid"] is True

        # 5. Pipeline execution
        pipe_payload = {"tool_name": "uuid", "arguments": {}}
        res_pipe = await ac.post("/api/v1/tools/pipeline", json=pipe_payload)
        assert res_pipe.status_code == 200
        assert res_pipe.json()["data"]["success"] is True

        # 6. Health & Statistics
        res_h = await ac.get("/api/v1/tools/health")
        assert res_h.status_code == 200
        assert res_h.json()["data"]["is_healthy"] is True

        res_s = await ac.get("/api/v1/tools/statistics")
        assert res_s.status_code == 200
        assert "total_registered_tools" in res_s.json()["data"]
