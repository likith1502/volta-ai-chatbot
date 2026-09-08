import logging
import uuid
from typing import Any, Optional, Sequence

from app.ai.base import AIProvider
from app.ai.prompts.prompt_builder import PromptBuilder
from app.ai.tools.dispatcher import AIToolDispatcher
from app.checkpoints.checkpoint_manager import CheckpointManager
from app.checkpoints.checkpoint_store import InMemoryCheckpointStore
from app.context.state import ConversationData, ConversationState
from app.events.event import WorkflowEvent
from app.events.event_bus import WorkflowEventBus
from app.events.event_types import WorkflowEventType
from app.execution.execution_policy import ExecutionPolicy
from app.execution.executor import GraphExecutor
from app.graph.builder import GraphBuilder
from app.graph.contracts import GraphMetadata
from app.graph.edge import GraphEdge
from app.graph.graph import Graph
from app.workflow.nodes.decision_node import DecisionNode
from app.workflow.nodes.end_node import EndNode
from app.workflow.nodes.intent_node import IntentNode
from app.workflow.nodes.llm_node import LLMNode
from app.workflow.nodes.memory_node import MemoryNode
from app.workflow.nodes.response_node import ResponseNode
from app.workflow.nodes.start_node import StartNode
from app.workflow.nodes.tool_node import ToolNode

logger = logging.getLogger("app.services.chat_graph")


