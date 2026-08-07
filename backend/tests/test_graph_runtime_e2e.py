import pytest
import uuid
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_graph_runtime_api_e2e():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Execute graph workflow
        exec_payload = {"workflow_id": "e2e_booking_workflow", "inputs": {"intent": "book"}}
        res_exec = await ac.post("/api/v1/graph-runtime/execute", json=exec_payload)
        assert res_exec.status_code == 200
        json_e = res_exec.json()
        assert json_e["success"] is True
        session_id = json_e["data"]["session_id"]
        assert session_id is not None

        # 2. Get active session details
        res_sess = await ac.get(f"/api/v1/graph-runtime/session?session_id={session_id}")
        assert res_sess.status_code == 200
        assert res_sess.json()["data"]["session_id"] == session_id

        # 3. Resume session
        resume_payload = {"session_id": session_id, "approval_granted": True}
        res_res = await ac.post("/api/v1/graph-runtime/resume", json=resume_payload)
        assert res_res.status_code == 200
        assert res_res.json()["data"]["success"] is True

        # 4. Check Health
        res_h = await ac.get("/api/v1/graph-runtime/health")
        assert res_h.status_code == 200
        assert res_h.json()["data"]["is_healthy"] is True

        # 5. Get Statistics
        res_s = await ac.get("/api/v1/graph-runtime/statistics")
        assert res_s.status_code == 200
        assert "total_executions" in res_s.json()["data"]

        # 6. Get Analytics
        res_a = await ac.get("/api/v1/graph-runtime/analytics")
        assert res_a.status_code == 200
        assert "total_graph_executions" in res_a.json()["data"]
