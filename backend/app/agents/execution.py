import time
import logging
from typing import Any, Optional
from app.agents.agent import Agent
from app.agents.context import AgentContext
from app.agents.exceptions import AgentBudgetExhaustedError, AgentPermissionDeniedError
from app.agents.lifecycle import AgentLifecycleState
from app.agents.permissions import AgentPermission
from app.agents.status import AgentStatus
from app.agents.task import AgentTask, TaskResult, TaskStatus
from app.events.event import WorkflowEvent
from app.events.event_bus import WorkflowEventBus
from app.memory.manager import MemoryManager
from app.prompt.manager import PromptManager
from app.runtime.manager import RuntimeManager
from app.tools.contracts import ToolExecutePayload
from app.tools.manager import ToolManager

logger = logging.getLogger("app.agents.execution")


class AgentExecution:
    """Orchestrates single-agent task execution turns via public runtime managers."""

    def __init__(
        self,
        prompt_manager: Optional[PromptManager] = None,
        memory_manager: Optional[MemoryManager] = None,
        tool_manager: Optional[ToolManager] = None,
        runtime_manager: Optional[RuntimeManager] = None,
        event_bus: Optional[WorkflowEventBus] = None,
    ) -> None:
        self.prompt_manager = prompt_manager or PromptManager()
        self.memory_manager = memory_manager or MemoryManager()
        self.tool_manager = tool_manager or ToolManager()
        self.runtime_manager = runtime_manager or RuntimeManager()
        self.event_bus = event_bus or WorkflowEventBus()

    async def execute_turn(self, agent: Agent, task: AgentTask, context: AgentContext) -> TaskResult:
        """Executes a single agent task turn."""
        t0 = time.perf_counter()

        # 1. Budget check
        if agent.is_budget_exhausted():
            raise AgentBudgetExhaustedError(f"Agent '{agent.name}' budget exhausted.")

        # 2. Lifecycle transition
        if agent.instance.lifecycle.current_state == AgentLifecycleState.CREATED:
            agent.transition_lifecycle(AgentLifecycleState.REGISTERED)
            agent.transition_lifecycle(AgentLifecycleState.READY)
        agent.transition_lifecycle(AgentLifecycleState.RUNNING)
        agent.set_status(AgentStatus.BUSY)

        # 3. Publish start event
        try:
            await self.event_bus.publish(WorkflowEvent(
                event_name="agent_execution.started",
                payload={"agent_id": agent.agent_id, "task_id": task.task_id},
                source="agent_execution",
            ))
        except Exception:
            pass

        # 4. Perform task logic via public managers
        # If tool execution requested and permitted
        tool_output = {}
        if agent.has_permission(AgentPermission.CAN_EXECUTE_TOOLS) and "tool_name" in task.inputs:
            tool_name = task.inputs["tool_name"]
            tool_args = task.inputs.get("tool_args", {})
            try:
                res = await self.tool_manager.execute_tool(ToolExecutePayload(tool_name=tool_name, arguments=tool_args))
                tool_output = res.model_dump()
            except Exception as exc:
                logger.warning(f"Tool execution failed: {exc}")

        dt = (time.perf_counter() - t0) * 1000.0

        # Update budget runtime
        agent.definition.policy.budget.current_runtime_ms += dt

        agent.transition_lifecycle(AgentLifecycleState.COMPLETED)
        agent.set_status(AgentStatus.IDLE)

        # Publish completion event
        try:
            await self.event_bus.publish(WorkflowEvent(
                event_name="agent_execution.completed",
                payload={"agent_id": agent.agent_id, "task_id": task.task_id, "latency_ms": dt},
                source="agent_execution",
            ))
        except Exception:
            pass

        return TaskResult(
            task_id=task.task_id,
            assigned_agent_id=agent.agent_id,
            status=TaskStatus.COMPLETED,
            output={"result": f"Agent '{agent.name}' executed task '{task.title}'", "tool_output": tool_output},
            latency_ms=round(dt, 2),
        )
