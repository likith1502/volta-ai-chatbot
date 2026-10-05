"""Consolidated Models Module for Agents Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum
from pydantic import BaseModel, Field
from typing import Any
import uuid

# --- Consolidated from permissions.py ---
class AgentPermission(str, Enum):
    """Specific permission capabilities granted to an agent."""
    CAN_DELEGATE = 'can_delegate'
    CAN_APPROVE = 'can_approve'
    CAN_EXECUTE_TOOLS = 'can_execute_tools'
    CAN_ACCESS_MEMORY = 'can_access_memory'
    CAN_RENDER_PROMPTS = 'can_render_prompts'
    CAN_CREATE_TASKS = 'can_create_tasks'
    CAN_SUPERVISE = 'can_supervise'

class AgentPermissionSet(BaseModel):
    """Set of permissions governing agent actions."""
    permissions: set[AgentPermission] = Field(default_factory=lambda: {AgentPermission.CAN_ACCESS_MEMORY, AgentPermission.CAN_RENDER_PROMPTS})

    def has_permission(self, permission: AgentPermission) -> bool:
        return permission in self.permissions

    def grant(self, permission: AgentPermission) -> None:
        self.permissions.add(permission)

    def revoke(self, permission: AgentPermission) -> None:
        self.permissions.discard(permission)

# --- Consolidated from role.py ---
class AgentRole(str, Enum):
    """Supported agent roles within the multi-agent orchestration runtime."""
    SUPPORT = 'support'
    SUPERVISOR = 'supervisor'
    PLANNER = 'planner'
    RESEARCH = 'research'
    TOOL = 'tool'
    MEMORY = 'memory'
    REVIEWER = 'reviewer'
    CRITIC = 'critic'
    EXECUTOR = 'executor'
    CUSTOM = 'custom'

# --- Consolidated from status.py ---
class AgentStatus(str, Enum):
    """Operational status of an agent instance."""
    IDLE = 'idle'
    BUSY = 'busy'
    WAITING = 'waiting'
    DELEGATING = 'delegating'
    PAUSED = 'paused'
    ERROR = 'error'
    TERMINATED = 'terminated'

# --- Consolidated from identity.py ---
class AgentIdentity(BaseModel):
    """Identity attributes for an agent."""
    agent_id: str = Field(default_factory=lambda: f'agent_{uuid.uuid4().hex[:8]}')
    name: str = Field(..., min_length=1)
    version: str = Field(default='1.0.0')
    description: str = Field(default='Autonomous Enterprise Worker Agent')
    owner: str = Field(default='system')

# --- Consolidated from budget.py ---
class AgentExecutionBudget(BaseModel):
    """Resource budget and safety limits for agent execution turns."""
    max_runtime_ms: float = Field(default=30000.0, ge=100.0)
    max_retries: int = Field(default=3, ge=0)
    max_tool_calls: int = Field(default=10, ge=0)
    max_delegation_depth: int = Field(default=3, ge=0)
    max_tokens: int = Field(default=4096, ge=1)
    max_cost_usd: float = Field(default=1.0, ge=0.0)
    max_memory_items: int = Field(default=20, ge=1)
    current_runtime_ms: float = Field(default=0.0, ge=0.0)
    current_retries: int = Field(default=0, ge=0)
    current_tool_calls: int = Field(default=0, ge=0)
    current_delegation_depth: int = Field(default=0, ge=0)

    def is_exhausted(self) -> bool:
        """Returns True if any budget limit is exceeded."""
        if self.current_runtime_ms >= self.max_runtime_ms:
            return True
        if self.current_retries >= self.max_retries:
            return True
        if self.current_tool_calls >= self.max_tool_calls:
            return True
        if self.current_delegation_depth > self.max_delegation_depth:
            return True
        return False

# --- Consolidated from capabilities.py ---
class AgentCapabilities(BaseModel):
    """Capabilities supported by an agent."""
    supports_planning: bool = True
    supports_delegation: bool = True
    supports_tool_execution: bool = True
    supports_memory_access: bool = True
    supports_streaming: bool = True
    supports_hitl: bool = True
    supported_tools: list[str] = Field(default_factory=lambda: ['echo', 'calculator', 'datetime', 'uuid'])

# --- Consolidated from config.py ---
class AgentRuntimeConfig(BaseModel):
    """Global configuration settings for Enterprise Multi-Agent Orchestration Runtime."""
    max_agents: int = Field(default=100, ge=1)
    default_provider: str = 'mock'
    default_model: str = 'mock-model-v1'
    event_emission_enabled: bool = True

# --- Consolidated from context.py ---
class AgentContext(BaseModel):
    """Runtime context passed during agent execution turns."""
    conversation_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    session_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    inputs: dict[str, Any] = Field(default_factory=dict)
    memory_snapshot: list[dict[str, Any]] = Field(default_factory=list)
    variables: dict[str, Any] = Field(default_factory=dict)

# --- Consolidated from metadata.py ---
class AgentMetadata(BaseModel):
    """Metadata tags and operational labels for an agent."""
    tags: list[str] = Field(default_factory=lambda: ['enterprise', 'v7.5'])
    domain: str = 'urban_mobility'
    author: str = 'Volta Engineering'
    version: str = '7.5.0'

# --- Consolidated from persona.py ---
class AgentPersona(BaseModel):
    """Behavioral traits and style instructions defining agent persona."""
    communication_style: str = Field(default='professional', description='e.g. professional, concise, empathetic')
    expertise: list[str] = Field(default_factory=lambda: ['urban_mobility', 'customer_service'])
    tone: str = Field(default='helpful and authoritative')
    constraints: list[str] = Field(default_factory=lambda: ['Never share confidential API keys', 'Strictly factual'])
    reasoning_style: str = Field(default='analytical', description='e.g. analytical, step-by-step, creative')
    language: str = Field(default='en')
    response_style: str = Field(default='markdown_structured')

# --- Consolidated from policy.py ---
class AgentPolicy(BaseModel):
    """Aggregate policy binding execution budget and permission sets."""
    budget: AgentExecutionBudget = Field(default_factory=AgentExecutionBudget)
    permissions: AgentPermissionSet = Field(default_factory=AgentPermissionSet)
    require_human_approval: bool = False
    allow_parallel_tasks: bool = True

# --- Consolidated from profile.py ---
class AgentProfile(BaseModel):
    """Prompt and LLM generation profile linking to Prompt Execution Engine (v7.1)."""
    prompt_template_id: str = 'agent_system_v1'
    system_instruction_override: str = 'You are an autonomous AI worker agent operating within the Volta platform.'
    provider: str = 'mock'
    model: str = 'mock-model-v1'
    temperature: float = 0.7
    max_tokens: int = 2048

# --- Consolidated from versioning.py ---
class AgentVersion(BaseModel):
    version: str = '7.5.0'
    milestone: str = 'Phase 7.5 Enterprise Multi-Agent Orchestration Runtime'
    frozen_dependencies: list[str] = Field(default_factory=lambda: ['app.runtime (v7.0)', 'app.prompt (v7.1)', 'app.memory (v7.2)', 'app.tools (v7.3)', 'app.graph_runtime (v7.4)'])

# --- Consolidated from manifest.py ---
class AgentManifest(BaseModel):
    """Manifest describing complete specifications of an agent."""
    identity: AgentIdentity
    role: AgentRole = AgentRole.SUPPORT
    persona: AgentPersona = Field(default_factory=AgentPersona)
    capabilities: AgentCapabilities = Field(default_factory=AgentCapabilities)
    policy: AgentPolicy = Field(default_factory=AgentPolicy)

