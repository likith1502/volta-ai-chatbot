from abc import ABC, abstractmethod
from typing import Optional
from app.prompt.templates.base_template import BasePromptTemplate


class PromptRepository(ABC):
    """Abstract storage repository abstraction managing persistence and retrieval of BasePromptTemplates (InMemory, Git, Database, Cloud Hub)."""

    @abstractmethod
    async def save_template(self, template: BasePromptTemplate) -> None:
        """Persists or updates a prompt template."""
        pass

    @abstractmethod
    async def get_template(self, template_id: str) -> Optional[BasePromptTemplate]:
        """Retrieves a prompt template by ID."""
        pass

    @abstractmethod
    async def delete_template(self, template_id: str) -> None:
        """Deletes a prompt template by ID."""
        pass

    @abstractmethod
    async def list_templates(self) -> list[BasePromptTemplate]:
        """Lists all stored prompt templates."""
        pass


class InMemoryPromptRepository(PromptRepository):
    """In-memory storage implementation for prompt templates."""

    def __init__(self) -> None:
        self._templates: dict[str, BasePromptTemplate] = {}

    async def save_template(self, template: BasePromptTemplate) -> None:
        tid = template.template_id.lower().strip()
        self._templates[tid] = template

    async def get_template(self, template_id: str) -> Optional[BasePromptTemplate]:
        return self._templates.get(template_id.lower().strip())

    async def delete_template(self, template_id: str) -> None:
        self._templates.pop(template_id.lower().strip(), None)

    async def list_templates(self) -> list[BasePromptTemplate]:
        return list(self._templates.values())
