from typing import Any
from fastapi import APIRouter, HTTPException, status

from app.rag.contracts import (
    RAGDocumentPayload,
    RAGIngestPayload,
    RAGQueryPayload,
    RAGRetrievePayload,
)
from app.rag.manager import RAGManager
from app.utils.responses import success_response

router = APIRouter(prefix="/rag", tags=["Enterprise RAG Engine"])

_rag_manager = RAGManager()


@router.post(
    "/documents",
    status_code=status.HTTP_200_OK,
    summary="Add Document to Knowledge Store",
)
async def add_document(payload: RAGDocumentPayload) -> dict[str, Any]:
    """Adds a document to knowledge repository."""
    try:
        doc = await _rag_manager.add_document(payload)
        return success_response(
            data={"document_id": doc.document_id, "title": doc.title, "status": str(doc.status)},
            message=f"Document '{doc.title}' added to knowledge repository.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Document creation failed: {exc}")


@router.get(
    "/documents",
    status_code=status.HTTP_200_OK,
    summary="List Knowledge Documents",
)
async def list_documents() -> dict[str, Any]:
    """Returns list of all documents."""
    docs = await _rag_manager.list_documents()
    return success_response(
        data=[{"document_id": d.document_id, "title": d.title, "status": str(d.status), "mime_type": d.mime_type} for d in docs],
        message="Knowledge documents retrieved.",
    )


@router.get(
    "/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Document Details by ID",
)
async def get_document_by_id(document_id: str) -> dict[str, Any]:
    """Retrieves document details by ID."""
    doc = await _rag_manager.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")
    return success_response(
        data={
            "document_id": doc.document_id,
            "title": doc.title,
            "status": str(doc.status),
            "mime_type": doc.mime_type,
            "raw_text": doc.raw_text,
            "metadata": doc.metadata,
        },
        message=f"Document '{document_id}' retrieved.",
    )


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Document",
)
async def delete_document(document_id: str) -> dict[str, Any]:
    """Deletes document and vectors."""
    deleted = await _rag_manager.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")
    return success_response(
        data={"document_id": document_id, "deleted": True},
        message=f"Document '{document_id}' deleted successfully.",
    )


@router.post(
    "/ingest",
    status_code=status.HTTP_200_OK,
    summary="Execute Ingestion Pipeline",
)
async def ingest_document(payload: RAGIngestPayload) -> dict[str, Any]:
    """Executes parse, chunk, embed, and index pipeline."""
    try:
        job = await _rag_manager.ingest_document(payload)
        return success_response(
            data=job.model_dump(),
            message=f"Document '{payload.document_id}' ingested successfully.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")


@router.post(
    "/retrieve",
    status_code=status.HTTP_200_OK,
    summary="Retrieve RAG Context",
)
async def retrieve_rag_context(payload: RAGRetrievePayload) -> dict[str, Any]:
    """Retrieves and reranks context for query."""
    try:
        context, trace, explanation = await _rag_manager.retrieve_context(payload)
        return success_response(
            data={
                "context": context.model_dump(),
                "trace": trace.model_dump(),
                "explanation": explanation.model_dump(),
            },
            message=f"Context retrieved for query '{payload.query}'.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {exc}")


@router.post(
    "/query",
    status_code=status.HTTP_200_OK,
    summary="Answer Query via RAG + LLM Runtime",
)
async def answer_rag_query(payload: RAGQueryPayload) -> dict[str, Any]:
    """Executes RAG retrieval and delegates response generation to LLM Runtime."""
    try:
        res = await _rag_manager.answer_query(payload)
        return success_response(
            data=res,
            message="RAG query answered successfully.",
        )
    except Exception as exc:
        print(f"DEBUG RAG QUERY ERROR: {exc!r}")
        raise HTTPException(status_code=500, detail=f"RAG query execution failed: {exc}")


@router.get(
    "/statistics",
    status_code=status.HTTP_200_OK,
    summary="Get RAG Engine Statistics",
)
async def get_rag_statistics() -> dict[str, Any]:
    """Returns RAG statistics snapshot."""
    stats = _rag_manager.statistics
    return success_response(
        data=stats.model_dump(),
        message="RAG statistics retrieved.",
    )


@router.get(
    "/analytics",
    status_code=status.HTTP_200_OK,
    summary="Get RAG Telemetry Analytics",
)
async def get_rag_analytics() -> dict[str, Any]:
    """Returns RAG telemetry analytics report."""
    metrics = _rag_manager.analytics_manager.get_metrics()
    return success_response(
        data=metrics.model_dump(),
        message="RAG telemetry metrics retrieved.",
    )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Check RAG Engine Health",
)
async def get_rag_health() -> dict[str, Any]:
    """Returns RAG Engine health report."""
    health_status = await _rag_manager.health_manager.check_health()
    return success_response(
        data=health_status.model_dump(),
        message="RAG Engine health report retrieved.",
    )
