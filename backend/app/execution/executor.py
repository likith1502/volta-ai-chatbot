from typing import Any, List, Optional

from app.context.events import WorkflowEvent, WorkflowEventType
from app.context.state import ConversationState
from app.execution.dispatcher import ExecutionDispatcher
from app.execution.exceptions import ExecutionValidationException
from app.execution.execution_context import ExecutionContext
from app.execution.execution_policy import ExecutionPolicy
from app.execution.execution_result import ExecutionResult
from app.execution.execution_strategy import ExecutionStrategy, SequentialStrategy
from app.execution.planner import ExecutionPlanner
from app.execution.scheduler import ExecutionScheduler
from app.graph.contracts import IGraph, IGraphExecutor


class GraphExecutor(IGraphExecutor):
    """
    Core Provider-Independent Graph Execution Engine.
    Executes compiled Graph objects, coordinates graph traversal, enforces execution policy,
    dispatches node lifecycle hooks, and records execution metrics and telemetry events.
    """

    def __init__(
        self,
        strategy: Optional[ExecutionStrategy] = None,
        policy: Optional[ExecutionPolicy] = None,
        dispatcher: Optional[ExecutionDispatcher] = None,
        scheduler: Optional[ExecutionScheduler] = None,
        planner: Optional[ExecutionPlanner] = None,
    ) -> None:
        self.strategy = strategy or SequentialStrategy()
        self.policy = policy or ExecutionPolicy()
        self.dispatcher = dispatcher or ExecutionDispatcher()
        self.scheduler = scheduler or ExecutionScheduler()
        self.planner = planner or ExecutionPlanner()
        self.events: List[WorkflowEvent] = []

    def _emit_event(self, event_type: WorkflowEventType, conversation_id: Any, payload: dict) -> None:
        if self.policy.emit_events:
            evt = WorkflowEvent(
                event_type=event_type,
                conversation_id=conversation_id,
                payload=payload,
            )
            self.events.append(evt)

    async def execute(
        self,
        graph: IGraph,
        initial_state: ConversationState,
    ) -> ExecutionResult:
        """
        Executes graph starting from entry node to completion.
        Performs mandatory pre-execution graph validation prior to execution.
        """
        # 1. Mandatory Graph Validation Before Execution
        try:
            validation_res = graph.validate()
            if hasattr(validation_res, "is_valid") and not validation_res.is_valid:
                errors = getattr(validation_res, "errors", [])
                raise ExecutionValidationException(
                    f"Graph validation failed prior to execution. Errors: {errors}"
                )
        except ExecutionValidationException:
            raise
        except Exception as exc:
            raise ExecutionValidationException(
                f"Graph validation failed prior to execution: {str(exc)}"
            ) from exc

        conv_id = getattr(getattr(initial_state, "conversation", None), "conversation_id", None) or initial_state.metadata.state_id

        context = ExecutionContext(
            graph_id=graph.metadata.name or "graph",
            workflow_id=str(conv_id),
        )

        # Emit ExecutionStarted
        self._emit_event(
            event_type=WorkflowEventType.WORKFLOW_STARTED,
            conversation_id=conv_id,
            payload={"graph_id": graph.metadata.name, "execution_id": str(context.execution_id)},
        )

        try:
            # 2. Execute via Strategy
            result = await self.strategy.execute(
                graph=graph,
                initial_state=initial_state,
                policy=self.policy,
                dispatcher=self.dispatcher,
                scheduler=self.scheduler,
                context=context,
            )

            # Emit ExecutionCompleted or ExecutionFailed
            if result.execution_status.value == "completed":
                self._emit_event(
                    event_type=WorkflowEventType.WORKFLOW_COMPLETED,
                    conversation_id=conv_id,
                    payload={"visited_nodes": result.visited_nodes},
                )
            else:
                self._emit_event(
                    event_type=WorkflowEventType.WORKFLOW_FAILED,
                    conversation_id=conv_id,
                    payload={"errors": result.errors},
                )

            return result

        except Exception as exc:
            self._emit_event(
                event_type=WorkflowEventType.WORKFLOW_FAILED,
                conversation_id=conv_id,
                payload={"error": str(exc)},
            )
            raise exc
