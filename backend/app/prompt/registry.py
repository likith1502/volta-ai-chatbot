import logging
from typing import Optional
from app.prompt.exceptions import TemplateNotFoundError
from app.prompt.profile import PromptProfile
from app.prompt.templates.base_template import BasePromptTemplate

logger = logging.getLogger("app.prompt.registry")


class PromptRegistry:
    """Thread-safe registry managing registered BasePromptTemplate implementations and PromptProfile objects."""

    def __init__(self) -> None:
        self._templates: dict[str, BasePromptTemplate] = {}
        self._profiles: dict[str, PromptProfile] = {}
        self._register_default_profiles()

    def _register_default_profiles(self) -> None:
        """Registers built-in default generation profiles."""
        self.register_profile(
            PromptProfile(
                profile_id="default_chat",
                display_name="Default Chat Generation Profile",
                temperature=0.7,
                max_tokens=1000,
                description="Balanced generation profile for conversational turns.",
            )
        )
        self.register_profile(
            PromptProfile(
                profile_id="strict_json",
                display_name="Strict JSON Extraction Profile",
                temperature=0.1,
                max_tokens=1500,
                response_format="json",
                description="Low-temperature profile optimized for deterministic JSON output.",
            )
        )

    def register_template(self, template: BasePromptTemplate) -> None:
        """Registers a BasePromptTemplate instance."""
        tid = template.template_id.lower().strip()
        self._templates[tid] = template
        logger.info(f"Registered BasePromptTemplate '{tid}'")

    def unregister_template(self, template_id: str) -> None:
        """Unregisters a template by ID."""
        tid = template_id.lower().strip()
        self._templates.pop(tid, None)

    def lookup_template(self, template_id: str) -> BasePromptTemplate:
        """Retrieves template by ID or raises TemplateNotFoundError."""
        tid = template_id.lower().strip()
        if tid in self._templates:
            return self._templates[tid]
        raise TemplateNotFoundError(f"Prompt template '{template_id}' is not registered in PromptRegistry.")

    def get_template(self, template_id: str) -> Optional[BasePromptTemplate]:
        """Safely retrieves template if registered, else None."""
        try:
            return self.lookup_template(template_id)
        except TemplateNotFoundError:
            return None

    def exists_template(self, template_id: str) -> bool:
        return template_id.lower().strip() in self._templates

    def list_templates(self) -> list[BasePromptTemplate]:
        return list(self._templates.values())

    def register_profile(self, profile: PromptProfile) -> None:
        """Registers a PromptProfile instance."""
        pid = profile.profile_id.lower().strip()
        self._profiles[pid] = profile
        logger.info(f"Registered PromptProfile '{pid}'")

    def lookup_profile(self, profile_id: str) -> Optional[PromptProfile]:
        return self._profiles.get(profile_id.lower().strip())

    def list_profiles(self) -> list[PromptProfile]:
        return list(self._profiles.values())
