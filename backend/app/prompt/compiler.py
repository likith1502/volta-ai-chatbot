import uuid
from typing import Optional

from app.prompt.contracts import CompiledPrompt, PromptRequest, PromptResponse
from app.prompt.profile import PromptProfile


class PromptCompiler:
    """Responsibility: Converts internal PromptResponse & PromptProfile into CompiledPrompt for RuntimeManager."""

    def compile(
        self,
        request: PromptRequest,
        response: PromptResponse,
        profile: Optional[PromptProfile] = None,
    ) -> CompiledPrompt:
        """Compiles PromptResponse and optional PromptProfile into a CompiledPrompt object."""
        # Determine provider & model from request overrides, profile, or defaults
        provider = request.provider or (profile.provider if profile else None)
        model = request.model or (profile.model if profile else None)
        temperature = (
            request.temperature
            if request.temperature is not None
            else (profile.temperature if profile else None)
        )
        max_tokens = (
            request.max_tokens
            if request.max_tokens is not None
            else (profile.max_tokens if profile else None)
        )

        system_prompt = request.system_prompt_override or response.system_prompt

        return CompiledPrompt(
            compiled_id=uuid.uuid4(),
            messages=response.messages,
            system_prompt=system_prompt,
            provider=provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            metadata={
                "template_id": response.template_id,
                "revision_id": response.revision_id,
                "profile_id": profile.profile_id if profile else None,
            },
        )
