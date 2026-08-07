import logging
import time
import uuid
from typing import Any, Optional

from app.agents.agent import Agent
from app.agents.analytics import AgentAnalyticsManager
from app.agents.communication import CommunicationManager
from app.agents.context import AgentContext
from app.agents.contracts import (
    AgentDelegatePayload,
    AgentExecutePayload,
    AgentMessagePayload,
    AgentRegisterPayload,
    AgentTaskPayload,
    TeamCreatePayload,
)
from app.agents.definition import AgentDefinition
from app.agents.delegator import DelegationManager
from app.agents.exceptions import AgentNotFoundError
from app.agents.execution import AgentExecution
from app.agents.factory import AgentFactory
from app.agents.health import AgentHealthManager, AgentHealthStatus
from app.agents.identity import AgentIdentity
from app.agents.message import AgentMessage
from app.agents.persona import AgentPersona
from app.agents.registry import AgentRegistry
from app.agents.role import AgentRole
from app.agents.scheduler import TaskScheduler
from app.agents.statistics import AgentStatistics
from app.agents.supervisor import SupervisorAgent
from app.agents.task import AgentTask, TaskResult
from app.agents.task_queue import TaskQueue
from app.agents.team import AgentTeam
from app.agents.team_manager import TeamManager
from app.events.event_bus import WorkflowEventBus
from app.memory.manager import MemoryManager
from app.prompt.manager import PromptManager
from app.runtime.manager import RuntimeManager
from app.tools.manager import ToolManager

logger = logging.getLogger("app.agents.manager")


class AgentRuntimeManager:
    """Single central orchestration entry point for the Enterprise Multi-Agent Orchestration Runtime.

    Manages agent registry, worker lifecycle, task queues, delegation, inter-agent mailboxes, team composition, and lower layer runtime facades.
    """

    def __init__(
        self,
        event_bus: Optional[WorkflowEventBus] = None,
        registry: Optional[AgentRegistry] = None,
        team_manager: Optional[TeamManager] = None,
        prompt_manager: Optional[PromptManager] = None,
        memory_manager: Optional[MemoryManager] = None,
        tool_manager: Optional[ToolManager] = None,
        runtime_manager: Optional[RuntimeManager] = None,
    ) -> None:
        self.event_bus = event_bus or WorkflowEventBus()
        self.registry = registry or AgentRegistry()
        self.team_manager = team_manager or TeamManager()

        self.prompt_manager = prompt_manager or PromptManager()
        self.memory_manager = memory_manager or MemoryManager()
        self.tool_manager = tool_manager or ToolManager()
        self.runtime_manager = runtime_manager or RuntimeManager()

        self.communication_manager = CommunicationManager(event_bus=self.event_bus)
        self.delegation_manager = DelegationManager()
        self.task_queue = TaskQueue()
        self.scheduler = TaskScheduler(task_queue=self.task_queue)
        self.executor = AgentExecution(
            prompt_manager=self.prompt_manager,
            memory_manager=self.memory_manager,
            tool_manager=self.tool_manager,
            runtime_manager=self.runtime_manager,
            event_bus=self.event_bus,
        )

        self.health_manager = AgentHealthManager(registry=self.registry)
        self.analytics_manager = AgentAnalyticsManager()
        self.statistics = AgentStatistics()

        # Pre-seed reference agents if registry empty
        self._seed_reference_agents()

    def _seed_reference_agents(self) -> None:
        if not self.registry.list_agents():
            sup = SupervisorAgent()
            self.registry.register_agent(sup)

            worker1 = AgentFactory.create_worker("Ride Discovery Agent", role=AgentRole.RESEARCH)
            self.registry.register_agent(worker1)

            worker2 = AgentFactory.create_worker("Booking Tool Agent", role=AgentRole.TOOL)
            self.registry.register_agent(worker2)

            self.team_manager.create_team(
                name="Volta Mobility Team",
                supervisor_id=sup.agent_id,
                member_ids=[worker1.agent_id, worker2.agent_id],
            )

    async def register_agent(self, payload: AgentRegisterPayload) -> Agent:
        """Registers a new agent instance from payload specs."""
        identity = AgentIdentity(name=payload.name)
        persona = AgentPersona(communication_style=payload.communication_style, tone=payload.tone)
        role = AgentRole(payload.role)
        definition = AgentDefinition(identity=identity, role=role, persona=persona)
        agent = Agent(definition=definition)

        self.registry.register_agent(agent)
        self.statistics.total_registered_agents += 1
        return agent

    async def execute_task(self, payload: AgentExecutePayload) -> TaskResult:
        """Executes a task turn with target agent."""
        agent = self.registry.get_agent(payload.agent_id)
        if not agent:
            raise AgentNotFoundError(f"Agent '{payload.agent_id}' not found.")

        task = AgentTask(title=payload.task_title, inputs=payload.inputs)
        context = AgentContext(inputs=payload.inputs)

        result = await self.executor.execute_turn(agent, task, context)
        self.analytics_manager.record_task_execution(
            duration_ms=result.latency_ms,
            success=(result.status == "completed"),
            role=agent.role,
        )
        self.statistics.total_tasks_executed += 1
        return result

    async def delegate_task(self, payload: AgentDelegatePayload) -> AgentTask:
        """Delegates task from delegator agent to delegatee agent."""
        delegator = self.registry.get_agent(payload.delegator_agent_id)
        delegatee = self.registry.get_agent(payload.delegatee_agent_id)

        if not delegator or not delegatee:
            raise AgentNotFoundError("Delegator or Delegatee agent not found.")

        task = self.delegation_manager.delegate_task(
            delegator=delegator,
            delegatee=delegatee,
            task_title=payload.task_title,
            inputs=payload.inputs,
            current_depth=payload.current_depth,
        )
        self.statistics.total_delegations += 1
        return task

    async def send_message(self, payload: AgentMessagePayload) -> AgentMessage:
        """Sends inter-agent message to target mailbox."""
        msg = AgentMessage(
            sender_agent_id=payload.sender_agent_id,
            recipient_agent_id=payload.recipient_agent_id,
            content=payload.content,
        )
        await self.communication_manager.send_message(msg)
        self.statistics.total_messages_sent += 1
        return msg

    async def enqueue_task(self, payload: AgentTaskPayload) -> AgentTask:
        """Enqueues task into priority TaskQueue."""
        task = AgentTask(title=payload.title, priority=payload.priority, inputs=payload.inputs)
        self.task_queue.enqueue(task)
        return task

    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        return self.registry.get_agent(agent_id)

    async def list_agents(self) -> list[Agent]:
        return self.registry.list_agents()

    async def get_statistics(self) -> AgentStatistics:
        report = self.analytics_manager.get_report()
        self.statistics.average_task_latency_ms = report.average_duration_ms
        self.statistics.active_workers_count = len(self.registry.find_available())
        return self.statistics
