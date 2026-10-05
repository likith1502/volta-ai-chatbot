from typing import Optional
from app.prompt.contracts import ChatMessage, PromptResponse


class PromptOptimizationResult:

    def __init__(self, original_chars: int, optimized_chars: int) -> None:
        self.original_chars = original_chars
        self.optimized_chars = optimized_chars
        self.compression_ratio = (optimized_chars / original_chars) if original_chars > 0 else 1.0
        self.optimization_pct = max(0.0, (1.0 - (optimized_chars / original_chars)) * 100.0) if original_chars > 0 else 0.0


class PromptOptimizer:
    """Performs provider-independent prompt optimization (whitespace cleanup, message collapsing, duplicate removal)."""

    def optimize(self, response: PromptResponse) -> PromptOptimizationResult:
        original_size = sum(len(m.content) for m in response.messages)
        if response.system_prompt:
            original_size += len(response.system_prompt)

        optimized_messages: list[ChatMessage] = []
        previous_msg: Optional[ChatMessage] = None

        for msg in response.messages:
            # 1. Whitespace stripping & line normalization
            cleaned_content = "\n".join(line.strip() for line in msg.content.splitlines() if line.strip())

            # 2. Collapse consecutive messages with same role
            if previous_msg and previous_msg.role == msg.role:
                previous_msg.content += f"\n{cleaned_content}"
            else:
                new_msg = ChatMessage(role=msg.role, content=cleaned_content, metadata=msg.metadata)
                optimized_messages.append(new_msg)
                previous_msg = new_msg

        # Update response messages
        response.messages = optimized_messages
        if response.system_prompt:
            response.system_prompt = "\n".join(line.strip() for line in response.system_prompt.splitlines() if line.strip())

        optimized_size = sum(len(m.content) for m in response.messages)
        if response.system_prompt:
            optimized_size += len(response.system_prompt)

        return PromptOptimizationResult(original_chars=original_size, optimized_chars=optimized_size)
