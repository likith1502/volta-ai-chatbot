from app.prompt.templates.base_template import BasePromptTemplate


class AgentPromptTemplate(BasePromptTemplate):
    """Placeholder template contract for Phase 7.5 Multi-Agent Runtime prompt formatting."""

    @property
    def template_type(self) -> str:
        return "agent"
