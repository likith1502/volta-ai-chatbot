from typing import Callable, List, Optional, Type, Union

from app.events.event_filter import WorkflowEventFilter
from app.events.event_listener import WorkflowEventListener
from app.events.event_subscription import EventSubscription
from app.events.event_types import EventPriority, WorkflowEventCategory
from app.events.exceptions import (
    DuplicateListenerException,
    EventListenerNotFoundException,
)


class WorkflowEventRegistry:
    """Registry managing event subscriptions, listeners, priority ordering, and factory instantiations."""

    def __init__(self) -> None:
        self._subscriptions: dict[str, Union[EventSubscription, Callable[[], WorkflowEventListener]]] = {}

    def register(
        self,
        listener: Union[WorkflowEventListener, Type[WorkflowEventListener], Callable[[], WorkflowEventListener]],
        listener_id: Optional[str] = None,
        filter: Optional[WorkflowEventFilter] = None,
        priority: Optional[EventPriority] = None,
        overwrite: bool = False,
    ) -> EventSubscription:
        """Registers a listener instance, class, or factory as an active subscription."""
        target_id = listener_id
        if target_id is None:
            if isinstance(listener, WorkflowEventListener):
                target_id = listener.listener_id
            elif isinstance(listener, type) and issubclass(listener, WorkflowEventListener):
                target_id = getattr(listener, "listener_id", listener.__name__)
            elif callable(listener):
                target_id = getattr(listener, "__name__", str(id(listener)))
            else:
                target_id = str(listener)

        if target_id in self._subscriptions and not overwrite:
            raise DuplicateListenerException(
                f"Event listener with ID '{target_id}' is already registered."
            )

        if isinstance(listener, WorkflowEventListener):
            sub = EventSubscription(
                listener=listener,
                filter=filter,
                priority=priority or listener.priority,
            )
            self._subscriptions[target_id] = sub
            return sub
        elif isinstance(listener, type) and issubclass(listener, WorkflowEventListener):
            instance = listener(listener_id=target_id)
            sub = EventSubscription(
                listener=instance,
                filter=filter,
                priority=priority or instance.priority,
            )
            self._subscriptions[target_id] = sub
            return sub
        elif callable(listener):
            res = listener()
            if isinstance(res, WorkflowEventListener):
                sub = EventSubscription(
                    listener=res,
                    filter=filter,
                    priority=priority or res.priority,
                )
                self._subscriptions[target_id] = sub
                return sub
            raise EventListenerNotFoundException(
                f"Factory function for listener '{target_id}' did not return a WorkflowEventListener."
            )
        raise EventListenerNotFoundException(f"Invalid listener registration type for '{target_id}'.")

    def register_factory(
        self,
        listener_id: str,
        factory: Callable[[], WorkflowEventListener],
        filter: Optional[WorkflowEventFilter] = None,
        priority: Optional[EventPriority] = None,
        overwrite: bool = False,
    ) -> EventSubscription:
        """Registers a lazy listener factory function."""
        return self.register(
            listener=factory,
            listener_id=listener_id,
            filter=filter,
            priority=priority,
            overwrite=overwrite,
        )

    def unregister(self, listener_id: str) -> None:
        """Unregisters a listener subscription by ID."""
        if listener_id not in self._subscriptions:
            raise EventListenerNotFoundException(
                f"Event listener with ID '{listener_id}' not found."
            )
        del self._subscriptions[listener_id]

    def exists(self, listener_id: str) -> bool:
        """Returns True if listener_id is registered."""
        return listener_id in self._subscriptions

    def lookup(self, listener_id: str) -> EventSubscription:
        """Retrieves subscription by listener_id."""
        if listener_id not in self._subscriptions:
            raise EventListenerNotFoundException(
                f"Event listener with ID '{listener_id}' not found."
            )
        sub = self._subscriptions[listener_id]
        if isinstance(sub, EventSubscription):
            return sub
        raise EventListenerNotFoundException(f"Invalid subscription stored for '{listener_id}'.")

    def list(self) -> List[str]:
        """Lists IDs of registered listeners."""
        return list(self._subscriptions.keys())

    def list_subscribers(self) -> List[EventSubscription]:
        """Lists all active subscriptions sorted by priority (CRITICAL -> HIGH -> NORMAL -> LOW)."""
        weights = {
            EventPriority.CRITICAL: 4,
            EventPriority.HIGH: 3,
            EventPriority.NORMAL: 2,
            EventPriority.LOW: 1,
        }
        active_subs = [s for s in self._subscriptions.values() if isinstance(s, EventSubscription) and s.enabled]
        return sorted(active_subs, key=lambda s: weights.get(s.priority, 2), reverse=True)

    def clear(self) -> None:
        """Clears all registered subscriptions."""
        self._subscriptions.clear()
