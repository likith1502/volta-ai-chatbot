from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.events.event import WorkflowEvent
from app.events.event_types import EventPriority


class WorkflowEventListener(BaseModel, ABC):
    """
    Abstract contract for workflow event listeners.
    Listeners are read-only observers. They MUST NOT mutate execution state, ConversationState,
    or perform irreversible external side effects.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    listener_id: str
    priority: EventPriority = EventPriority.NORMAL
    tags: list[str] = Field(default_factory=list)

    def supports(self, event: WorkflowEvent) -> bool:
        """Evaluates whether this listener handles the target event."""
        return True

    async def before_event(self, event: WorkflowEvent) -> None:
        """Lifecycle hook invoked immediately prior to on_event."""
        pass

    @abstractmethod
    async def on_event(self, event: WorkflowEvent) -> None:
        """
        Asynchronously handles an observed event notification.
        Must be implemented by concrete listener subclasses.
        """
        pass

    async def after_event(self, event: WorkflowEvent) -> None:
        """Lifecycle hook invoked following successful on_event completion."""
        pass

    async def on_error(self, event: WorkflowEvent, error: Exception) -> None:
        """Error handler hook invoked if on_event encounters an exception."""
        pass
