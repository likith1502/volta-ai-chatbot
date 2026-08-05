import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


class StreamHistoryRecord(BaseModel):
    """Audit log entry recording a stream message delivery dispatch."""

    record_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    message_id: uuid.UUID
    channel: str
    adapter: str
    delivery_result: str = "success"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class StreamHistory(BaseModel):
    """Log tracking historical stream delivery audit records."""

    records: list[StreamHistoryRecord] = Field(default_factory=list)

    def record_delivery(
        self,
        message_id: uuid.UUID,
        channel: str,
        adapter: str,
        delivery_result: str = "success",
        metadata: Optional[dict[str, Any]] = None,
    ) -> StreamHistoryRecord:
        """Records a new stream delivery audit record."""
        rec = StreamHistoryRecord(
            message_id=message_id,
            channel=channel,
            adapter=adapter,
            delivery_result=delivery_result,
            metadata=metadata or {},
        )
        self.records.append(rec)
        return rec
