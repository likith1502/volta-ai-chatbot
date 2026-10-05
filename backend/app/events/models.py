"""Consolidated Models Module for Events Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field

# --- Consolidated from event_types.py ---
class WorkflowEventCategory(str, Enum):
    """Broad functional categories for workflow events."""
    EXECUTION = 'execution'
    NODE = 'node'
    GRAPH = 'graph'
    STATE = 'state'
    CHECKPOINT = 'checkpoint'
    SYSTEM = 'system'
    SECURITY = 'security'
    CUSTOM = 'custom'

class EventPriority(str, Enum):
    """Priority levels for event dispatching and processing."""
    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'
    CRITICAL = 'critical'

class WorkflowEventType(str, Enum):
    """Specific event type identifiers generated throughout workflow lifecycle."""
    EXECUTION_STARTED = 'execution_started'
    EXECUTION_COMPLETED = 'execution_completed'
    EXECUTION_FAILED = 'execution_failed'
    NODE_STARTED = 'node_started'
    NODE_COMPLETED = 'node_completed'
    NODE_FAILED = 'node_failed'
    EDGE_EVALUATED = 'edge_evaluated'
    BRANCH_SELECTED = 'branch_selected'
    STATE_UPDATED = 'state_updated'
    SNAPSHOT_CREATED = 'snapshot_created'
    CHECKPOINT_REQUESTED = 'checkpoint_requested'
    WARNING_RAISED = 'warning_raised'
    ERROR_RAISED = 'error_raised'
    CUSTOM = 'custom'

# --- Consolidated from event_status.py ---
class WorkflowEventStatus(str, Enum):
    """Lifecycle states of a workflow event during routing and processing."""
    CREATED = 'created'
    QUEUED = 'queued'
    DISPATCHED = 'dispatched'
    PROCESSED = 'processed'
    FAILED = 'failed'
    IGNORED = 'ignored'

# --- Consolidated from event_metadata.py ---
class WorkflowEventMetadata(BaseModel):
    """Metadata describing a workflow event origin and specifications."""
    version: str = '1.0.0'
    schema_version: str = '1.0'
    source: str = 'workflow_engine'
    producer: str = 'system'
    priority: EventPriority = EventPriority.NORMAL
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

