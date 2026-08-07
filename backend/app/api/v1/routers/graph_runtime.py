from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.graph_runtime.contracts import (
    GraphCancelPayload,
    GraphExecutePayload,
    GraphPausePayload,
    GraphResumePayload,
)
from app.graph_runtime.manager import GraphRuntimeManager
from app.utils.responses import success_response

router = APIRouter(prefix="/graph-runtime", tags=["Enterprise Graph Runtime"])

_graph_runtime_manager = GraphRuntimeManager()


@router.post(
    "/execute",
    status_code=status.HTTP_200_OK,
    summary="Execute Graph Workflow Runtime",
)
async def execute_graph(payload: GraphExecutePayload) -> dict[str, Any]:
    """Executes a workflow graph runtime request."""
    try:
        result = await _graph_runtime_manager.execute_graph(payload)
        return success_response(
            data=result.model_dump(),
            message=f"Workflow graph '{payload.workflow_id}' executed successfully.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 500),
            detail=f"Graph execution failed: {exc}",
        )


@router.post(
    "/resume",
    status_code=status.HTTP_200_OK,
    summary="Resume Graph Execution Session",
)
async def resume_graph_session(payload: GraphResumePayload) -> dict[str, Any]:
    """Resumes a paused or interrupted graph execution session."""
    try:
        result = await _graph_runtime_manager.resume_session(payload)
        return success_response(
            data=result.model_dump(),
            message=f"Session '{payload.session_id}' resumed successfully.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Resume failed: {exc}")


@router.post(
    "/pause",
    status_code=status.HTTP_200_OK,
    summary="Pause Graph Execution Session",
)
async def pause_graph_session(payload: GraphPausePayload) -> dict[str, Any]:
    """Pauses a running graph execution session."""
    try:
        session = await _graph_runtime_manager.pause_session(payload)
        return success_response(
            data=session.model_dump(),
            message=f"Session '{payload.session_id}' paused successfully.",
        )
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"Pause failed: {exc}")


@router.post(
    "/cancel",
    status_code=status.HTTP_200_OK,
    summary="Cancel Graph Execution Session",
)
async def cancel_graph_session(payload: GraphCancelPayload) -> dict[str, Any]:
    """Cancels a graph execution session."""
    try:
        session = await _graph_runtime_manager.cancel_session(payload)
        return success_response(
            data=session.model_dump(),
            message=f"Session '{payload.session_id}' cancelled successfully.",
        )
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"Cancel failed: {exc}")


@router.get(
    "/session",
    status_code=status.HTTP_200_OK,
    summary="Get Active Graph Session",
)
async def get_graph_session(session_id: str = Query(..., min_length=1)) -> dict[str, Any]:
    """Retrieves graph runtime session state by ID."""
    session = await _graph_runtime_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return success_response(
        data=session.model_dump(),
        message=f"Session '{session_id}' retrieved.",
    )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Check Graph Runtime Health",
)
async def get_graph_health() -> dict[str, Any]:
    """Returns health report for Graph Runtime."""
    health_status = await _graph_runtime_manager.health_manager.check_health()
    return success_response(
        data=health_status.model_dump(),
        message="Graph Runtime health report retrieved.",
    )


@router.get(
    "/statistics",
    status_code=status.HTTP_200_OK,
    summary="Get Graph Runtime Statistics",
)
async def get_graph_statistics() -> dict[str, Any]:
    """Returns statistics snapshot of Graph Runtime operations."""
    stats = await _graph_runtime_manager.get_statistics()
    return success_response(
        data=stats.model_dump(),
        message="Graph Runtime statistics retrieved.",
    )


@router.get(
    "/analytics",
    status_code=status.HTTP_200_OK,
    summary="Get Graph Runtime Analytics",
)
async def get_graph_analytics() -> dict[str, Any]:
    """Returns analytics report for Graph Runtime executions."""
    report = _graph_runtime_manager.analytics_manager.get_report()
    return success_response(
        data=report.model_dump(),
        message="Graph Runtime analytics report retrieved.",
    )
