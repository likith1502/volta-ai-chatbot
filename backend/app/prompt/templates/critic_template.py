from app.prompt.templates.base_template import BasePromptTemplate


class CriticPromptTemplate(BasePromptTemplate):
    """Placeholder template contract for self-critique and quality review prompting."""

    @property
    def template_type(self) -> str:
        return "critic"
