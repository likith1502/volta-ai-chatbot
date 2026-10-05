from app.prompt.templates.base_template import BasePromptTemplate


class ReflectionPromptTemplate(BasePromptTemplate):
    """Placeholder template contract for agent reflection and memory synthesis prompting."""

    @property
    def template_type(self) -> str:
        return "reflection"
