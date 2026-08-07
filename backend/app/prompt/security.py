import re
from typing import Optional
from pydantic import BaseModel, Field


class PromptSecurityPolicy(BaseModel):
    """Provider-independent security policy defining length bounds, blocked keywords, and injection detection."""

    max_prompt_length_chars: int = Field(default=50000, ge=100)
    blocked_placeholders: list[str] = Field(default_factory=lambda: ["__system__", "__admin__", "eval("])
    restricted_variable_names: list[str] = Field(default_factory=lambda: ["api_key", "secret", "password"])
    enable_injection_detection: bool = True

    def validate_variable_name(self, name: str) -> bool:
        """Returns True if variable name is allowed."""
        return name.lower() not in self.restricted_variable_names

    def detect_injection(self, text: str) -> Optional[str]:
        """Detects potential prompt injection patterns in text string."""
        if not self.enable_injection_detection:
            return None

        patterns = [
            (r"ignore\s+(all\s+)?previous\s+instructions", "Prompt injection attempt detected: ignore previous instructions"),
            (r"system\s*:\s*you\s+are", "System role override attempt detected"),
            (r"<script.*?>", "HTML/XSS injection pattern detected"),
        ]

        for pattern, msg in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return msg
        return None
