"""Consolidated Telemetry Module for Prompt Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABC, abstractmethod
from app.prompt.contracts import PromptRequest, PromptResponse
from app.prompt.templates.base_template import BasePromptTemplate
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Any
import json

if TYPE_CHECKING:
    from app.prompt.result import PromptResult


# --- Consolidated from analytics.py ---
class PromptAnalyticsReport(BaseModel):
    """Analytics and usage telemetry report across all prompt executions."""
    total_executions: int = Field(default=0, ge=0)
    total_renders: int = Field(default=0, ge=0)
    average_render_time_ms: float = Field(default=0.0, ge=0.0)
    failure_rate_pct: float = Field(default=0.0, ge=0.0)
    top_templates: list[str] = Field(default_factory=list)
    average_token_estimate: float = Field(default=0.0, ge=0.0)
    average_compression_ratio: float = Field(default=1.0, ge=0.0)

class PromptAnalyticsManager:
    """Aggregates execution analytics telemetry for dashboard inspection."""

    def __init__(self) -> None:
        self.render_count = 0
        self.exec_count = 0
        self.total_render_ms = 0.0
        self.failures = 0
        self.template_counts: dict[str, int] = {}

    def record_render(self, template_id: str, duration_ms: float, is_success: bool=True) -> None:
        self.render_count += 1
        self.total_render_ms += duration_ms
        self.template_counts[template_id] = self.template_counts.get(template_id, 0) + 1
        if not is_success:
            self.failures += 1

    def record_execution(self, template_id: str) -> None:
        self.exec_count += 1

    def get_report(self) -> PromptAnalyticsReport:
        avg_render = self.total_render_ms / self.render_count if self.render_count > 0 else 0.0
        fail_pct = self.failures / self.render_count * 100.0 if self.render_count > 0 else 0.0
        top = sorted(self.template_counts.keys(), key=lambda k: self.template_counts[k], reverse=True)[:5]
        return PromptAnalyticsReport(total_executions=self.exec_count, total_renders=self.render_count, average_render_time_ms=avg_render, failure_rate_pct=fail_pct, top_templates=top)

# --- Consolidated from metrics.py ---
class PromptMetrics(BaseModel):
    """Execution telemetry and quality metrics container."""
    render_time_ms: float = Field(default=0.0, ge=0.0)
    validation_time_ms: float = Field(default=0.0, ge=0.0)
    optimization_time_ms: float = Field(default=0.0, ge=0.0)
    execution_time_ms: float = Field(default=0.0, ge=0.0)
    template_size_chars: int = Field(default=0, ge=0)
    rendered_size_chars: int = Field(default=0, ge=0)
    token_estimate: int = Field(default=0, ge=0)
    compression_ratio: float = Field(default=1.0, ge=0.0, description='Rendered size / Optimized size ratio')
    variable_coverage_pct: float = Field(default=100.0, ge=0.0, le=100.0)
    optimization_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    estimated_complexity: str = Field(default='low', description="'low', 'medium', 'high'")
    validation_score: float = Field(default=1.0, ge=0.0, le=1.0)

# --- Consolidated from serializer.py ---
class PromptSerializer:
    """Import and export helpers formatting templates and rendered prompts as JSON, Markdown, or YAML."""

    @staticmethod
    def template_to_json(template: BasePromptTemplate) -> str:
        data = {'template_id': template.template_id, 'template_type': template.template_type, 'system_instruction': template.system_instruction, 'messages': [m.model_dump() for m in template.messages], 'variables': [v.model_dump() for v in template.variables], 'parent_template_id': template.parent_template_id, 'metadata': template.metadata.model_dump()}
        return json.dumps(data, indent=2, default=str)

    @staticmethod
    def result_to_markdown(result: PromptResult) -> str:
        lines = [f'# Prompt Execution Result — {result.context.prompt_id}', f'- **Template ID**: `{result.context.template_id}` | **Revision**: `{result.context.revision_id}`', f'- **Execution Status**: `{result.execution_status}`', f'- **Render Latency**: `{result.metrics.render_time_ms:.2f}ms` | **Token Estimate**: `{result.metrics.token_estimate}`', '', '## Rendered Messages']
        if result.rendered_prompt:
            if result.rendered_prompt.system_prompt:
                lines.append('### SYSTEM')
                lines.append(result.rendered_prompt.system_prompt)
                lines.append('')
            for msg in result.rendered_prompt.messages:
                lines.append(f'### {msg.role.upper()}')
                lines.append(msg.content)
                lines.append('')
        if result.runtime_result and result.runtime_result.response:
            lines.append('## LLM Generation Response')
            lines.append(result.runtime_result.response.content)
        return '\n'.join(lines)

# --- Consolidated from hooks.py ---
class PreRenderHook(ABC):
    """Hook contract executed before template rendering."""

    @abstractmethod
    async def pre_render(self, request: PromptRequest) -> None:
        pass

class PostRenderHook(ABC):
    """Hook contract executed after template rendering and optimization."""

    @abstractmethod
    async def post_render(self, response: PromptResponse) -> None:
        pass

class PreExecutionHook(ABC):
    """Hook contract executed before passing prompt to RuntimeManager."""

    @abstractmethod
    async def pre_execution(self, result: PromptResult) -> None:
        pass

class PostExecutionHook(ABC):
    """Hook contract executed after RuntimeManager completes LLM generation."""

    @abstractmethod
    async def post_execution(self, result: PromptResult) -> None:
        pass

# --- Consolidated from trace.py ---
class PromptTraceStep(BaseModel):
    """Execution trace step recording pipeline stage timing and status."""
    stage_name: str = Field(..., description="'validation', 'security', 'injection', 'rendering', 'optimization', 'compilation'")
    status: str = Field(default='COMPLETED', description="'COMPLETED', 'SKIPPED', 'FAILED'")
    duration_ms: float = Field(default=0.0, ge=0.0)
    details: str = ''
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PromptTrace(BaseModel):
    """Complete execution trace recording per-stage pipeline performance."""
    steps: list[PromptTraceStep] = Field(default_factory=list)
    total_duration_ms: float = Field(default=0.0, ge=0.0)

    def add_step(self, stage_name: str, duration_ms: float, status: str='COMPLETED', details: str='') -> None:
        self.steps.append(PromptTraceStep(stage_name=stage_name, duration_ms=duration_ms, status=status, details=details))
        self.total_duration_ms += duration_ms

