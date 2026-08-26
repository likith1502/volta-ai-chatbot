from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.agents.contracts import (
    AgentDelegatePayload,
    AgentExecutePayload,
    AgentMessagePayload,
    AgentRegisterPayload,
    AgentTaskPayload,
)
from app.agents.manager import AgentRuntimeManager
from app.utils.responses import success_response

router = APIRouter(
    prefix="/agents", tags=["Enterprise Multi-Agent Orchestration Runtime"]
)

_agent_runtime_manager = AgentRuntimeManager()


@router.post(
    "/register",
    status_code=status.HTTP_200_OK,
    summary="Register Agent Worker",
)
async def register_agent(payload: AgentRegisterPayload) -> dict[str, Any]:
    """Registers a new agent instance."""
    try:
        agent = await _agent_runtime_manager.register_agent(payload)
        return success_response(
            data={
                "agent_id": agent.agent_id,
                "name": agent.name,
                "role": str(agent.role),
            },
            message=f"Agent '{agent.name}' registered successfully.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Registration failed: {exc}")


@router.post(
    "/execute",
    status_code=status.HTTP_200_OK,
    summary="Execute Agent Task Turn",
)
async def execute_agent_task(payload: AgentExecutePayload) -> dict[str, Any]:
    """Executes a single agent task turn."""
    try:
        result = await _agent_runtime_manager.execute_task(payload)
        return success_response(
            data=result.model_dump(),
            message=f"Task '{payload.task_title}' executed by agent '{payload.agent_id}'.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 500),
            detail=f"Agent execution failed: {exc}",
        )


@router.post(
    "/delegate",
    status_code=status.HTTP_200_OK,
    summary="Delegate Task Between Agents",
)
async def delegate_task(payload: AgentDelegatePayload) -> dict[str, Any]:
    """Delegates a sub-task from delegator agent to delegatee agent."""
    try:
        task = await _agent_runtime_manager.delegate_task(payload)
        return success_response(
            data=task.model_dump(),
            message=f"Task delegated to '{payload.delegatee_agent_id}'.",
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Delegation failed: {exc}")


@router.post(
    "/message",
    status_code=status.HTTP_200_OK,
    summary="Send Inter-Agent Message",
)
async def send_agent_message(payload: AgentMessagePayload) -> dict[str, Any]:
    """Sends an inter-agent message to target mailbox."""
    try:
        msg = await _agent_runtime_manager.send_message(payload)
        return success_response(
            data=msg.model_dump(),
            message=f"Message sent to mailbox of '{payload.recipient_agent_id}'.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Message sending failed: {exc}")


@router.post(
    "/task",
    status_code=status.HTTP_200_OK,
    summary="Enqueue Agent Task",
)
async def enqueue_agent_task(payload: AgentTaskPayload) -> dict[str, Any]:
    """Enqueues task into priority TaskQueue."""
    try:
        task = await _agent_runtime_manager.enqueue_task(payload)
        return success_response(
            data=task.model_dump(),
            message=f"Task '{payload.title}' enqueued with priority {payload.priority}.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Task enqueue failed: {exc}")


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="List Registered Agents",
)
async def list_agents() -> dict[str, Any]:
    """Returns list of all registered agents."""
    agents = await _agent_runtime_manager.list_agents()
    return success_response(
        data=[
            {
                "agent_id": a.agent_id,
                "name": a.name,
                "role": str(a.role),
                "status": str(a.status),
            }
            for a in agents
        ],
        message="Registered agents retrieved.",
    )


@router.get(
    "/statistics",
    status_code=status.HTTP_200_OK,
    summary="Get Multi-Agent Statistics",
)
async def get_agent_statistics() -> dict[str, Any]:
    """Returns statistics snapshot of Multi-Agent Runtime operations."""
    stats = await _agent_runtime_manager.get_statistics()
    return success_response(
        data=stats.model_dump(),
        message="Multi-Agent statistics retrieved.",
    )


@router.get(
    "/analytics",
    status_code=status.HTTP_200_OK,
    summary="Get Multi-Agent Analytics",
)
async def get_agent_analytics() -> dict[str, Any]:
    """Returns analytics telemetry report for Multi-Agent execution."""
    report = _agent_runtime_manager.analytics_manager.get_report()
    return success_response(
        data=report.model_dump(),
        message="Multi-Agent analytics report retrieved.",
    )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Check Multi-Agent Runtime Health",
)
async def get_agent_health() -> dict[str, Any]:
    """Returns health status report for Multi-Agent Runtime."""
    health_status = await _agent_runtime_manager.health_manager.check_health()
    return success_response(
        data=health_status.model_dump(),
        message="Multi-Agent Runtime health report retrieved.",
    )


@router.get(
    "/{agent_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Agent Details by ID",
)
async def get_agent_by_id(agent_id: str) -> dict[str, Any]:
    """Retrieves agent details by ID."""
    agent = await _agent_runtime_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found.")
    return success_response(
        data={
            "agent_id": agent.agent_id,
            "name": agent.name,
            "role": str(agent.role),
            "status": str(agent.status),
            "definition": agent.definition.model_dump(),
        },
        message=f"Agent '{agent_id}' retrieved.",
    )
