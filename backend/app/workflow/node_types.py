from enum import Enum


class WorkflowNodeType(str, Enum):
    """Category of workflow node in the node library."""

    START = "start"
    END = "end"
    LLM = "llm"
    TOOL = "tool"
    MEMORY = "memory"
    INTENT = "intent"
    ENTITY = "entity"
    DECISION = "decision"
    RESPONSE = "response"
    SYSTEM = "system"
    CUSTOM = "custom"
