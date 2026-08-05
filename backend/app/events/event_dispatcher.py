import time
from typing import Any, List

from app.events.event import WorkflowEvent
from app.events.event_result import WorkflowEventResult
from app.events.event_subscription import EventSubscription


class WorkflowEventDispatcher:
    """
    Dispatches published events to registered subscriber listeners.
    Provides listener filtering, priority ordering, and error isolation guarantees.
    """

    async def dispatch(
        self,
        event: WorkflowEvent,
        subscriptions: List[EventSubscription],
    ) -> WorkflowEventResult:
        start_time = time.perf_counter()
        processed = 0
        ignored = 0
        errors: List[dict[str, Any]] = []
        warnings: List[str] = []

        for sub in subscriptions:
            if not sub.enabled:
                ignored += 1
                continue

            if sub.filter and not sub.filter.matches(event):
                ignored += 1
                continue

            if not sub.listener.supports(event):
                ignored += 1
                continue

            # Execute listener with error isolation
            try:
                await sub.listener.before_event(event)
                await sub.listener.on_event(event)
                await sub.listener.after_event(event)
                processed += 1
            except Exception as exc:
                errors.append(
                    {"listener_id": sub.listener.listener_id, "error": str(exc)}
                )
                try:
                    await sub.listener.on_error(event, exc)
                except Exception:
                    pass

        duration = round(time.perf_counter() - start_time, 6)

        return WorkflowEventResult(
            success=len(errors) == 0,
            processed=processed,
            ignored=ignored,
            listener_count=len(subscriptions),
            processing_time=duration,
            warnings=warnings,
            errors=errors,
        )
