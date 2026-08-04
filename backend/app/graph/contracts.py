import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Optional, Union

from pydantic import BaseModel, Field

from app.context.state import ConversationState
from app.context.types import ExecutionMode, WorkflowStatus


class GraphMetadata(BaseModel):
    """Standardized metadata schema for Graph instances."""

    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tags: list[str] = Field(default_factory=list)
    execution_mode: ExecutionMode = ExecutionMode.SYNC


class GraphBuildOptions(BaseModel):
    """Configuration options for graph compilation and validation."""

    allow_cycles: bool = True
    strict_validation: bool = True
    sort_edges: bool = True
    compile_indexes: bool = True


class GraphValidationResult(BaseModel):
    """Container for graph validation diagnostics and statistics."""

    is_valid: bool = True
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    statistics: dict[str, Any] = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    """Contract model for graph execution results."""

    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    status: WorkflowStatus = WorkflowStatus.COMPLETED
    final_state: Optional[ConversationState] = None
    duration_ms: float = 0.0
    visited_nodes: list[str] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class IGraphNode(ABC):
    """Abstract interface for graph node components."""

    node_id: str
    node_name: str
    node_type: str
    description: str
    metadata: dict[str, Any]

    @abstractmethod
    async def execute(self, state: ConversationState) -> ConversationState:
        """Asynchronously executes node logic on state and returns updated ConversationState."""
        pass


class IGraphEdge(ABC):
    """Abstract interface for directed graph edges between nodes."""

    source_node: str
    target_node: str
    edge_condition: Optional[Union[Callable[[ConversationState], bool], Callable[[ConversationState], Awaitable[bool]], str]]
    priority: int
    metadata: dict[str, Any]

    @abstractmethod
    async def evaluate(self, state: ConversationState) -> bool:
        """Evaluates whether the edge condition is satisfied for the given state."""
        pass


class IGraph(ABC):
    """Abstract interface for immutable compiled graph representation."""

    @property
    @abstractmethod
    def nodes(self) -> dict[str, IGraphNode]:
        """Dictionary of all registered nodes mapped by node_id."""
        pass

    @property
    @abstractmethod
    def edges(self) -> list[IGraphEdge]:
        """List of all registered edges in the graph."""
        pass

    @property
    @abstractmethod
    def entry_node(self) -> Optional[str]:
        """Designated entrypoint node ID."""
        pass

    @property
    @abstractmethod
    def metadata(self) -> GraphMetadata:
        """Standardized graph metadata."""
        pass

    @abstractmethod
    def get_node(self, node_id: str) -> IGraphNode:
        """Retrieves node by ID or raises NodeNotFoundException."""
        pass

    @abstractmethod
    def get_outgoing_edges(self, node_id: str) -> list[IGraphEdge]:
        """Retrieves all directed outgoing edges originating from specified node ID."""
        pass

    @abstractmethod
    def validate(self) -> GraphValidationResult:
        """Validates graph structural integrity and returns validation result."""
        pass


class IGraphBuilder(ABC):
    """Abstract contract for assembling and compiling a Graph."""

    @abstractmethod
    def add_node(self, node: IGraphNode) -> "IGraphBuilder":
        """Registers a node into the graph builder."""
        pass

    @abstractmethod
    def add_edge(self, edge: IGraphEdge) -> "IGraphBuilder":
        """Registers a directed edge into the graph builder."""
        pass

    @abstractmethod
    def set_entry_node(self, node_id: str) -> "IGraphBuilder":
        """Specifies entrypoint node ID for graph execution."""
        pass

    @abstractmethod
    def validate(self, options: Optional[GraphBuildOptions] = None) -> GraphValidationResult:
        """Validates graph structural rules and connectivity."""
        pass

    @abstractmethod
    def build(self, options: Optional[GraphBuildOptions] = None) -> IGraph:
        """Compiles and returns an immutable Graph instance."""
        pass


class IGraphExecutor(ABC):
    """Abstract contract for executing graph workflows."""

    @abstractmethod
    async def execute(self, graph: IGraph, initial_state: ConversationState) -> ExecutionResult:
        """Executes the graph starting from entry node to completion."""
        pass


class IGraphRegistry(ABC):
    """Abstract contract for managing reusable graph templates."""

    @abstractmethod
    def register(
        self,
        name: str,
        builder_or_factory: Union[IGraphBuilder, Callable[[], IGraphBuilder]],
        overwrite: bool = False,
    ) -> None:
        """Registers a graph builder or factory function under a template name."""
        pass

    @abstractmethod
    def get(self, name: str) -> IGraph:
        """Retrieves and compiles a registered graph template by name."""
        pass

    @abstractmethod
    def list_graphs(self) -> list[str]:
        """Lists names of all registered graph templates."""
        pass

    @abstractmethod
    def unregister(self, name: str) -> None:
        """Unregisters a graph template by name."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clears all registered graph templates."""
        pass


class IGraphFactory(ABC):
    """Abstract contract for creating customized graph instances."""

    @abstractmethod
    def create_graph(self, **kwargs: Any) -> IGraph:
        """Creates and returns a new configured Graph instance."""
        pass
