from app.prompt.templates.base_template import BasePromptTemplate


class SystemPromptTemplate(BasePromptTemplate):
    """System instruction template for configuring AI persona, behavior, and constraints."""

    @property
    def template_type(self) -> str:
        return "system"
