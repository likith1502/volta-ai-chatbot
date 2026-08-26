import time
import uuid
from typing import Any, Callable, Dict, List, Tuple

from app.streaming.stream_channel import StreamChannel
from app.streaming.stream_filter import StreamFilter
from app.streaming.stream_message import StreamMessage
from app.streaming.stream_result import StreamResult
from app.streaming.stream_subscription import StreamSubscription
from app.streaming.stream_types import StreamPriority

_PRIORITY_WEIGHTS = {
    StreamPriority.CRITICAL: 4,
    StreamPriority.HIGH: 3,
    StreamPriority.NORMAL: 2,
    StreamPriority.LOW: 1,
    StreamPriority.BACKGROUND: 0,
}


class StreamDispatcher:
    """
    Message routing dispatcher for stream channels.
    Evaluates subscriptions, enforces priority ordering, and isolates subscriber failures.
    """

    def __init__(self) -> None:
        # channel_id -> list of (StreamSubscription, callback)
        self._subscribers: Dict[
            str, List[Tuple[StreamSubscription, Callable[[StreamMessage], Any]]]
        ] = {}

    def register_subscriber(
        self,
        channel_id: str,
        subscription: StreamSubscription,
        callback: Callable[[StreamMessage], Any],
    ) -> None:
        """Registers a subscriber callback to a channel with specified priority."""
        if channel_id not in self._subscribers:
            self._subscribers[channel_id] = []
        self._subscribers[channel_id].append((subscription, callback))

    def unregister_subscriber(self, subscription_id: uuid.UUID) -> None:
        """Unregisters subscriber by subscription_id across all channels."""
        for channel_id in list(self._subscribers.keys()):
            self._subscribers[channel_id] = [
                (sub, cb)
                for sub, cb in self._subscribers[channel_id]
                if sub.subscription_id != subscription_id
            ]

    async def dispatch(
        self, channel: StreamChannel, message: StreamMessage
    ) -> StreamResult:
        """
        Dispatches a StreamMessage to all active channel subscribers ordered by priority.
        Isolates failures so an exception in one callback does not break other subscribers.
        """
        start_time = time.perf_counter()
        subs = self._subscribers.get(channel.channel_id, [])

        # Filter active subscribers
        active_subs = [(sub, cb) for sub, cb in subs if sub.active]

        # Sort descending by priority weight
        active_subs.sort(
            key=lambda item: _PRIORITY_WEIGHTS.get(item[0].priority, 0),
            reverse=True,
        )

        delivered = 0
        skipped = 0
        errors: List[Dict[str, Any]] = []

        for sub, callback in active_subs:
            # Evaluate filters
            matches = True
            for flt in sub.filters:
                if isinstance(flt, StreamFilter) and not flt.matches(message):
                    matches = False
                    break

            if not matches:
                skipped += 1
                continue

            try:
                res = callback(message)
                if hasattr(res, "__await__"):
                    await res
                delivered += 1
            except Exception as exc:
                errors.append(
                    {
                        "subscription_id": str(sub.subscription_id),
                        "subscriber_id": sub.subscriber_id,
                        "error": str(exc),
                    }
                )

        duration = round(time.perf_counter() - start_time, 4)
        return StreamResult(
            success=len(errors) == 0,
            delivered=delivered,
            skipped=skipped,
            errors=errors,
            processing_time=duration,
        )
