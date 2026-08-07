import uuid
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.prompt.contracts import ChatMessage, PromptMessage, PromptRequest
from app.prompt.cost import PromptCostEstimator
from app.prompt.manager import PromptManager
from app.prompt.result import PromptResult
from app.prompt.templates.chat_template import ChatPromptTemplate
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


class ScratchPromptPayload(BaseModel):
    """Payload for unsaved scratch prompt sandbox execution."""

    system_instruction: str = Field(default="You are a helpful AI assistant.")
    user_prompt_template: str = Field(..., description="Raw text template string containing {placeholders}")
    variables: dict[str, Any] = Field(default_factory=dict)
    provider: Optional[str] = Field(default="mock")
    model: Optional[str] = Field(default="mock-model-v1")


class ProviderComparePayload(BaseModel):
    """Payload for comparing prompt execution across multiple providers."""

    template_id: str = "mobility_assistant_v1"
    variables: dict[str, Any] = Field(default_factory=lambda: {"city_name": "San Francisco", "user_name": "Likith"})
    providers: list[str] = Field(default_factory=lambda: ["mock", "gemini"])


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


@router.post(
    "/sandbox/execute",
    status_code=status.HTTP_200_OK,
    summary="Execute Unsaved Scratch Prompt (Sandbox Mode)",
)
async def execute_scratch_prompt(payload: ScratchPromptPayload) -> dict[str, Any]:
    """Executes an unsaved scratch prompt template directly in sandbox mode."""
    try:
        scratch_id = f"scratch_{uuid.uuid4().hex[:8]}"
        template = ChatPromptTemplate(
            template_id=scratch_id,
            system_instruction=payload.system_instruction,
        )
        template.add_message(role="user", content_template=payload.user_prompt_template)
        _prompt_manager.registry.register_template(template)

        req = PromptRequest(
            template_id=scratch_id,
            variables=payload.variables,
            provider=payload.provider,
            model=payload.model,
        )

        result: PromptResult = await _prompt_manager.execute(req)
        _prompt_manager.registry.unregister_template(scratch_id)

        return success_response(
            data=result.model_dump(),
            message="Scratch prompt sandbox executed successfully",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 500),
            detail=f"Scratch prompt execution failed: {exc}",
        )


@router.post(
    "/compare",
    status_code=status.HTTP_200_OK,
    summary="Compare Provider Execution Side-by-Side",
)
async def compare_providers(payload: ProviderComparePayload) -> dict[str, Any]:
    """Executes the same prompt request across multiple providers side-by-side to compare latency, tokens, cost, and output."""
    results: dict[str, Any] = {}
    for prov in payload.providers:
        try:
            req = PromptRequest(
                template_id=payload.template_id,
                variables=payload.variables,
                provider=prov,
            )
            res = await _prompt_manager.execute(req)
            results[prov] = res.model_dump()
        except Exception as exc:
            results[prov] = {"error": str(exc)}

    return success_response(
        data=results,
        message=f"Side-by-side provider comparison for '{payload.template_id}' completed",
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
