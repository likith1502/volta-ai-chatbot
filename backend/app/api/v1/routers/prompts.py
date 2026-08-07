import uuid
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.prompt.contracts import PromptRequest
from app.prompt.manager import PromptManager
from app.prompt.result import PromptResult
from app.utils.responses import success_response

router = APIRouter(prefix="/prompts", tags=["Prompt Execution Engine"])

# Global singleton instance for local dev/testing
_prompt_manager = PromptManager()


class PromptRenderPayload(BaseModel):
    """Payload for prompt rendering, linting, validation, and optimization."""

    template_id: str = Field(..., description="Target template ID (e.g. 'mobility_assistant_v1', 'ride_booking_v1')")
    revision_id: Optional[str] = Field(default="v1", description="Template revision ID")
    profile_id: Optional[str] = Field(default=None, description="Generation profile ID")
    variables: dict[str, Any] = Field(default_factory=dict, description="Variables to substitute into placeholders")
    system_prompt_override: Optional[str] = Field(default=None)
    provider: Optional[str] = Field(default=None)
    model: Optional[str] = Field(default=None)
    temperature: Optional[float] = Field(default=None)
    max_tokens: Optional[int] = Field(default=None)
    conversation_id: Optional[uuid.UUID] = None


@router.post(
    "/render",
    status_code=status.HTTP_200_OK,
    summary="Render Prompt Without LLM Generation",
)
async def render_prompt(payload: PromptRenderPayload) -> dict[str, Any]:
    """Renders, validates, lints, and optimizes prompt WITHOUT calling LLM inference."""
    try:
        req = PromptRequest(
            template_id=payload.template_id,
            revision_id=payload.revision_id,
            profile_id=payload.profile_id,
            variables=payload.variables,
            system_prompt_override=payload.system_prompt_override,
            provider=payload.provider,
            model=payload.model,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
            conversation_id=payload.conversation_id,
        )

        result: PromptResult = await _prompt_manager.render(req)
        return success_response(
            data=result.model_dump(),
            message="Prompt rendered successfully",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 500),
            detail=f"Prompt render failed: {exc}",
        )


@router.post(
    "/execute",
    status_code=status.HTTP_200_OK,
    summary="Render and Execute Prompt via LLM Runtime",
)
async def execute_prompt(payload: PromptRenderPayload) -> dict[str, Any]:
    """Renders prompt via pipeline and executes end-to-end LLM generation turn via RuntimeManager."""
    try:
        req = PromptRequest(
            template_id=payload.template_id,
            revision_id=payload.revision_id,
            profile_id=payload.profile_id,
            variables=payload.variables,
            system_prompt_override=payload.system_prompt_override,
            provider=payload.provider,
            model=payload.model,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
            conversation_id=payload.conversation_id,
        )

        result: PromptResult = await _prompt_manager.execute(req)
        return success_response(
            data=result.model_dump(),
            message="Prompt rendered and executed successfully",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 500),
            detail=f"Prompt execution failed: {exc}",
        )


@router.get(
    "/templates",
    status_code=status.HTTP_200_OK,
    summary="List Registered Prompt Templates",
)
async def list_templates() -> dict[str, Any]:
    """Returns all registered prompt templates and revision details."""
    templates = [
        {
            "template_id": t.template_id,
            "template_type": t.template_type,
            "system_instruction": t.system_instruction,
            "variables": [v.model_dump() for v in t.variables],
            "messages": [m.model_dump() for m in t.messages],
            "parent_template_id": t.parent_template_id,
            "revisions": list(t.revisions.keys()),
        }
        for t in _prompt_manager.registry.list_templates()
    ]
    return success_response(
        data=templates,
        message="Registered prompt templates retrieved",
    )


@router.get(
    "/profiles",
    status_code=status.HTTP_200_OK,
    summary="List Registered Prompt Profiles",
)
async def list_profiles() -> dict[str, Any]:
    """Returns all registered generation profiles."""
    profiles = [p.model_dump() for p in _prompt_manager.registry.list_profiles()]
    return success_response(
        data=profiles,
        message="Registered prompt profiles retrieved",
    )


@router.get(
    "/templates/{template_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Prompt Template Details",
)
async def get_template_details(template_id: str) -> dict[str, Any]:
    """Returns details for specified prompt template."""
    t = _prompt_manager.registry.get_template(template_id)
    if not t:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found.")

    return success_response(
        data={
            "template_id": t.template_id,
            "template_type": t.template_type,
            "system_instruction": t.system_instruction,
            "variables": [v.model_dump() for v in t.variables],
            "messages": [m.model_dump() for m in t.messages],
            "parent_template_id": t.parent_template_id,
            "revisions": {k: v.model_dump() for k, v in t.revisions.items()},
        },
        message=f"Details for template '{template_id}' retrieved",
    )


@router.get(
    "/history",
    status_code=status.HTTP_200_OK,
    summary="Get Prompt Execution History & Snapshots",
)
async def get_prompt_history(limit: int = Query(default=20, ge=1, le=100)) -> dict[str, Any]:
    """Returns recent prompt execution results and rendering snapshots."""
    results = await _prompt_manager.execution_store.list_recent_results(limit=limit)
    snapshots = await _prompt_manager.execution_store.list_recent_snapshots(limit=limit)

    return success_response(
        data={
            "results": [r.model_dump() for r in results],
            "snapshots": [s.model_dump() for s in snapshots],
        },
        message="Prompt history retrieved",
    )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Check Prompt Engine Health",
)
async def get_prompt_health() -> dict[str, Any]:
    """Returns health status report for Prompt Execution Engine."""
    health_status = await _prompt_manager.health_manager.check_health()
    return success_response(
        data=health_status.model_dump(),
        message="Prompt Engine health report retrieved",
    )
