import re
from typing import Any, Optional

from app.prompt.contracts import PromptVariable


class PromptVariableStore:
    """Store managing variable definitions, default values, and substitution helpers."""

    def __init__(self, variables: Optional[list[PromptVariable]] = None) -> None:
        self._variables: dict[str, PromptVariable] = {}
        if variables:
            for v in variables:
                self.register(v)

    def register(self, variable: PromptVariable) -> None:
        self._variables[variable.name] = variable

    def get(self, name: str) -> Optional[PromptVariable]:
        return self._variables.get(name)

    def list_variables(self) -> list[PromptVariable]:
        return list(self._variables.values())

    @staticmethod
    def extract_placeholders(text: str) -> set[str]:
        """Extracts placeholder names enclosed in single curly braces `{variable_name}` from string."""
        return set(re.findall(r"\{([a-zA-Z0-9_]+)\}", text))

    @staticmethod
    def substitute(
        text: str, variables: dict[str, Any], defaults: Optional[dict[str, Any]] = None
    ) -> str:
        """Substitutes variables into `{variable_name}` placeholders in text string."""
        defaults = defaults or {}
        placeholders = PromptVariableStore.extract_placeholders(text)
        result = text
        for var_name in placeholders:
            val = variables.get(var_name)
            if val is None:
                val = defaults.get(var_name, f"{{{var_name}}}")
            result = result.replace(f"{{{var_name}}}", str(val))
        return result
