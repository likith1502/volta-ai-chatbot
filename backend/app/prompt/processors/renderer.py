import time
from typing import Any, Optional
from app.prompt.contracts import ChatMessage, PromptMessage, PromptResponse
from app.prompt.variables import PromptVariableStore


class PromptRenderer:
    """Renders raw prompt messages and templates by substituting variables into placeholders."""

    def render(
        self,
        template_id: str,
        revision_id: str,
        messages: list[PromptMessage],
        variables: dict[str, Any],
        system_instruction: Optional[str] = None,
    ) -> PromptResponse:
        """Renders list of PromptMessages into concrete ChatMessage instances."""
        rendered_messages: list[ChatMessage] = []

        rendered_system_prompt: Optional[str] = None
        if system_instruction:
            rendered_system_prompt = PromptVariableStore.substitute(system_instruction, variables)

        for p_msg in messages:
            content = PromptVariableStore.substitute(p_msg.content_template, variables)
            rendered_messages.append(
                ChatMessage(
                    role=p_msg.role,
                    content=content,
                    metadata=p_msg.metadata,
                )
            )

        return PromptResponse(
            template_id=template_id,
            revision_id=revision_id,
            messages=rendered_messages,
            system_prompt=rendered_system_prompt,
            variables_applied=variables,
        )
