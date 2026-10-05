from app.prompt.templates.base_template import BasePromptTemplate


class WorkflowPromptTemplate(BasePromptTemplate):
    """Placeholder template contract for Phase 7.4 Graph Workflow prompt formatting."""

    @property
    def template_type(self) -> str:
        return "workflow"
