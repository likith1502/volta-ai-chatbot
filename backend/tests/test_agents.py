import pytest
import uuid
from app.agents.agent import Agent
from app.agents.budget import AgentExecutionBudget
from app.agents.definition import AgentDefinition
from app.agents.delegator import DelegationManager
from app.agents.exceptions import AgentBudgetExhaustedError, AgentDelegationError, AgentPermissionDeniedError
from app.agents.factory import AgentFactory
from app.agents.identity import AgentIdentity
from app.agents.lifecycle import AgentLifecycleManager, AgentLifecycleState
from app.agents.manager import AgentRuntimeManager
from app.agents.message import AgentMessage
from app.agents.permissions import AgentPermission, AgentPermissionSet
from app.agents.persona import AgentPersona
from app.agents.role import AgentRole
from app.agents.status import AgentStatus
from app.agents.supervisor import SupervisorAgent
from app.agents.task import AgentTask, TaskResult
from app.agents.team import AgentTeam, TeamStatus
from app.agents.team_manager import TeamManager


@pytest.mark.asyncio
async def test_agent_lifecycle_transitions():
    agent = AgentFactory.create_worker("Lifecycle Test Agent")
    assert agent.instance.lifecycle.current_state == AgentLifecycleState.CREATED

    assert agent.transition_lifecycle(AgentLifecycleState.REGISTERED) is True
    assert agent.instance.lifecycle.current_state == AgentLifecycleState.REGISTERED

    assert agent.transition_lifecycle(AgentLifecycleState.READY) is True
    assert agent.transition_lifecycle(AgentLifecycleState.RUNNING) is True
    assert agent.instance.lifecycle.current_state == AgentLifecycleState.RUNNING

    # Invalid transition directly to CREATED
    assert agent.transition_lifecycle(AgentLifecycleState.CREATED) is False


@pytest.mark.asyncio
async def test_delegation_permissions_and_depth_limits():
    delegator_def = AgentDefinition(identity=AgentIdentity(name="Delegator Agent"), role=AgentRole.SUPERVISOR)
    delegator_def.policy.permissions.grant(AgentPermission.CAN_DELEGATE)
    delegator_def.policy.budget.max_delegation_depth = 2

    delegatee_def = AgentDefinition(identity=AgentIdentity(name="Worker Agent"), role=AgentRole.SUPPORT)
    
    delegator = Agent(definition=delegator_def)
    delegatee = Agent(definition=delegatee_def)

    delegator_mgr = DelegationManager()

    # Valid delegation at depth 1
    task = delegator_mgr.delegate_task(delegator, delegatee, "Subtask 1", {}, current_depth=1)
    assert task.assigned_agent_id == delegatee.agent_id

    # Exceeded depth limit at depth 3
    with pytest.raises(AgentDelegationError):
        delegator_mgr.delegate_task(delegator, delegatee, "Loop Subtask", {}, current_depth=3)


@pytest.mark.asyncio
async def test_permission_failure():
    no_perm_def = AgentDefinition(identity=AgentIdentity(name="Restricted Agent"))
    no_perm_def.policy.permissions.revoke(AgentPermission.CAN_DELEGATE)
    agent_restricted = Agent(definition=no_perm_def)

    target = AgentFactory.create_worker("Target Worker")
    delegator_mgr = DelegationManager()

    with pytest.raises(AgentPermissionDeniedError):
        delegator_mgr.delegate_task(agent_restricted, target, "Unauthorized Delegation", {})


@pytest.mark.asyncio
async def test_budget_exhaustion():
    budget_def = AgentDefinition(identity=AgentIdentity(name="Low Budget Agent"))
    budget_def.policy.permissions.grant(AgentPermission.CAN_DELEGATE)
    budget_def.policy.budget.max_runtime_ms = 100.0
    budget_def.policy.budget.current_runtime_ms = 150.0  # Exhausted

    agent_exhausted = Agent(definition=budget_def)
    assert agent_exhausted.is_budget_exhausted() is True

    target = AgentFactory.create_worker("Target Worker")
    delegator_mgr = DelegationManager()

    with pytest.raises(AgentBudgetExhaustedError):
        delegator_mgr.delegate_task(agent_exhausted, target, "Exhausted Task", {})


@pytest.mark.asyncio
async def test_team_manager_and_registry():
    tm = TeamManager()
    sup = SupervisorAgent()
    w1 = AgentFactory.create_worker("Worker 1")

    team = tm.create_team("Mobility Team", sup.agent_id, [w1.agent_id])
    assert team.status == TeamStatus.READY
    assert len(team.member_agent_ids) == 1
    assert team.supervisor_agent_id == sup.agent_id


@pytest.mark.asyncio
async def test_agent_runtime_manager_execution():
    manager = AgentRuntimeManager()
    agents = await manager.list_agents()
    assert len(agents) >= 3

    worker = agents[1]
    res = await manager.execute_task(
        type("Payload", (), {"agent_id": worker.agent_id, "task_title": "Run discovery", "inputs": {}})()
    )

    assert res.status == "completed"
    assert res.assigned_agent_id == worker.agent_id
