import logging
from typing import Optional
from app.prompt.exceptions import TemplateNotFoundError
from app.prompt.profile import PromptProfile
from app.prompt.repository import InMemoryPromptRepository, PromptRepository
from app.prompt.templates.base_template import BasePromptTemplate

logger = logging.getLogger("app.prompt.registry")


class PromptRegistry:
    """Thread-safe registry managing BasePromptTemplate implementations backed by PromptRepository and managing PromptProfile objects."""

    def __init__(self, repository: Optional[PromptRepository] = None) -> None:
        self.repository = repository or InMemoryPromptRepository()
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

    async def unregister_template_async(self, template_id: str) -> None:
        await self.repository.delete_template(template_id)

    async def register_template_async(self, template: BasePromptTemplate) -> None:
        """Asynchronously registers or updates a template in repository."""
        await self.repository.save_template(template)
        logger.info(f"Registered BasePromptTemplate '{template.template_id}' in PromptRepository")

    def unregister_template(self, template_id: str) -> None:
        if isinstance(self.repository, InMemoryPromptRepository):
            tid = template_id.lower().strip()
            self.repository._templates.pop(tid, None)
        else:
            import asyncio
            asyncio.run(self.unregister_template_async(template_id))

    def register_template(self, template: BasePromptTemplate) -> None:
        """Synchronous wrapper registering template in repository."""
        if isinstance(self.repository, InMemoryPromptRepository):
            tid = template.template_id.lower().strip()
            self.repository._templates[tid] = template
        else:
            import asyncio
            asyncio.run(self.repository.save_template(template))
        logger.info(f"Registered BasePromptTemplate '{template.template_id}'")

    async def lookup_template_async(self, template_id: str) -> BasePromptTemplate:
        """Asynchronously retrieves template by ID or raises TemplateNotFoundError."""
        t = await self.repository.get_template(template_id)
        if t:
            return t
        raise TemplateNotFoundError(f"Prompt template '{template_id}' is not registered in PromptRepository.")

    def lookup_template(self, template_id: str) -> BasePromptTemplate:
        """Synchronous lookup helper for in-memory or sync contexts."""
        if isinstance(self.repository, InMemoryPromptRepository):
            tid = template_id.lower().strip()
            t = self.repository._templates.get(tid)
            if t:
                return t
            raise TemplateNotFoundError(f"Prompt template '{template_id}' is not registered in PromptRepository.")
        
        import asyncio
        return asyncio.run(self.lookup_template_async(template_id))

    async def get_template_async(self, template_id: str) -> Optional[BasePromptTemplate]:
        try:
            return await self.lookup_template_async(template_id)
        except TemplateNotFoundError:
            return None

    def get_template(self, template_id: str) -> Optional[BasePromptTemplate]:
        try:
            return self.lookup_template(template_id)
        except TemplateNotFoundError:
            return None

    def exists_template(self, template_id: str) -> bool:
        if isinstance(self.repository, InMemoryPromptRepository):
            return template_id.lower().strip() in self.repository._templates
        return self.get_template(template_id) is not None

    def list_templates(self) -> list[BasePromptTemplate]:
        if isinstance(self.repository, InMemoryPromptRepository):
            return list(self.repository._templates.values())
        import asyncio
        return asyncio.run(self.repository.list_templates())

    async def list_templates_async(self) -> list[BasePromptTemplate]:
        return await self.repository.list_templates()

    def register_profile(self, profile: PromptProfile) -> None:
        pid = profile.profile_id.lower().strip()
        self._profiles[pid] = profile
        logger.info(f"Registered PromptProfile '{pid}'")

    def lookup_profile(self, profile_id: str) -> Optional[PromptProfile]:
        return self._profiles.get(profile_id.lower().strip())

    def list_profiles(self) -> list[PromptProfile]:
        return list(self._profiles.values())
