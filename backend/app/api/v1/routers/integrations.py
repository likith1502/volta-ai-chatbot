from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.integrations.capabilities import IntegrationCapability
from app.integrations.contracts import (
    IntegrationConfigurePayload,
    IntegrationProviderRegisterPayload,
    IntegrationTestPayload,
)
from app.integrations.manager import IntegrationManager
from app.utils.responses import success_response

router = APIRouter(prefix="/integrations", tags=["Enterprise Integration Platform"])

_integration_manager = IntegrationManager()


@router.get(
    "/providers",
    status_code=status.HTTP_200_OK,
    summary="List Registered Integration Providers",
)
async def list_providers(
    category: Optional[str] = Query(default=None),
) -> dict[str, Any]:
    """Lists registered production integration adapters."""
    cap = IntegrationCapability(category) if category else None
    providers = _integration_manager.list_providers(cap)
    return success_response(
        data=[
            {
                "provider_id": p.provider_id,
                "name": p.name,
                "category": p.category.value,
                "priority": p.priority,
                "status": str(p.status),
                "health_level": str(p.health_level),
            }
            for p in providers
        ],
        message="Integration providers retrieved.",
    )


@router.get(
    "/providers/{provider_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Provider Details by ID",
)
async def get_provider_by_id(provider_id: str) -> dict[str, Any]:
    """Retrieves provider configuration & manifest details."""
    p = _integration_manager.get_provider(provider_id)
    if not p:
        raise HTTPException(
            status_code=404, detail=f"Provider '{provider_id}' not found."
        )
    return success_response(
        data={
            "provider_id": p.provider_id,
            "name": p.name,
            "category": p.category.value,
            "priority": p.priority,
            "status": str(p.status),
            "manifest": p.manifest.model_dump(),
        },
        message=f"Provider '{provider_id}' details retrieved.",
    )


@router.post(
    "/providers/register",
    status_code=status.HTTP_200_OK,
    summary="Register Integration Provider",
)
async def register_provider(
    payload: IntegrationProviderRegisterPayload,
) -> dict[str, Any]:
    """Registers a new integration provider adapter."""
    try:
        adapter = await _integration_manager.register_provider(payload)
        return success_response(
            data={
                "provider_id": adapter.provider_id,
                "name": adapter.name,
                "category": adapter.category.value,
            },
            message=f"Provider '{payload.provider_id}' registered successfully.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Provider registration failed: {exc}"
        )


@router.post(
    "/providers/configure",
    status_code=status.HTTP_200_OK,
    summary="Configure Provider Options",
)
async def configure_provider(payload: IntegrationConfigurePayload) -> dict[str, Any]:
    """Configures adapter options."""
    try:
        res = await _integration_manager.configure_provider(payload)
        return success_response(
            data={"provider_id": payload.provider_id, "configured": res},
            message=f"Provider '{payload.provider_id}' configured.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Provider configuration failed: {exc}"
        )


@router.post(
    "/providers/test",
    status_code=status.HTTP_200_OK,
    summary="Test Provider Connection",
)
async def test_provider_connection(payload: IntegrationTestPayload) -> dict[str, Any]:
    """Executes live connectivity test."""
    try:
        res = await _integration_manager.test_provider_connection(payload)
        return success_response(
            data=res,
            message=f"Provider '{payload.provider_id}' connection test completed.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Connection test failed: {exc}")


@router.get(
    "/statistics",
    status_code=status.HTTP_200_OK,
    summary="Get Integration Statistics",
)
async def get_integration_statistics() -> dict[str, Any]:
    """Returns platform integration statistics."""
    stats = _integration_manager.statistics
    return success_response(
        data=stats.model_dump(),
        message="Integration statistics retrieved.",
    )


@router.get(
    "/analytics",
    status_code=status.HTTP_200_OK,
    summary="Get Integration Analytics",
)
async def get_integration_analytics() -> dict[str, Any]:
    """Returns integration analytics report."""
    metrics = _integration_manager.metrics
    return success_response(
        data=metrics.model_dump(),
        message="Integration metrics retrieved.",
    )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Get Platform Aggregated Health Report",
)
async def get_platform_health() -> dict[str, Any]:
    """Returns unified platform aggregated health report."""
    health_report = await _integration_manager.check_platform_health()
    return success_response(
        data=health_report.model_dump(),
        message="Platform health report retrieved.",
    )
