from enum import Enum


class StreamType(str, Enum):
    """Functional classification for real-time stream messages."""

    EVENT = "event"
    STATE = "state"
    EXECUTION = "execution"
    CHECKPOINT = "checkpoint"
    METRICS = "metrics"
    LOG = "log"
    SYSTEM = "system"
    HEARTBEAT = "heartbeat"
    CUSTOM = "custom"


class StreamPriority(str, Enum):
    """Priority levels for streaming message dispatching."""

    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


class StreamMode(str, Enum):
    """Modes governing message delivery and processing."""

    LIVE = "live"
    BUFFERED = "buffered"
    BATCH = "batch"
    SNAPSHOT = "snapshot"
    REPLAY = "replay"


class DeliveryGuarantee(str, Enum):
    """Delivery guarantee semantics supported by stream transports."""

    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    BEST_EFFORT = "best_effort"


class OverflowStrategy(str, Enum):
    """Strategies for handling queue overflow under backpressure."""

    DROP_OLDEST = "drop_oldest"
    DROP_NEWEST = "drop_newest"
    BLOCK = "block"
    FAIL = "fail"
