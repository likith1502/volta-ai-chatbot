from app.prompt.templates.base_template import BasePromptTemplate


class DecisionPromptTemplate(BasePromptTemplate):
    """Placeholder template contract for agentic decision node prompting."""

    @property
    def template_type(self) -> str:
        return "decision"
