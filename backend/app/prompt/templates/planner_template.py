from app.prompt.templates.base_template import BasePromptTemplate


class PlannerPromptTemplate(BasePromptTemplate):
    """Placeholder template contract for multi-step task planning prompting."""

    @property
    def template_type(self) -> str:
        return "planner"
