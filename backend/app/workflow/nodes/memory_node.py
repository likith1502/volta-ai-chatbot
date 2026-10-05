from typing import Any, Optional

from app.context.state import ConversationState
from app.context.types import NodeType
from app.workflow.base import BaseWorkflowNode
from app.workflow.metadata import NodeExecutionContext
from app.workflow.node_types import WorkflowNodeType


class MemoryNode(BaseWorkflowNode):
    """
    Workflow Node managing contextual memory synchronization.
    Maintains short-term and long-term memory state across workflow execution.
    """

    node_name: str = "MemoryNode"
    node_type: NodeType = NodeType.MEMORY
    node_category: WorkflowNodeType = WorkflowNodeType.MEMORY
    node_description: str = "Contextual memory workflow node."

    memory_strategy: Optional[Any] = None

    async def execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """Asynchronously synchronizes memory state across workflow steps."""
        if not state.conversation.current_message and not state.memory.short_term_memory:
            return state

        memories = state.memory.short_term_memory.get("memories", [])
        memory_payload = {
            "status": "synchronized",
            "memory_count": len(memories),
            "keys": [m.get("memory_key") for m in memories if isinstance(m, dict)],
        }

        new_node_results = dict(state.execution.node_results)
        new_node_results[self.node_id] = memory_payload

        return state.with_update(
            workflow_step=self.node_id,
            node_results=new_node_results,
        )
