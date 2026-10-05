import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_rag_api_e2e():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Add document
        add_payload = {
            "title": "E2E Scooter Manual",
            "raw_text": "Scooters can be unlocked using QR code scanning in the Volta app.",
            "mime_type": "text/plain",
        }
        res_add = await ac.post("/api/v1/rag/documents", json=add_payload)
        assert res_add.status_code == 200
        doc_id = res_add.json()["data"]["document_id"]
        assert doc_id is not None

        # 2. Ingest document
        ingest_payload = {"document_id": doc_id, "chunk_size": 256, "chunk_overlap": 32}
        res_ing = await ac.post("/api/v1/rag/ingest", json=ingest_payload)
        assert res_ing.status_code == 200
        assert res_ing.json()["data"]["status"] == "completed"

        # 3. List documents
        res_list = await ac.get("/api/v1/rag/documents")
        assert res_list.status_code == 200
        assert len(res_list.json()["data"]) >= 1

        # 4. Get document details
        res_det = await ac.get(f"/api/v1/rag/documents/{doc_id}")
        assert res_det.status_code == 200

        # 5. Retrieve RAG context
        ret_payload = {"query": "QR code unlock", "top_k": 3, "strategy": "vector", "reranker": "cosine"}
        res_ret = await ac.post("/api/v1/rag/retrieve", json=ret_payload)
        assert res_ret.status_code == 200
        assert "context" in res_ret.json()["data"]

        # 6. Answer query via RAG + LLM Runtime
        query_payload = {"query": "How do I unlock a scooter?", "top_k": 3}
        res_q = await ac.post("/api/v1/rag/query", json=query_payload)
        assert res_q.status_code == 200
        assert res_q.json()["data"]["answer"] is not None

        # 7. Check Health
        res_h = await ac.get("/api/v1/rag/health")
        assert res_h.status_code == 200
        assert res_h.json()["data"]["is_healthy"] is True

        # 8. Get Statistics & Analytics
        res_s = await ac.get("/api/v1/rag/statistics")
        assert res_s.status_code == 200

        res_a = await ac.get("/api/v1/rag/analytics")
        assert res_a.status_code == 200
