"""Phase 7.8 — Deployment REST API Router.

Endpoints:
  POST /api/v1/deployment/validate
  POST /api/v1/deployment/deploy
  POST /api/v1/deployment/rollback
  POST /api/v1/deployment/scale
  GET  /api/v1/deployment/status
  GET  /api/v1/deployment/health
  GET  /api/v1/deployment/statistics
  GET  /api/v1/deployment/analytics
  GET  /api/v1/deployment/environment
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Any, Optional
from dataclasses import asdict

from app.deployment.manager import DeploymentManager
from app.deployment.contracts import (
    DeploymentValidatePayload,
    DeploymentDeployPayload,
    DeploymentRollbackPayload,
    DeploymentScalePayload,
)

router = APIRouter(prefix="/deployment", tags=["Deployment (v7.8)"])

_manager = DeploymentManager()


def _ok(data: Any) -> dict:
    return {"success": True, "data": data}


def _err(msg: str) -> dict:
    return {"success": False, "error": msg}


@router.post("/validate")
async def validate_deployment(payload: DeploymentValidatePayload) -> dict:
    try:
        report = await _manager.validate(payload)
        return _ok({
            "deployment_id": report.deployment_id,
            "all_passed": report.all_passed,
            "passed_count": report.passed_count,
            "failed_count": report.failed_count,
            "checks": [asdict(c) for c in report.checks],
            "warnings": report.warnings,
            "errors": report.errors,
        })
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/deploy")
async def deploy(payload: DeploymentDeployPayload) -> dict:
    try:
        deployment = await _manager.deploy(payload)
        return _ok(deployment.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/rollback")
async def rollback(payload: DeploymentRollbackPayload) -> dict:
    try:
        result = await _manager.rollback(payload)
        return _ok(result)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/scale")
async def scale(payload: DeploymentScalePayload) -> dict:
    try:
        from dataclasses import asdict as _asdict
        event = await _manager.scale(payload)
        return _ok(_asdict(event))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/status")
async def get_status(deployment_id: str = Query(default="volta-platform-v7.8")) -> dict:
    try:
        status = await _manager.get_deployment_status(deployment_id)
        return _ok(status.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/health")
async def get_health() -> dict:
    try:
        from dataclasses import asdict as _asdict
        summary = await _manager.get_platform_health()
        return _ok({
            "overall_health": summary.overall_health.value,
            "total_deployments": summary.total_deployments,
            "healthy_deployments": summary.healthy_deployments,
            "degraded_deployments": summary.degraded_deployments,
            "failed_deployments": summary.failed_deployments,
            "layer_status": summary.layer_status,
        })
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/statistics")
async def get_statistics() -> dict:
    try:
        stats = _manager.get_statistics()
        return _ok(asdict(stats))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/analytics")
async def get_analytics() -> dict:
    try:
        analytics = _manager.get_analytics()
        return _ok(analytics)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/environment")
async def get_environment() -> dict:
    try:
        env = _manager.environment_manager.active_environment
        if not env:
            raise HTTPException(status_code=404, detail="No active environment.")
        from dataclasses import asdict as _asdict
        return _ok(_asdict(env))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
