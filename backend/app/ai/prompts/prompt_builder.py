from typing import Any, Optional, Sequence, Union

from app.ai.models import AIMessage, AIRequest
from app.ai.prompts.system_prompt import VOLTA_SYSTEM_PROMPT
from app.ai.prompts.templates import format_conversation_history
from app.models.memory import Memory
from app.models.message import Message


class PromptBuilder:
    """Builder for constructing provider-independent AIRequest payloads."""

    def __init__(self, system_prompt: Optional[str] = None) -> None:
        self.system_prompt = system_prompt or VOLTA_SYSTEM_PROMPT

    def build(
        self,
        user_input: str,
        conversation_history: Sequence[Union[Message, dict[str, Any]]] = (),
        memories: Sequence[Union[Memory, Any]] = (),
    ) -> AIRequest:
        """Merges system prompt, memories, conversation history, and user input turn."""
        messages: list[AIMessage] = []

        # 1. Format history messages
        if conversation_history:
            messages.extend(format_conversation_history(conversation_history))

        # 2. Enrich current user message with memories if available
        if memories:
            memory_summary = "\n".join(
                [f"- {m.memory_key}: {m.memory_value}" for m in memories if hasattr(m, "memory_key")]
            )
            enriched_content = f"[User Context & Preferences]\n{memory_summary}\n\n{user_input}"
            messages.append(AIMessage(role="user", content=enriched_content))
        else:
            # Avoid duplicating user_input if already present in history
            last_msg = conversation_history[-1] if conversation_history else None
            last_content = (
                last_msg.get("content")
                if isinstance(last_msg, dict)
                else getattr(last_msg, "content", None)
            )
            if not conversation_history or last_content != user_input:
                messages.append(AIMessage(role="user", content=user_input))

        return AIRequest(
            messages=messages,
            system_prompt=self.system_prompt,
        )
