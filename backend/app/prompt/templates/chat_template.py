from app.prompt.templates.base_template import BasePromptTemplate


class ChatPromptTemplate(BasePromptTemplate):
    """Standard conversational turn template for multi-role chat turns."""

    @property
    def template_type(self) -> str:
        return "chat"
