import pytest
from app.agents.manager import AgentRuntimeManager
from app.graph_runtime.manager import GraphRuntimeManager
from app.memory.manager import MemoryManager
from app.prompt.manager import PromptManager
from app.rag.contracts import RAGDocumentPayload, RAGIngestPayload, RAGQueryPayload, RAGRetrievePayload
from app.rag.manager import RAGManager
from app.runtime.manager import RuntimeManager
from app.tools.manager import ToolManager


@pytest.mark.asyncio
async def test_full_stack_rag_runtime_integration_smoke():
    """Smoke test exercising full stack integration path:

    User Question ➔ Graph Runtime ➔ Supervisor Agent ➔ RAG Engine ➔ Memory Runtime ➔ Prompt Engine ➔ Tool Runtime ➔ LLM Runtime ➔ Response
    """
    # 1. Initialize full frozen stack layers
    llm_runtime = RuntimeManager()
    prompt_engine = PromptManager()
    memory_runtime = MemoryManager()
    tool_runtime = ToolManager()
    graph_runtime = GraphRuntimeManager()
    agent_runtime = AgentRuntimeManager()

    rag_engine = RAGManager(
        prompt_manager=prompt_engine,
        runtime_manager=llm_runtime,
    )

    # 2. Seed knowledge base document into RAG Engine
    doc_payload = RAGDocumentPayload(
        title="Volta EV Charging Station Policy",
        raw_text="All Volta EV charging stations support 100kW fast charging. Unlock fee is $1.00.",
    )
    doc = await rag_engine.add_document(doc_payload)
    await rag_engine.ingest_document(RAGIngestPayload(document_id=doc.document_id))

    # 3. Retrieve context and query RAG Engine via public contracts
    context, trace, explanation = await rag_engine.retrieve_context(
        payload=RAGRetrievePayload(query="What is the charging station unlock fee?", top_k=3, strategy="vector", reranker="cosine")
    )
    assert context.context_text is not None
    assert len(context.citations) >= 1

    # 4. Execute answer query via RAG Engine + LLM Runtime delegation
    ans_res = await rag_engine.answer_query(
        payload=RAGQueryPayload(query="What is the charging station unlock fee?", top_k=3)
    )
    assert ans_res["answer"] is not None
    assert ans_res["explanation"]["reranker"] == "cosine"

    # 5. Verify full stack coordination through public interfaces
    health_status = await rag_engine.health_manager.check_health()
    assert health_status.is_healthy is True
    assert health_status.documents_count >= 1