class ChatGraphOrchestrator:
    """
    Adapter orchestrating chat interactions through the StateGraph and GraphExecutor runtime.
    Integrates IntentNode, DecisionNode, LLMNode, ToolNode, MemoryNode, ResponseNode,
    CheckpointManager, and WorkflowEventBus.
    """

    def __init__(
        self,
        provider: Optional[AIProvider] = None,
        tool_dispatcher: Optional[AIToolDispatcher] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        event_bus: Optional[WorkflowEventBus] = None,
        checkpoint_manager: Optional[CheckpointManager] = None,
    ) -> None:
        self.provider = provider
        self.tool_dispatcher = tool_dispatcher
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.event_bus = event_bus or WorkflowEventBus()
        self.checkpoint_manager = checkpoint_manager or CheckpointManager(store=InMemoryCheckpointStore())
        self.executor = GraphExecutor(policy=ExecutionPolicy(emit_events=True))

    def build_graph(self) -> Graph:
        """Compiles the production-safe chat execution graph with conditional routing."""
        builder = GraphBuilder()

        # 1. Instantiate Graph Nodes
        start_node = StartNode(node_id="start")
        intent_node = IntentNode(node_id="intent")
        decision_node = DecisionNode(node_id="decision")
        llm_node = LLMNode(
            node_id="llm",
            provider=self.provider,
            prompt_builder=self.prompt_builder,
        )
        tool_node = ToolNode(
            node_id="tool",
            tool_dispatcher=self.tool_dispatcher,
        )
        memory_node = MemoryNode(node_id="memory")
        response_node = ResponseNode(node_id="response")
        end_node = EndNode(node_id="end")

        for node in [
            start_node,
            intent_node,
            decision_node,
            llm_node,
            tool_node,
            memory_node,
            response_node,
            end_node,
        ]:
            builder.add_node(node)

        # 2. Add Directed Edges with Conditional Branching
        # Start -> Intent -> Decision
        builder.add_edge(GraphEdge(source_node="start", target_node="intent", priority=0))
        builder.add_edge(GraphEdge(source_node="intent", target_node="decision", priority=0))

        # Decision -> Direct Tool (if pre-staged tool calls exist)
        builder.add_edge(
            GraphEdge(
                source_node="decision",
                target_node="tool",
                edge_condition=lambda s: s.execution.node_results.get("decision", {}).get("route") == "tool",
                priority=20,
            )
        )

        # Decision -> LLM (default conversational or recommendation path)
        builder.add_edge(
            GraphEdge(
                source_node="decision",
                target_node="llm",
                edge_condition=lambda s: s.execution.node_results.get("decision", {}).get("route") != "tool",
                priority=10,
            )
        )

        # LLM -> Tool (if tool calls requested or recommendation required)
        builder.add_edge(
            GraphEdge(
                source_node="llm",
                target_node="tool",
                edge_condition=lambda s: bool(s.execution.tool_calls)
                or (s.memory.detected_intent and s.memory.detected_intent.get("requires_recommendation")),
                priority=10,
            )
        )

        # LLM -> Memory (fallback if no tool required)
        builder.add_edge(
            GraphEdge(
                source_node="llm",
                target_node="memory",
                priority=5,
            )
        )

        # Tool -> Memory
        builder.add_edge(GraphEdge(source_node="tool", target_node="memory", priority=10))

        # Memory -> Response -> End
        builder.add_edge(GraphEdge(source_node="memory", target_node="response", priority=10))
        builder.add_edge(GraphEdge(source_node="response", target_node="end", priority=10))

        builder.set_entry_node("start")
        builder.set_metadata(GraphMetadata(name="chat_orchestration_graph", version="1.0.0"))

        return builder.build()

    async def execute_chat_turn(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        session_id: str,
        message_text: str,
        history_messages: Sequence[Any] = (),
        memories: Sequence[Any] = (),
    ) -> dict[str, Any]:
        """Executes a complete chat turn through the Graph Runtime."""
        # 1. Prepare Initial ConversationState
        history_payload = [
            {
                "role": getattr(m.role, "value", str(m.role)),
                "content": m.content,
            }
            for m in history_messages
        ]

        conv_data = ConversationData(
            conversation_id=conversation_id,
            user_id=str(user_id),
            current_message={"role": "user", "content": message_text},
            history=history_payload,
        )
        state = ConversationState(conversation=conv_data).with_update(
            short_term_memory={"memories": list(memories)},
        )

        # 2. Publish Workflow Started Event
        try:
            await self.event_bus.publish(
                WorkflowEvent(
                    event_type=WorkflowEventType.EXECUTION_STARTED,
                    workflow_id=str(conversation_id),
                    payload={"session_id": session_id, "user_id": str(user_id)},
                )
            )
        except Exception as evt_exc:
            logger.debug("Event publication non-blocking error: %s", evt_exc)

        # 3. Compile and Execute Graph
        graph = self.build_graph()
        exec_result = await self.executor.execute(graph, state)

        final_state = exec_result.final_state

        # 4. Capture Checkpoint
        try:
            snapshot = exec_result.snapshots[-1] if exec_result.snapshots else None
            checkpoint = self.checkpoint_manager.create_checkpoint(
                workflow_id=str(conversation_id),
                graph_id=graph.metadata.name or "chat_orchestration_graph",
                state=final_state,
                execution_snapshot=snapshot,
            )
            final_state = final_state.with_update(checkpoint_id=checkpoint.checkpoint_id)
        except Exception as cp_exc:
            logger.debug("Checkpoint creation non-blocking error: %s", cp_exc)

        # 5. Publish Workflow Completed Event
        try:
            await self.event_bus.publish(
                WorkflowEvent(
                    event_type=WorkflowEventType.EXECUTION_COMPLETED,
                    workflow_id=str(conversation_id),
                    payload={"visited_nodes": exec_result.visited_nodes},
                )
            )
        except Exception as evt_exc:
            logger.debug("Event publication non-blocking error: %s", evt_exc)

        # 6. Extract Response Turn Elements
        resp_data = final_state.execution.node_results.get("response", {})
        content = resp_data.get("content", "I am here to assist you.")
        model_used = resp_data.get("model_used", "volta-assistant")
        usage = resp_data.get("usage", {})
        total_tokens = resp_data.get("total_tokens", 0)

        rec_id_raw = resp_data.get("recommendation_id")
        recommendation_id: Optional[uuid.UUID] = None
        if rec_id_raw:
            try:
                recommendation_id = uuid.UUID(str(rec_id_raw))
            except (ValueError, TypeError):
                recommendation_id = None

        return {
            "content": content,
            "model_used": model_used,
            "usage": usage,
            "total_tokens": total_tokens,
            "recommendation_id": recommendation_id,
            "visited_nodes": exec_result.visited_nodes,
            "final_state": final_state,
        }
