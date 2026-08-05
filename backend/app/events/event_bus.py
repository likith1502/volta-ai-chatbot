from typing import Callable, List, Optional, Type, Union

from app.events.event import WorkflowEvent
from app.events.event_dispatcher import WorkflowEventDispatcher
from app.events.event_filter import WorkflowEventFilter
from app.events.event_listener import WorkflowEventListener
from app.events.event_metrics import WorkflowEventMetrics
from app.events.event_registry import WorkflowEventRegistry
from app.events.event_result import WorkflowEventResult
from app.events.event_subscription import EventSubscription
from app.events.event_types import EventPriority


class WorkflowEventBus:
    """
    In-memory synchronous & async-compatible event bus.
    
    Delivery Guarantee Invariant (ADR 028):
    The Event Bus guarantees at-most-once in-memory delivery. It does NOT provide persistence,
    retries, acknowledgements, ordering across processes, or durability.
    """

    def __init__(
        self,
        registry: Optional[WorkflowEventRegistry] = None,
        dispatcher: Optional[WorkflowEventDispatcher] = None,
    ) -> None:
        self.registry = registry or WorkflowEventRegistry()
        self.dispatcher = dispatcher or WorkflowEventDispatcher()
        self.metrics = WorkflowEventMetrics()

    def subscribe(
        self,
        listener: Union[WorkflowEventListener, Type[WorkflowEventListener], Callable[[], WorkflowEventListener]],
        listener_id: Optional[str] = None,
        filter: Optional[WorkflowEventFilter] = None,
        priority: Optional[EventPriority] = None,
        overwrite: bool = False,
    ) -> EventSubscription:
        """Subscribes a listener to the event bus."""
        return self.registry.register(
            listener=listener,
            listener_id=listener_id,
            filter=filter,
            priority=priority,
            overwrite=overwrite,
        )

    def unsubscribe(self, listener_id: str) -> None:
        """Unsubscribes a listener from the event bus."""
        self.registry.unregister(listener_id)

    def exists(self, listener_id: str) -> bool:
        """Returns True if listener_id is registered."""
        return self.registry.exists(listener_id)

    def list_subscribers(self) -> List[EventSubscription]:
        """Lists active subscribers sorted by priority."""
        return self.registry.list_subscribers()

    def clear(self) -> None:
        """Clears all subscribers."""
        self.registry.clear()

    async def publish(self, event: WorkflowEvent) -> WorkflowEventResult:
        """Publishes a single WorkflowEvent to all matching subscribed listeners."""
        subscribers = self.registry.list_subscribers()
        result = await self.dispatcher.dispatch(event, subscribers)

        if result.success:
            self.metrics.events_processed += 1
        else:
            self.metrics.events_failed += 1
        self.metrics.dispatch_time += result.processing_time
        self.metrics.compute_metrics()

        return result

    async def publish_batch(self, events: List[WorkflowEvent]) -> List[WorkflowEventResult]:
        """Publishes a batch of WorkflowEvent instances sequentially to matching subscribers."""
        results = []
        for event in events:
            res = await self.publish(event)
            results.append(res)
        return results
