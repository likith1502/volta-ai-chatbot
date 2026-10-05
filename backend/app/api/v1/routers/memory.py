import uuid
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.memory.contracts import MemoryRequest, MemoryResponse, MemorySearchResult
from app.memory.manager import MemoryManager
from app.memory.status import MemoryStatus
from app.memory.types import MemoryType
from app.utils.responses import success_response

router = APIRouter(prefix="/memory", tags=["Enterprise Memory Runtime"])

# Global singleton instance for local dev/testing
_memory_manager = MemoryManager()


class SearchMemoryPayload(BaseModel):
    """Payload for memory search and scoring."""

    query: str = Field(default="", description="Search query keyword filter")
    conversation_id: Optional[uuid.UUID] = Field(default=None)
    strategy: str = Field(default="hybrid", description="'recent', 'importance', 'hybrid', 'sliding_window'")
    limit: int = Field(default=10, ge=1, le=100)


class AssembleContextPayload(BaseModel):
    """Payload for context assembly & context window budget calculation."""

    conversation_id: Optional[uuid.UUID] = Field(default=None)
    strategy: str = Field(default="hybrid")
    token_budget: int = Field(default=4000, ge=100)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create New Conversation Memory",
)
async def create_memory(payload: MemoryRequest) -> dict[str, Any]:
    """Creates and stores a new Memory instance."""
    try:
        memory = await _memory_manager.create_memory(payload)
        return success_response(
            data=memory.model_dump(),
            message="Memory entry created successfully",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 500),
            detail=f"Memory creation failed: {exc}",
        )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="List Stored Memories",
)
async def list_memories(
    conversation_id: Optional[uuid.UUID] = Query(default=None),
    status_filter: Optional[MemoryStatus] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict[str, Any]:
    """Lists stored memories with optional conversation or status filter."""
    repo = _memory_manager.registry.get_repository()
    if conversation_id:
        mems = await repo.list_by_conversation(conversation_id, status=status_filter, limit=limit)
    else:
        mems = await repo.list_all(limit=limit)

    return success_response(
        data=[m.model_dump() for m in mems],
        message="Memories retrieved successfully",
    )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Check Memory Runtime Health",
)
async def get_memory_health() -> dict[str, Any]:
    """Returns health status report for Enterprise Memory Runtime."""
    health_status = await _memory_manager.health_manager.check_health()
    return success_response(
        data=health_status.model_dump(),
        message="Memory Runtime health report retrieved",
    )


@router.get(
    "/statistics",
    status_code=status.HTTP_200_OK,
    summary="Get Memory Repository Statistics",
)
async def get_memory_statistics() -> dict[str, Any]:
    """Returns state statistics snapshot of memory repository."""
    stats = await _memory_manager.get_statistics()
    return success_response(
        data=stats.model_dump(),
        message="Memory repository statistics retrieved",
    )


@router.get(
    "/metrics",
    status_code=status.HTTP_200_OK,
    summary="Get Memory Runtime Metrics",
)
async def get_memory_metrics() -> dict[str, Any]:
    """Returns memory execution metrics telemetry."""
    return success_response(
        data=_memory_manager.metrics.model_dump(),
        message="Memory metrics retrieved",
    )


@router.get(
    "/{memory_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Memory Entry Details",
)
async def get_memory_details(memory_id: uuid.UUID) -> dict[str, Any]:
    """Retrieves memory entry by UUID."""
    try:
        mem = await _memory_manager.get_memory(memory_id)
        return success_response(
            data=mem.model_dump(),
            message=f"Memory '{memory_id}' retrieved",
        )
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"Memory '{memory_id}' not found.")


@router.delete(
    "/{memory_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Memory Entry",
)
async def delete_memory_entry(memory_id: uuid.UUID) -> dict[str, Any]:
    """Deletes memory entry by UUID."""
    try:
        res = await _memory_manager.delete_memory(memory_id)
        if not res:
            raise HTTPException(status_code=404, detail=f"Memory '{memory_id}' not found.")
        return success_response(
            data={"deleted": True, "memory_id": str(memory_id)},
            message=f"Memory '{memory_id}' deleted successfully",
        )
    except Exception as exc:
        raise HTTPException(status_code=getattr(exc, "status_code", 500), detail=f"Delete failed: {exc}")


@router.post(
    "/search",
    status_code=status.HTTP_200_OK,
    summary="Search and Score Memories",
)
async def search_memories(payload: SearchMemoryPayload) -> dict[str, Any]:
    """Searches and scores stored memories using specified strategy."""
    res: MemorySearchResult = await _memory_manager.search_memories(
        query=payload.query,
        conversation_id=payload.conversation_id,
        strategy=payload.strategy,
        limit=payload.limit,
    )
    return success_response(
        data=res.model_dump(),
        message="Memory search completed successfully",
    )


@router.post(
    "/context",
    status_code=status.HTTP_200_OK,
    summary="Assemble Memory Context Payload",
)
async def assemble_context(payload: AssembleContextPayload) -> dict[str, Any]:
    """Assembles structured MemoryContext payload for prompt variable injection."""
    ctx = await _memory_manager.assemble_context(
        conversation_id=payload.conversation_id,
        strategy=payload.strategy,
        token_budget=payload.token_budget,
    )
    return success_response(
        data=ctx.model_dump(),
        message="Memory context assembled successfully",
    )


@router.post(
    "/cleanup",
    status_code=status.HTTP_200_OK,
    summary="Execute Memory Retention Cleanup",
)
async def cleanup_memories() -> dict[str, Any]:
    """Executes retention policy cleanup for expired memories."""
    count = await _memory_manager.cleanup_expired()
    return success_response(
        data={"cleaned_count": count},
        message=f"Cleanup completed. Expired memories cleaned: {count}",
    )
