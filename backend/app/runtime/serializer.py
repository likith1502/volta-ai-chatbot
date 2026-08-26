import json
from typing import Any

from app.runtime.contracts import ChatMessage
from app.runtime.result import RuntimeResult


class ConversationSerializer:
    """Serialization & export helper for runtime conversation turns, requests, and results."""

    @staticmethod
    def to_json(obj: Any) -> str:
        """Serializes runtime primitives (RuntimeRequest, RuntimeResponse, RuntimeResult) to JSON string."""
        if hasattr(obj, "model_dump_json"):
            return obj.model_dump_json(indent=2)
        return json.dumps(obj, default=str, indent=2)

    @staticmethod
    def to_markdown(messages: list[ChatMessage], result: RuntimeResult) -> str:
        """Exports a conversation turn and runtime result to clean GitHub-flavored markdown."""
        lines = [
            f"# Runtime Turn Export — {result.context.runtime_id}",
            f"- **Provider**: `{result.context.provider}` | **Model**: `{result.context.model}`",
            f"- **Execution Status**: `{result.execution_status}`",
            f"- **Latency**: `{result.metrics.latency_ms:.2f}ms` | **Tokens**: `{result.metrics.tokens.total_tokens}` | **Est. Cost**: `${result.metrics.estimated_cost_usd:.6f}`",
            "",
            "## Messages",
        ]
        for msg in messages:
            role_header = f"### {msg.role.upper()}"
            lines.append(role_header)
            lines.append(msg.content)
            lines.append("")

        if result.response:
            lines.append("## Assistant Response")
            lines.append(result.response.content)
            lines.append("")

        return "\n".join(lines)
