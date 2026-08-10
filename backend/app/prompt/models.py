"""Consolidated Models Module for Prompt Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABC, abstractmethod
from app.prompt.contracts import PromptRequest
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Any
from typing import Any, Optional
import uuid

# --- Consolidated from metadata.py ---
class PromptTemplateMetadata(BaseModel):
    """Authoring concerns metadata container for prompt templates."""
    template_id: str
    version: str = '1.0.0'
    schema_version: str = 'v1'
    author: str = 'system'
    tags: list[str] = Field(default_factory=list)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PromptExecutionMetadata(BaseModel):
    """Runtime execution telemetry metadata container."""
    client_ip: Optional[str] = None
    environment: str = 'development'
    user_id: Optional[str] = None
    custom_headers: dict[str, Any] = Field(default_factory=dict)

# --- Consolidated from capabilities.py ---
class PromptCapabilities(BaseModel):
    """Capability reporting flags for prompt templates and prompt execution engine."""
    supports_variables: bool = True
    supports_templates: bool = True
    supports_system_prompt: bool = True
    supports_tools: bool = True
    supports_rag: bool = True
    supports_multimodal: bool = False
    supports_images: bool = False
    supports_json_output: bool = True

# --- Consolidated from context.py ---
class PromptContext(BaseModel):
    """Immutable execution context container tracking prompt rendering lineage."""
    prompt_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    template_id: str
    revision_id: str = 'v1'
    conversation_id: Optional[uuid.UUID] = None
    execution_id: Optional[uuid.UUID] = None
    runtime_id: Optional[uuid.UUID] = None
    workflow_id: Optional[str] = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)

# --- Consolidated from versioning.py ---
class TemplateRevision(BaseModel):
    """Immutable template revision record representing a specific version snapshot (e.g. 'v1', 'v2')."""
    revision_id: str = Field(default='v1', description="'v1', 'v2', 'v3'")
    template_id: str
    content_template: str
    system_instruction: str = ''
    author: str = 'system'
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    change_summary: str = 'Initial revision'

class PromptVersion(BaseModel):
    """Version tracking model for prompt schema and runtime releases."""
    prompt_version: str = '7.1.0'
    schema_version: str = 'v1'
    template_version: str = '1.0.0'

# --- Consolidated from variable_provider.py ---
class VariableProvider(ABC):
    """Abstract Base Class for dynamic variable resolution (enables seamless injection from Phase 7.2 Memory Runtime, Phase 7.3 Tool Runtime, or external DB)."""

    @abstractmethod
    async def resolve_variables(self, request: PromptRequest) -> dict[str, Any]:
        """Resolves dynamic variable key-value pairs for given PromptRequest."""
        pass

class DefaultVariableProvider(VariableProvider):
    """Default variable provider returning variables directly from PromptRequest payload."""

    async def resolve_variables(self, request: PromptRequest) -> dict[str, Any]:
        return request.variables.copy()

