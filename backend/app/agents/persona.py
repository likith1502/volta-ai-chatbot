from pydantic import BaseModel, Field


class AgentPersona(BaseModel):
    """Behavioral traits and style instructions defining agent persona."""

    communication_style: str = Field(default="professional", description="e.g. professional, concise, empathetic")
    expertise: list[str] = Field(default_factory=lambda: ["urban_mobility", "customer_service"])
    tone: str = Field(default="helpful and authoritative")
    constraints: list[str] = Field(default_factory=lambda: ["Never share confidential API keys", "Strictly factual"])
    reasoning_style: str = Field(default="analytical", description="e.g. analytical, step-by-step, creative")
    language: str = Field(default="en")
    response_style: str = Field(default="markdown_structured")
