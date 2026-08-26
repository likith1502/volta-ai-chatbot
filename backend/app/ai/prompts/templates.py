from typing import Any, Sequence

from app.ai.models import AIMessage
from app.models.message import Message


def format_conversation_history(messages: Sequence[Message]) -> list[AIMessage]:
    """Converts ORM Message instances into standardized AIMessage payloads."""
    formatted = []
    for msg in messages:
        role = msg.role.value if hasattr(msg.role, "value") else str(msg.role)
        formatted.append(AIMessage(role=role, content=msg.content))
    return formatted


def build_context_prompt(user_message: str, memories: Sequence[Any] = ()) -> str:
    """Builds a contextual prompt enriched with relevant user memories if available."""
    if not memories:
        return user_message

    memory_summary = "\n".join(
        [
            f"- {m.memory_key}: {m.memory_value}"
            for m in memories
            if hasattr(m, "memory_key")
        ]
    )
    return f"[User Context & Preferences]\n{memory_summary}\n\n[User Input]\n{user_message}"
