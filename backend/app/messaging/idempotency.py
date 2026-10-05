import asyncio
import time
from enum import Enum
from typing import Optional

from app.messaging.models import ChannelType


class IdempotencyState(str, Enum):
    """Lifecycle states of message deduplication."""

    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class IdempotencyStore:
    """Thread-safe, stateful idempotency store preventing concurrent duplicate processing."""

    def __init__(
        self,
        ttl_seconds: int = 3600,
        in_flight_timeout: float = 120.0,
        max_size: int = 10000,
    ) -> None:
        self.ttl_seconds = ttl_seconds
        self.in_flight_timeout = in_flight_timeout
        self.max_size = max_size
        # maps key -> (state, expiration_timestamp)
        self._cache: dict[str, tuple[IdempotencyState, float]] = {}
        self._lock = asyncio.Lock()

    def _make_key(self, channel: ChannelType, external_message_id: str) -> str:
        return f"{channel.value}:{external_message_id.strip()}"

    def _purge_expired(self, now: float) -> None:
        expired_keys = [k for k, (_, exp) in self._cache.items() if exp <= now]
        for k in expired_keys:
            self._cache.pop(k, None)

        if len(self._cache) > self.max_size:
            sorted_keys = sorted(self._cache.items(), key=lambda x: x[1][1])
            excess = len(self._cache) - self.max_size
            for k, _ in sorted_keys[:excess]:
                self._cache.pop(k, None)

    async def try_acquire(
        self,
        channel: ChannelType,
        external_message_id: str,
    ) -> bool:
        """Atomically transitions NEW -> PROCESSING.

        Returns False if message is already PROCESSING or COMPLETED.
        """
        key = self._make_key(channel, external_message_id)
        now = time.monotonic()
        async with self._lock:
            self._purge_expired(now)
            entry = self._cache.get(key)
            if entry is not None:
                state, exp = entry
                if exp > now and state in (
                    IdempotencyState.PROCESSING,
                    IdempotencyState.COMPLETED,
                ):
                    return False

            # Acquire lock: transition to PROCESSING
            self._cache[key] = (
                IdempotencyState.PROCESSING,
                now + self.in_flight_timeout,
            )
            return True

    async def mark_completed(
        self,
        channel: ChannelType,
        external_message_id: str,
    ) -> None:
        """Transitions PROCESSING -> COMPLETED with standard TTL window."""
        key = self._make_key(channel, external_message_id)
        now = time.monotonic()
        async with self._lock:
            self._purge_expired(now)
            self._cache[key] = (
                IdempotencyState.COMPLETED,
                now + self.ttl_seconds,
            )

    async def mark_failed(
        self,
        channel: ChannelType,
        external_message_id: str,
    ) -> None:
        """Transitions PROCESSING -> FAILED, releasing lock for subsequent retry attempts."""
        key = self._make_key(channel, external_message_id)
        now = time.monotonic()
        async with self._lock:
            self._purge_expired(now)
            # Retain brief failure record (30s) or allow immediate retry
            self._cache.pop(key, None)

    async def get_state(
        self,
        channel: ChannelType,
        external_message_id: str,
    ) -> IdempotencyState | None:
        """Returns the current lifecycle state of the message if not expired."""
        key = self._make_key(channel, external_message_id)
        now = time.monotonic()
        async with self._lock:
            self._purge_expired(now)
            entry = self._cache.get(key)
            if entry is not None:
                state, exp = entry
                if exp > now:
                    return state
            return None

    async def is_duplicate(
        self,
        channel: ChannelType,
        external_message_id: str,
    ) -> bool:
        """Returns True if message is currently PROCESSING or COMPLETED."""
        state = await self.get_state(channel, external_message_id)
        return state in (IdempotencyState.PROCESSING, IdempotencyState.COMPLETED)

    async def mark_processed(
        self,
        channel: ChannelType,
        external_message_id: str,
    ) -> None:
        """Alias for mark_completed for backward compatibility."""
        await self.mark_completed(channel, external_message_id)

    async def clear(self) -> None:
        """Clears all stored entries (primarily for test resets)."""
        async with self._lock:
            self._cache.clear()


_global_idempotency_store: Optional[IdempotencyStore] = None


def get_idempotency_store() -> IdempotencyStore:
    """Returns singleton IdempotencyStore instance."""
    global _global_idempotency_store
    if _global_idempotency_store is None:
        _global_idempotency_store = IdempotencyStore()
    return _global_idempotency_store
