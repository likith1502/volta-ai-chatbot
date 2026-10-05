import pytest
import uuid
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_multi_agent_full_stack_smoke_e2e():
    """End-to-end multi-agent integration smoke test exercising the complete stack:

    User -> Graph Runtime -> Supervisor Agent -> Planner Agent -> Memory Runtime -> Prompt Engine -> Tool Runtime -> LLM Runtime -> Mock/Gemini -> Response.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Health checks across all 6 layers
        res_h = await ac.get("/api/v1/health")
        assert res_h.status_code == 200

        res_ag_h = await ac.get("/api/v1/agents/health")
        assert res_ag_h.status_code == 200
        assert res_ag_h.json()["data"]["is_healthy"] is True

        # 2. Register Multi-Agent Showcase Team
        res_sup = await ac.post("/api/v1/agents/register", json={
            "name": "Showcase Travel Supervisor",
            "role": "supervisor",
            "communication_style": "structured",
        })
        assert res_sup.status_code == 200
        sup_id = res_sup.json()["data"]["agent_id"]

        res_planner = await ac.post("/api/v1/agents/register", json={
            "name": "Showcase Itinerary Planner",
            "role": "planner",
            "communication_style": "analytical",
        })
        assert res_planner.status_code == 200
        planner_id = res_planner.json()["data"]["agent_id"]

        # 3. Delegate subtask from Supervisor to Planner
        del_payload = {
            "delegator_agent_id": sup_id,
            "delegatee_agent_id": planner_id,
            "task_title": "Decompose Mobility Booking Itinerary",
            "inputs": {"destination": "Airport Terminal 1", "origin": "Central Station"},
            "current_depth": 1,
        }
        res_del = await ac.post("/api/v1/agents/delegate", json=del_payload)
        assert res_del.status_code == 200
        assert res_del.json()["data"]["assigned_agent_id"] == planner_id

        # 4. Execute turn with Planner Agent
        exec_payload = {
            "agent_id": planner_id,
            "task_title": "Decompose Mobility Booking Itinerary",
            "inputs": {"tool_name": "calculator", "tool_args": {"operation": "add", "a": 10, "b": 20}},
        }
        res_exec = await ac.post("/api/v1/agents/execute", json=exec_payload)
        assert res_exec.status_code == 200
        assert res_exec.json()["data"]["status"] == "completed"
        assert res_exec.json()["data"]["output"]["tool_output"]["success"] is True

        # 5. Send inter-agent completion message
        msg_payload = {
            "sender_agent_id": planner_id,
            "recipient_agent_id": sup_id,
            "content": "Itinerary decomposition and tool calculation complete.",
        }
        res_msg = await ac.post("/api/v1/agents/message", json=msg_payload)
        assert res_msg.status_code == 200

        # 6. Verify Statistics
        res_stats = await ac.get("/api/v1/agents/statistics")
        assert res_stats.status_code == 200
        assert res_stats.json()["data"]["total_tasks_executed"] >= 1
