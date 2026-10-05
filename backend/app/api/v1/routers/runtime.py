import uuid
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.runtime.contracts import ChatMessage, RuntimeRequest
from app.runtime.manager import RuntimeManager
from app.runtime.result import RuntimeResult
from app.utils.responses import success_response

router = APIRouter(prefix="/runtime", tags=["Enterprise LLM Runtime Engine"])

# Global singleton instance for local testing/dev
_runtime_manager = RuntimeManager()


class ChatTurnPayload(BaseModel):
    """API payload for executing a runtime chat completion turn."""

    message: str = Field(..., min_length=1, description="User input message text")
    provider: Optional[str] = Field(default=None, description="'gemini', 'mock'")
    model: Optional[str] = Field(default=None, description="'gemini-2.5-flash', 'gemini-2.5-pro', 'mock-model-v1'")
    system_prompt: Optional[str] = Field(default=None, description="Optional system instruction override")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    conversation_id: Optional[uuid.UUID] = None
    history: list[dict[str, Any]] = Field(default_factory=list, description="Prior conversation turn history")


@router.post(
    "/chat",
    status_code=status.HTTP_200_OK,
    summary="Execute Enterprise LLM Runtime Chat Turn",
)
async def execute_runtime_chat(payload: ChatTurnPayload) -> dict[str, Any]:
    """Executes a complete LLM runtime turn through provider selection, execution engine, retries, and token accounting."""
    try:
        messages = []
        for h in payload.history:
            role = h.get("role", "user")
            content = h.get("content", "")
            if content:
                messages.append(ChatMessage(role=role, content=content))

        messages.append(ChatMessage(role="user", content=payload.message))

        req = RuntimeRequest(
            conversation_id=payload.conversation_id or uuid.uuid4(),
            messages=messages,
            system_prompt=payload.system_prompt,
            provider=payload.provider,
            model=payload.model,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
        )

        result: RuntimeResult = await _runtime_manager.execute(req)

        return success_response(
            data=result.model_dump(),
            message="Runtime chat turn executed successfully",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 500),
            detail=f"Runtime chat execution failed: {exc}",
        )


@router.get(
    "/providers",
    status_code=status.HTTP_200_OK,
    summary="List Registered Runtime Providers",
)
async def list_providers() -> dict[str, Any]:
    """Returns list of all registered provider identifiers in RuntimeRegistry."""
    providers = _runtime_manager.registry.list_providers()
    return success_response(
        data=providers,
        message="Registered runtime providers retrieved",
    )


@router.get(
    "/providers/{provider_name}/health",
    status_code=status.HTTP_200_OK,
    summary="Check Provider Health & Capabilities",
)
async def get_provider_health(provider_name: str) -> dict[str, Any]:
    """Checks health status and reports capabilities for specified provider."""
    health_status = await _runtime_manager.health_manager.check_provider_health(provider_name)
    return success_response(
        data=health_status.model_dump(),
        message=f"Health status for provider '{provider_name}' retrieved",
    )


@router.get(
    "/models",
    status_code=status.HTTP_200_OK,
    summary="List Registered Models & Pricing Metadata",
)
async def list_models(provider: Optional[str] = Query(default=None)) -> dict[str, Any]:
    """Returns list of all model definitions and cost structures from ModelRegistry."""
    models = [m.model_dump() for m in _runtime_manager.model_registry.list_models(provider=provider)]
    return success_response(
        data=models,
        message="Registered models retrieved",
    )


@router.get(
    "/config",
    status_code=status.HTTP_200_OK,
    summary="Get Active Runtime Configuration",
)
async def get_runtime_config() -> dict[str, Any]:
    """Returns current active runtime engine configuration."""
    return success_response(
        data=_runtime_manager.config.model_dump(),
        message="Active runtime configuration retrieved",
    )


@router.get(
    "/executions",
    status_code=status.HTTP_200_OK,
    summary="List Execution History",
)
async def list_execution_history(limit: int = Query(default=20, ge=1, le=100)) -> dict[str, Any]:
    """Returns recent execution history records from RuntimeExecutionStore."""
    records = await _runtime_manager.execution_store.list_recent(limit=limit)
    return success_response(
        data=[r.model_dump() for r in records],
        message="Recent execution history retrieved",
    )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Check LLM Runtime Health",
)
async def get_runtime_health() -> dict[str, Any]:
    """Returns health status report for LLM Runtime Engine."""
    providers_health = await _runtime_manager.health_manager.check_all_providers()
    data = {k: v.model_dump() for k, v in providers_health.items()}
    return success_response(
        data=data,
        message="LLM Runtime Engine health report retrieved",
    )
