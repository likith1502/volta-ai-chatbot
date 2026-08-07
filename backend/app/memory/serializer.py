import json
from typing import Any
from app.memory.context import MemoryContext
from app.memory.memory import Memory


class MemorySerializer:
    """Serialization and export helpers formatting memory objects into JSON or Markdown."""

    @staticmethod
    def memory_to_json(memory: Memory) -> str:
        return memory.model_dump_json(indent=2)

    @staticmethod
    def context_to_markdown(context: MemoryContext) -> str:
        lines = [
            f"# Assembled Memory Context — {context.context_id}",
            f"- **Conversation ID**: `{context.conversation_id}`",
            f"- **Strategy Used**: `{context.strategy_used}`",
            f"- **Total Memories**: `{context.total_memories_count}` | **Token Estimate**: `{context.total_token_estimate}`",
            "",
            "## Content Preview",
            context.format_as_text(),
        ]
        return "\n".join(lines)
