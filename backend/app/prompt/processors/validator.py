from typing import Any
from app.prompt.contracts import PromptMessage, PromptVariable
from app.prompt.exceptions import PromptValidationError
from app.prompt.variables import PromptVariableStore


class PromptValidationResult:

    def __init__(self) -> None:
        self.is_valid: bool = True
        self.missing_variables: list[str] = []
        self.errors: list[str] = []
        self.warnings: list[str] = []


class PromptValidator:
    """Validates prompt templates and supplied variables against requirements and constraints."""

    def validate(
        self,
        messages: list[PromptMessage],
        required_variables: list[PromptVariable],
        supplied_variables: dict[str, Any],
        max_length_chars: int = 50000,
    ) -> PromptValidationResult:
        result = PromptValidationResult()

        # 1. Check required variables
        for req_var in required_variables:
            if req_var.required and req_var.name not in supplied_variables and req_var.default_value is None:
                result.is_valid = False
                result.missing_variables.append(req_var.name)
                result.errors.append(f"Required variable '{req_var.name}' is missing.")

        # 2. Check unhandled placeholders in templates
        all_placeholders = set()
        for msg in messages:
            all_placeholders.update(PromptVariableStore.extract_placeholders(msg.content_template))

        for ph in all_placeholders:
            if ph not in supplied_variables and not any(v.name == ph and v.default_value is not None for v in required_variables):
                result.warnings.append(f"Placeholder '{ph}' has no supplied variable value or default.")

        # 3. Check message size constraints
        total_len = sum(len(m.content_template) for m in messages)
        if total_len > max_length_chars:
            result.is_valid = False
            result.errors.append(f"Prompt template length ({total_len} chars) exceeds max limit ({max_length_chars} chars).")

        return result
