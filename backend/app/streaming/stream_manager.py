import time
import uuid
from typing import Any, Callable, Dict, List, Optional

from app.streaming.exceptions import StreamChannelException
from app.streaming.stream_channel import StreamChannel
from app.streaming.stream_dispatcher import StreamDispatcher
from app.streaming.stream_history import StreamHistory
from app.streaming.stream_message import StreamMessage
from app.streaming.stream_metrics import StreamMetrics
from app.streaming.stream_registry import StreamRegistry
from app.streaming.stream_result import StreamResult
from app.streaming.stream_status import StreamStatus
from app.streaming.stream_subscription import StreamSubscription
from app.streaming.stream_types import StreamPriority


class StreamManager:
    """
    Central Manager for streaming channel creation, message publication,
    subscriber registration, and streaming lifecycle management.
    """

    def __init__(
        self,
        dispatcher: Optional[StreamDispatcher] = None,
        registry: Optional[StreamRegistry] = None,
    ) -> None:
        self.dispatcher = dispatcher or StreamDispatcher()
        self.registry = registry or StreamRegistry()
        self.channels: Dict[str, StreamChannel] = {}
        self.statuses: Dict[str, StreamStatus] = {}
        self.metrics = StreamMetrics()
        self.history = StreamHistory()

    def open_stream(self, channel_id: str, name: str, description: str = "") -> StreamChannel:
        """Creates and opens a new StreamChannel."""
        if channel_id in self.channels:
            raise StreamChannelException(f"StreamChannel '{channel_id}' is already open.")
        ch = StreamChannel(channel_id=channel_id, name=name, description=description)
        self.channels[channel_id] = ch
        self.statuses[channel_id] = StreamStatus.ACTIVE
        return ch

    def close_stream(self, channel_id: str) -> None:
        """Closes a StreamChannel."""
        if channel_id not in self.channels:
            raise StreamChannelException(f"StreamChannel '{channel_id}' not found.")
        self.statuses[channel_id] = StreamStatus.CLOSED

    def pause(self, channel_id: str) -> None:
        """Pauses a StreamChannel."""
        if channel_id not in self.channels:
            raise StreamChannelException(f"StreamChannel '{channel_id}' not found.")
        self.statuses[channel_id] = StreamStatus.PAUSED

    def resume(self, channel_id: str) -> None:
        """Resumes a paused StreamChannel."""
        if channel_id not in self.channels:
            raise StreamChannelException(f"StreamChannel '{channel_id}' not found.")
        self.statuses[channel_id] = StreamStatus.ACTIVE

    def subscribe(
        self,
        channel_id: str,
        subscriber_id: str,
        callback: Callable[[StreamMessage], Any],
        priority: StreamPriority = StreamPriority.NORMAL,
        filters: Optional[List[Any]] = None,
    ) -> StreamSubscription:
        """Subscribes a callback function to a channel."""
        if channel_id not in self.channels:
            self.open_stream(channel_id=channel_id, name=channel_id)

        sub = StreamSubscription(
            subscriber_id=subscriber_id,
            priority=priority,
            filters=filters or [],
        )
        self.channels[channel_id].subscribers.append(subscriber_id)
        self.dispatcher.register_subscriber(channel_id, sub, callback)
        self.metrics.subscribers = sum(len(ch.subscribers) for ch in self.channels.values())
        return sub

    def unsubscribe(self, subscription_id: uuid.UUID) -> None:
        """Unsubscribes a subscriber by subscription_id."""
        self.dispatcher.unregister_subscriber(subscription_id)

    async def publish(self, channel_id: str, message: StreamMessage) -> StreamResult:
        """Publishes a StreamMessage to the specified channel."""
        start_time = time.perf_counter()
        if channel_id not in self.channels:
            raise StreamChannelException(f"StreamChannel '{channel_id}' not found.")

        if self.statuses.get(channel_id) != StreamStatus.ACTIVE:
            self.metrics.record_dropped()
            return StreamResult(success=False, delivered=0, skipped=1, warnings=[f"Channel '{channel_id}' is not ACTIVE."])

        ch = self.channels[channel_id]
        res = await self.dispatcher.dispatch(ch, message)

        duration = round(time.perf_counter() - start_time, 4)
        self.metrics.record_sent(latency=duration)
        if not res.success:
            self.metrics.record_error()

        self.history.record_delivery(
            message_id=message.message_id,
            channel=channel_id,
            adapter="in_memory",
            delivery_result="success" if res.success else "error",
        )
        return res

    async def publish_batch(self, channel_id: str, messages: List[StreamMessage]) -> StreamResult:
        """Publishes a batch of StreamMessages to the specified channel."""
        total_delivered = 0
        total_skipped = 0
        all_errors = []

        start_time = time.perf_counter()
        for msg in messages:
            res = await self.publish(channel_id, msg)
            total_delivered += res.delivered
            total_skipped += res.skipped
            all_errors.extend(res.errors)

        duration = round(time.perf_counter() - start_time, 4)
        return StreamResult(
            success=len(all_errors) == 0,
            delivered=total_delivered,
            skipped=total_skipped,
            errors=all_errors,
            processing_time=duration,
        )
