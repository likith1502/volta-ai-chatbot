import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.events.event import WorkflowEvent
from app.events.event_status import WorkflowEventStatus
from app.events.event_types import (
    EventPriority,
    WorkflowEventCategory,
    WorkflowEventType,
)

PRIORITY_WEIGHTS = {
    EventPriority.LOW: 1,
    EventPriority.NORMAL: 2,
    EventPriority.HIGH: 3,
    EventPriority.CRITICAL: 4,
}


class WorkflowEventFilter(BaseModel):
    """Predicate filter for matching workflow events against specified criteria."""

    event_types: list[WorkflowEventType] = Field(default_factory=list)
    categories: list[WorkflowEventCategory] = Field(default_factory=list)
    statuses: list[WorkflowEventStatus] = Field(default_factory=list)
    workflow_id: Optional[str] = None
    graph_id: Optional[str] = None
    execution_id: Optional[uuid.UUID] = None
    node_id: Optional[str] = None
    min_priority: Optional[EventPriority] = None
    tags: list[str] = Field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def matches(self, event: WorkflowEvent) -> bool:
        """Evaluates whether an event satisfies all non-empty filter criteria."""
        if self.event_types and event.event_type not in self.event_types:
            return False

        if self.categories and event.category not in self.categories:
            return False

        if self.statuses and event.status not in self.statuses:
            return False

        if self.workflow_id and event.workflow_id != self.workflow_id:
            return False

        if self.graph_id and event.graph_id != self.graph_id:
            return False

        if self.execution_id and event.execution_id != self.execution_id:
            return False

        if self.node_id and event.node_id != self.node_id:
            return False

        if self.min_priority:
            event_weight = PRIORITY_WEIGHTS.get(event.metadata.priority, 2)
            min_weight = PRIORITY_WEIGHTS.get(self.min_priority, 2)
            if event_weight < min_weight:
                return False

        if self.tags:
            event_tags = set(event.metadata.tags)
            if not any(tag in event_tags for tag in self.tags):
                return False

        if self.start_time and event.timestamp < self.start_time:
            return False

        if self.end_time and event.timestamp > self.end_time:
            return False

        return True
