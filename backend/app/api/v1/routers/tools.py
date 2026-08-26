from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.tools.chain import ToolChain
from app.tools.contracts import ToolExecutePayload, ToolValidatePayload
from app.tools.manager import ToolManager
from app.utils.responses import success_response

router = APIRouter(prefix="/tools", tags=["Enterprise Tool Runtime"])

# Global singleton instance for local dev/testing
_tool_manager = ToolManager()


@router.post(
    "/execute",
    status_code=status.HTTP_200_OK,
    summary="Execute Tool Call",
)
async def execute_tool(payload: ToolExecutePayload) -> dict[str, Any]:
    """Executes a single tool call."""
    try:
        result = await _tool_manager.execute_tool(payload)
        return success_response(
            data=result.model_dump(),
            message=f"Tool '{payload.tool_name}' executed successfully",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 500),
            detail=f"Tool execution failed: {exc}",
        )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="List Registered Tools",
)
async def list_tools() -> dict[str, Any]:
    """Lists all registered tool manifests."""
    manifests = await _tool_manager.list_tools()
    return success_response(
        data=[m.model_dump() for m in manifests],
        message="Registered tool manifests retrieved",
    )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Check Tool Runtime Health",
)
async def get_tool_health() -> dict[str, Any]:
    """Returns health status report for Tool Runtime."""
    await _tool_manager._ensure_init()
    health_status = await _tool_manager.health_manager.check_health()
    return success_response(
        data=health_status.model_dump(),
        message="Tool Runtime health report retrieved",
    )


@router.get(
    "/statistics",
    status_code=status.HTTP_200_OK,
    summary="Get Tool Repository Statistics",
)
async def get_tool_statistics() -> dict[str, Any]:
    """Returns statistics snapshot of tool repository."""
    stats = await _tool_manager.get_statistics()
    return success_response(
        data=stats.model_dump(),
        message="Tool repository statistics retrieved",
    )


@router.get(
    "/{tool_name}",
    status_code=status.HTTP_200_OK,
    summary="Get Tool Manifest Details",
)
async def get_tool_details(tool_name: str) -> dict[str, Any]:
    """Retrieves tool manifest details by name."""
    try:
        manifest = await _tool_manager.get_manifest(tool_name)
        return success_response(
            data=manifest.model_dump(),
            message=f"Tool '{tool_name}' details retrieved",
        )
    except Exception:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found.")


@router.post(
    "/validate",
    status_code=status.HTTP_200_OK,
    summary="Validate Tool Arguments",
)
async def validate_tool_arguments(payload: ToolValidatePayload) -> dict[str, Any]:
    """Validates tool arguments against JSON schema without executing."""
    try:
        manifest = await _tool_manager.get_manifest(payload.tool_name)
        _tool_manager.validator.validate(manifest, payload.arguments)
        return success_response(
            data={"valid": True, "tool_name": payload.tool_name},
            message=f"Arguments for tool '{payload.tool_name}' are valid.",
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Validation failed: {exc}")


@router.post(
    "/pipeline",
    status_code=status.HTTP_200_OK,
    summary="Execute Tool Pipeline",
)
async def execute_tool_pipeline(payload: ToolExecutePayload) -> dict[str, Any]:
    """Executes tool request through step-by-step ToolPipeline."""
    try:
        pipe_result = await _tool_manager.execute_pipeline(payload)
        return success_response(
            data=pipe_result.model_dump(),
            message="ToolPipeline executed successfully",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {exc}")


@router.post(
    "/chain",
    status_code=status.HTTP_200_OK,
    summary="Execute Sequential ToolChain",
)
async def execute_tool_chain(chain: ToolChain) -> dict[str, Any]:
    """Executes a sequential multi-step ToolChain."""
    try:
        chain_result = await _tool_manager.execute_chain(chain)
        return success_response(
            data=chain_result.model_dump(),
            message="ToolChain executed successfully",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chain execution failed: {exc}")
