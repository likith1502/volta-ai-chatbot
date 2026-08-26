from app.prompt.templates.base_template import BasePromptTemplate


class ToolPromptTemplate(BasePromptTemplate):
    """Placeholder template contract for Phase 7.3 Tool Runtime prompt formatting."""

    @property
    def template_type(self) -> str:
        return "tool"
