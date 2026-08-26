import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from app.memory.memory import Memory


class MemoryContext(BaseModel):
    """Assembled runtime memory context container ready for prompt variable injection."""

    context_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    conversation_id: Optional[uuid.UUID] = None
    system_memories: list[Memory] = Field(default_factory=list)
    conversation_memories: list[Memory] = Field(default_factory=list)
    working_memories: list[Memory] = Field(default_factory=list)
    user_memories: list[Memory] = Field(default_factory=list)
    session_memories: list[Memory] = Field(default_factory=list)
    total_memories_count: int = Field(default=0, ge=0)
    total_token_estimate: int = Field(default=0, ge=0)
    strategy_used: str = Field(default="hybrid")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def format_as_text(self) -> str:
        """Formats assembled memory context into unified text string for prompt injection."""
        lines = []
        if self.system_memories:
            lines.append("--- SYSTEM MEMORIES ---")
            lines.extend(f"- {m.content}" for m in self.system_memories)

        if self.user_memories:
            lines.append("--- USER PREFERENCES & MEMORIES ---")
            lines.extend(f"- {m.content}" for m in self.user_memories)

        if self.conversation_memories:
            lines.append("--- RECENT CONVERSATION HISTORY ---")
            lines.extend(f"- {m.content}" for m in self.conversation_memories)

        if self.working_memories:
            lines.append("--- WORKING STATE ---")
            lines.extend(f"- {m.content}" for m in self.working_memories)

        return "\n".join(lines)
