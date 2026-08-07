import pytest
import uuid
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_memory_api_crud_e2e():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        cid = str(uuid.uuid4())
        # 1. Create memory
        create_payload = {
            "content": "User prefers Electric vehicles",
            "conversation_id": cid,
            "memory_type": "user",
            "importance": 0.9,
        }
        res_create = await ac.post("/api/v1/memory", json=create_payload)
        assert res_create.status_code == 201
        json_c = res_create.json()
        assert json_c["success"] is True
        mem_id = json_c["data"]["memory_id"]

        # 2. Get memory details
        res_get = await ac.get(f"/api/v1/memory/{mem_id}")
        assert res_get.status_code == 200
        assert res_get.json()["data"]["content"] == "User prefers Electric vehicles"

        # 3. List memories
        res_list = await ac.get(f"/api/v1/memory?conversation_id={cid}")
        assert res_list.status_code == 200
        assert len(res_list.json()["data"]) >= 1

        # 4. Assemble context
        ctx_payload = {"conversation_id": cid, "strategy": "hybrid"}
        res_ctx = await ac.post("/api/v1/memory/context", json=ctx_payload)
        assert res_ctx.status_code == 200
        assert res_ctx.json()["data"]["total_memories_count"] >= 1

        # 5. Delete memory
        res_del = await ac.delete(f"/api/v1/memory/{mem_id}")
        assert res_del.status_code == 200
        assert res_del.json()["data"]["deleted"] is True


@pytest.mark.asyncio
async def test_memory_api_health_and_statistics_e2e():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res_h = await ac.get("/api/v1/memory/health")
        assert res_h.status_code == 200
        assert res_h.json()["data"]["is_healthy"] is True

        res_s = await ac.get("/api/v1/memory/statistics")
        assert res_s.status_code == 200
        assert "total_memories" in res_s.json()["data"]
