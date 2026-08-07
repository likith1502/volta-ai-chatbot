import pytest
import uuid
from httpx import ASGITransport, AsyncClient

from app.graph_runtime.contracts import GraphExecutePayload
from app.graph_runtime.manager import GraphRuntimeManager
from app.graph_runtime.state import GraphRuntimeState
from app.main import app


@pytest.mark.asyncio
async def test_full_runtime_stack_smoke_e2e():
    """End-to-end regression smoke test exercising the complete Enterprise Runtime Stack.

    User Request -> Graph Runtime -> Prompt Engine -> Memory Runtime -> Tool Runtime -> LLM Runtime -> Provider -> Response.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Verify REST API Router endpoints readiness
        res_h = await ac.get("/api/v1/health")
        assert res_h.status_code == 200

        res_rt_h = await ac.get("/api/v1/runtime/health")
        assert res_rt_h.status_code == 200

        res_pr_h = await ac.get("/api/v1/prompts/health")
        assert res_pr_h.status_code == 200

        res_mem_h = await ac.get("/api/v1/memory/health")
        assert res_mem_h.status_code == 200

        res_tool_h = await ac.get("/api/v1/tools/health")
        assert res_tool_h.status_code == 200

        res_graph_h = await ac.get("/api/v1/graph-runtime/health")
        assert res_graph_h.status_code == 200

        # 2. Execute full graph workflow payload through REST API
        payload = {
            "workflow_id": "full_runtime_smoke_workflow",
            "inputs": {
                "user_intent": "book_mobility_ride",
                "origin": "Central Station",
                "destination": "Airport Terminal 1",
            },
        }

        res_exec = await ac.post("/api/v1/graph-runtime/execute", json=payload)
        assert res_exec.status_code == 200
        json_resp = res_exec.json()
        assert json_resp["success"] is True

        data = json_resp["data"]
        assert data["status"] == "completed"
        assert len(data["visited_nodes"]) >= 4
        assert "START" in data["visited_nodes"]
        assert "END" in data["visited_nodes"]

        # 3. Verify Execution Trace step recordings
        assert "trace" in data
        assert data["trace"] is not None
        assert len(data["trace"]["steps"]) >= 4

        # 4. Verify Session State query
        session_id = data["session_id"]
        res_sess = await ac.get(f"/api/v1/graph-runtime/session?session_id={session_id}")
        assert res_sess.status_code == 200
        assert res_sess.json()["data"]["session_id"] == session_id
