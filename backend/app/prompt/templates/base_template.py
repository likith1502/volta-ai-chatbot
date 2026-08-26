from abc import ABC, abstractmethod
from typing import Any, Optional

from app.prompt.contracts import PromptMessage, PromptVariable
from app.prompt.metadata import PromptTemplateMetadata
from app.prompt.versioning import TemplateRevision


class BasePromptTemplate(ABC):
    """Abstract Base Class defining standard prompt template contracts with revisioning and inheritance support."""

    def __init__(
        self,
        template_id: str,
        system_instruction: str = "",
        messages: Optional[list[PromptMessage]] = None,
        variables: Optional[list[PromptVariable]] = None,
        parent_template_id: Optional[str] = None,
        metadata: Optional[PromptTemplateMetadata] = None,
    ) -> None:
        self.template_id = template_id
        self.system_instruction = system_instruction
        self.messages: list[PromptMessage] = messages or []
        self.variables: list[PromptVariable] = variables or []
        self.parent_template_id = parent_template_id
        self.metadata = metadata or PromptTemplateMetadata(template_id=template_id)
        self.revisions: dict[str, TemplateRevision] = {}

        # Default revision v1
        self.add_revision(
            TemplateRevision(
                revision_id="v1",
                template_id=template_id,
                content_template="\n".join(m.content_template for m in self.messages),
                system_instruction=system_instruction,
            )
        )

    def add_revision(self, revision: TemplateRevision) -> None:
        self.revisions[revision.revision_id] = revision

    def get_revision(self, revision_id: str = "v1") -> Optional[TemplateRevision]:
        return self.revisions.get(revision_id)

    @property
    @abstractmethod
    def template_type(self) -> str:
        """Returns template type discriminator (e.g. 'chat', 'system', 'tool', 'agent')."""
        pass

    def add_message(
        self, role: str, content_template: str, metadata: Optional[dict] = None
    ) -> None:
        self.messages.append(
            PromptMessage(
                role=role, content_template=content_template, metadata=metadata or {}
            )
        )

    def add_variable(
        self,
        name: str,
        required: bool = True,
        default_value: Any = None,
        description: Optional[str] = None,
    ) -> None:
        self.variables.append(
            PromptVariable(
                name=name,
                required=required,
                default_value=default_value,
                description=description,
            )
        )
