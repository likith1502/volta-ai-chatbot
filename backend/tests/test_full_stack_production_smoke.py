import pytest
from app.integrations.manager import IntegrationManager
from app.integrations.capabilities import IntegrationCapability
from app.integrations.health_level import HealthLevel
from app.agents.manager import AgentRuntimeManager
from app.graph_runtime.manager import GraphRuntimeManager
from app.memory.manager import MemoryManager
from app.prompt.manager import PromptManager
from app.rag.manager import RAGManager
from app.rag.contracts import RAGDocumentPayload, RAGIngestPayload, RAGRetrievePayload
from app.runtime.manager import RuntimeManager
from app.tools.manager import ToolManager


@pytest.mark.asyncio
async def test_full_stack_production_integration_smoke():
    """Full-stack production integration smoke test:

    User ➔ Integration Platform ➔ RAG Engine ➔ Agent Runtime ➔ Graph Runtime ➔
    Tool Runtime ➔ Memory Runtime ➔ Prompt Engine ➔ LLM Runtime ➔ Response
    """
    # 1. Initialize full frozen runtime stack
    llm_runtime = RuntimeManager()
    prompt_engine = PromptManager()
    memory_runtime = MemoryManager()
    tool_runtime = ToolManager()
    graph_runtime = GraphRuntimeManager()
    agent_runtime = AgentRuntimeManager()
    rag_engine = RAGManager(prompt_manager=prompt_engine, runtime_manager=llm_runtime)

    # 2. Initialize integration manager (production adapters)
    integration_manager = IntegrationManager()

    # 3. Verify all 8 reference adapters are healthy
    health_report = await integration_manager.check_platform_health()
    assert health_report.overall_health == HealthLevel.GREEN
    assert health_report.active_providers_count >= 8

    # 4. Resolve storage adapter via capability discovery
    storage = integration_manager.resolve_active_provider(IntegrationCapability.STORAGE)
    assert storage is not None
    assert storage.provider_id == "storage.filesystem"

    # 5. Ingest document into RAG Engine
    doc = await rag_engine.add_document(RAGDocumentPayload(
        title="Integration Platform Architecture",
        raw_text="The VOLTA Enterprise Integration Platform connects 8 production adapters. Filesystem is the default storage.",
    ))
    await rag_engine.ingest_document(RAGIngestPayload(document_id=doc.document_id))

    # 6. Retrieve context via RAG Query Runtime
    context, trace, explanation = await rag_engine.retrieve_context(
        payload=RAGRetrievePayload(query="What is the default storage adapter?", top_k=3)
    )
    assert context.context_text is not None

    # 7. Verify LLM adapter from integration platform
    llm_adapter = integration_manager.resolve_active_provider(IntegrationCapability.LLM)
    assert llm_adapter is not None
    assert llm_adapter.provider_id == "llm.gemini"

    # 8. Verify observability adapter is online
    obs_adapter = integration_manager.resolve_active_provider(IntegrationCapability.OBSERVABILITY)
    assert obs_adapter is not None

    # 9. Final audit log check
    audit_events = integration_manager.audit_logger.get_events()
    assert len(audit_events) >= 8  # One register per reference adapter
