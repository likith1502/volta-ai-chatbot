from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import Field

from app.context.state import ConversationState
from app.graph.node import BaseNode
from app.workflow.metadata import (
    NodeCapability,
    NodeExecutionContext,
    NodeExecutionConstraints,
    WorkflowNodeConfig,
    WorkflowNodeMetadata,
)
from app.workflow.node_types import WorkflowNodeType


class BaseWorkflowNode(BaseNode, ABC):
    """
    Abstract Base Class for all reusable workflow nodes in the node library.
    Inherits from BaseNode to maintain 100% compatibility with Graph Orchestration Foundation.
    
    Architectural Rules:
    1. Nodes are completely stateless. Runtime state belongs in ConversationState.
    2. Nodes produce no direct, irreversible external side-effects (DB writes, payments, emails).
    3. Nodes must be fully async compatible.
    """

    node_description: str = ""
    node_category: WorkflowNodeType = WorkflowNodeType.CUSTOM
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    node_metadata: WorkflowNodeMetadata = Field(default_factory=WorkflowNodeMetadata)
    config: WorkflowNodeConfig = Field(default_factory=WorkflowNodeConfig)
    capabilities: NodeCapability = Field(default_factory=NodeCapability)
    constraints: NodeExecutionConstraints = Field(default_factory=NodeExecutionConstraints)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        if not self.description and self.node_description:
            self.description = self.node_description
        if self.node_metadata and self.node_metadata.category != self.node_category:
            self.node_metadata.category = self.node_category

    def validate_input(self, state: ConversationState) -> bool:
        """Validates that input state satisfies input schema requirements."""
        if state is None:
            return False
        return True

    def validate_output(self, state: ConversationState) -> bool:
        """Validates that output state satisfies output schema requirements."""
        if state is None:
            return False
        return True

    async def before_execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """Lifecycle hook executed prior to execute(). Default implementation is a pass-through."""
        self.validate_input(state)
        return state

    @abstractmethod
    async def execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """
        Asynchronously executes node operations on state and returns updated ConversationState.
        Must be implemented by concrete node subclasses.
        """
        pass

    async def after_execute(
        self, state: ConversationState, context: Optional[NodeExecutionContext] = None
    ) -> ConversationState:
        """Lifecycle hook executed following execute(). Default implementation is a pass-through."""
        self.validate_output(state)
        return state

    async def on_error(
        self,
        state: ConversationState,
        error: Exception,
        context: Optional[NodeExecutionContext] = None,
    ) -> ConversationState:
        """Lifecycle error hook called when execution fails. Default implementation returns state."""
        return state
