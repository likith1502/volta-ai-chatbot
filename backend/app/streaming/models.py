"""Consolidated Models Module for Streaming Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel
from pydantic import BaseModel, Field
from typing import Any
from typing import Any, Optional
import uuid

# --- Consolidated from stream_types.py ---
class StreamType(str, Enum):
    """Functional classification for real-time stream messages."""
    EVENT = 'event'
    STATE = 'state'
    EXECUTION = 'execution'
    CHECKPOINT = 'checkpoint'
    METRICS = 'metrics'
    LOG = 'log'
    SYSTEM = 'system'
    HEARTBEAT = 'heartbeat'
    CUSTOM = 'custom'

class StreamPriority(str, Enum):
    """Priority levels for streaming message dispatching."""
    CRITICAL = 'critical'
    HIGH = 'high'
    NORMAL = 'normal'
    LOW = 'low'
    BACKGROUND = 'background'

class StreamMode(str, Enum):
    """Modes governing message delivery and processing."""
    LIVE = 'live'
    BUFFERED = 'buffered'
    BATCH = 'batch'
    SNAPSHOT = 'snapshot'
    REPLAY = 'replay'

class DeliveryGuarantee(str, Enum):
    """Delivery guarantee semantics supported by stream transports."""
    AT_MOST_ONCE = 'at_most_once'
    AT_LEAST_ONCE = 'at_least_once'
    BEST_EFFORT = 'best_effort'

class OverflowStrategy(str, Enum):
    """Strategies for handling queue overflow under backpressure."""
    DROP_OLDEST = 'drop_oldest'
    DROP_NEWEST = 'drop_newest'
    BLOCK = 'block'
    FAIL = 'fail'

# --- Consolidated from stream_status.py ---
class StreamStatus(str, Enum):
    """Lifecycle states of a stream or streaming channel."""
    CREATED = 'created'
    ACTIVE = 'active'
    PAUSED = 'paused'
    CLOSED = 'closed'
    FAILED = 'failed'

# --- Consolidated from stream_metadata.py ---
class StreamMetadata(BaseModel):
    """Metadata attached to a stream message or channel."""
    version: str = '1.0.0'
    schema_version: str = '1.0'
    producer: str = 'system'
    source: str = 'workflow_engine'
    priority: StreamPriority = StreamPriority.NORMAL
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- Consolidated from backpressure.py ---
class BackpressurePolicy(BaseModel):
    """Configuration governing queue limits and overflow strategies under high load."""
    max_queue_size: int = 1000
    overflow_strategy: OverflowStrategy = OverflowStrategy.DROP_OLDEST
    drop_policy: str = 'oldest'
    timeout: float = 5.0

# --- Consolidated from stream_context.py ---
class StreamContext(BaseModel):
    """Runtime context tracking session configuration and mode for real-time streaming."""
    stream_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    execution_id: Optional[uuid.UUID] = None
    workflow_id: Optional[str] = None
    correlation_id: Optional[uuid.UUID] = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    replay_mode: StreamMode = StreamMode.LIVE
    metadata: dict[str, Any] = Field(default_factory=dict)

# --- Consolidated from stream_result.py ---
class StreamResult(BaseModel):
    """Outcome container summarizing stream message dispatch and processing results."""
    success: bool = True
    delivered: int = 0
    skipped: int = 0
    warnings: list[str] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)
    processing_time: float = 0.0

# --- Consolidated from stream_subscription.py ---
class StreamSubscription(BaseModel):
    """Binding model representing a subscriber's registered interest in a stream."""
    subscription_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    subscriber_id: str
    filters: list[Any] = Field(default_factory=list)
    priority: StreamPriority = StreamPriority.NORMAL
    active: bool = True

# --- Consolidated from stream_validation.py ---
class StreamValidationResult(BaseModel):
    """Validation outcome container summarizing diagnostic results for stream payloads."""
    is_valid: bool = True
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    compatible: bool = True
    schema_version: str = '1.0'

