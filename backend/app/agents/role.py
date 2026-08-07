from enum import Enum


class AgentRole(str, Enum):
    """Supported agent roles within the multi-agent orchestration runtime."""

    SUPPORT = "support"
    SUPERVISOR = "supervisor"
    PLANNER = "planner"
    RESEARCH = "research"
    TOOL = "tool"
    MEMORY = "memory"
    REVIEWER = "reviewer"
    CRITIC = "critic"
    EXECUTOR = "executor"
    CUSTOM = "custom"
