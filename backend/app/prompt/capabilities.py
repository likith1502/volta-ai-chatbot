from pydantic import BaseModel, Field


class PromptCapabilities(BaseModel):
    """Capability reporting flags for prompt templates and prompt execution engine."""

    supports_variables: bool = True
    supports_templates: bool = True
    supports_system_prompt: bool = True
    supports_tools: bool = True
    supports_rag: bool = True
    supports_multimodal: bool = False
    supports_images: bool = False
    supports_json_output: bool = True
