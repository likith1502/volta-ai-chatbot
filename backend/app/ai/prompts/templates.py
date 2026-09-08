from typing import Any, Sequence, Union

from app.ai.models import AIMessage
from app.models.message import Message


def format_conversation_history(messages: Sequence[Union[Message, dict[str, Any]]]) -> list[AIMessage]:
    """Converts ORM Message instances or dictionaries into standardized AIMessage payloads."""
    formatted = []
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get("role", "user")
            content = msg.get("content", "")
        else:
            role = msg.role.value if hasattr(msg.role, "value") else str(msg.role)
            content = msg.content
        formatted.append(AIMessage(role=role, content=content))
    return formatted


def build_context_prompt(user_message: str, memories: Sequence[Any] = ()) -> str:
    """Builds a contextual prompt enriched with relevant user memories if available."""
    if not memories:
        return user_message

    memory_summary = "\n".join([f"- {m.memory_key}: {m.memory_value}" for m in memories if hasattr(m, "memory_key")])
    return f"[User Context & Preferences]\n{memory_summary}\n\n[User Input]\n{user_message}"
