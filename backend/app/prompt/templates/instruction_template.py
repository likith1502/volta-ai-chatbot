from app.prompt.templates.base_template import BasePromptTemplate


class InstructionPromptTemplate(BasePromptTemplate):
    """Zero-shot or few-shot task instruction template."""

    @property
    def template_type(self) -> str:
        return "instruction"
