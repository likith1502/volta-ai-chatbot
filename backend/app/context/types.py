from enum import Enum


class WorkflowStatus(str, Enum):
    """Execution status of an orchestration workflow."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    INTERRUPTED = "interrupted"


class ConversationStatus(str, Enum):
    """Lifecycle status of a user conversation session."""

    ACTIVE = "active"
    IDLE = "idle"
    PAUSED = "paused"
    ARCHIVED = "archived"
    CLOSED = "closed"


class NodeType(str, Enum):
    """Category of node in a graph-based AI workflow."""

    INPUT = "input"
    LLM = "llm"
    ROUTER = "router"
    TOOL = "tool"
    MEMORY = "memory"
    OUTPUT = "output"
    GUARDRAIL = "guardrail"
    CUSTOM = "custom"


class ExecutionMode(str, Enum):
    """Execution model for workflow orchestration."""

    SYNC = "sync"
    ASYNC = "async"
    STREAMING = "streaming"
    BATCH = "batch"
