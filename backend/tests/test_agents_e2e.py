import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_agents_api_e2e():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Register a new agent
        reg_payload = {"name": "E2E Support Worker", "role": "support", "communication_style": "direct"}
        res_reg = await ac.post("/api/v1/agents/register", json=reg_payload)
        assert res_reg.status_code == 200
        json_r = res_reg.json()
        assert json_r["success"] is True
        agent_id = json_r["data"]["agent_id"]
        assert agent_id is not None

        # 2. Get list of agents
        res_list = await ac.get("/api/v1/agents")
        assert res_list.status_code == 200
        assert len(res_list.json()["data"]) >= 4

        # 3. Get agent details by ID
        res_det = await ac.get(f"/api/v1/agents/{agent_id}")
        assert res_det.status_code == 200
        assert res_det.json()["data"]["name"] == "E2E Support Worker"

        # 4. Execute agent task
        exec_payload = {"agent_id": agent_id, "task_title": "Resolve Support Ticket", "inputs": {"ticket_id": 101}}
        res_exec = await ac.post("/api/v1/agents/execute", json=exec_payload)
        assert res_exec.status_code == 200
        assert res_exec.json()["data"]["status"] == "completed"

        # 5. Send inter-agent message
        msg_payload = {"sender_agent_id": agent_id, "recipient_agent_id": "agent_supervisor_v1", "content": "Task completed"}
        res_msg = await ac.post("/api/v1/agents/message", json=msg_payload)
        assert res_msg.status_code == 200

        # 6. Check Health
        res_h = await ac.get("/api/v1/agents/health")
        assert res_h.status_code == 200
        assert res_h.json()["data"]["is_healthy"] is True

        # 7. Get Statistics
        res_s = await ac.get("/api/v1/agents/statistics")
        assert res_s.status_code == 200
        assert "total_registered_agents" in res_s.json()["data"]

        # 8. Get Analytics
        res_a = await ac.get("/api/v1/agents/analytics")
        assert res_a.status_code == 200
        assert "total_task_executions" in res_a.json()["data"]
