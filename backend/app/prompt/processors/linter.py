from typing import Optional
from app.prompt.contracts import PromptMessage, PromptVariable
from app.prompt.variables import PromptVariableStore


class LintIssue:

    def __init__(self, issue_type: str, message: str, severity: str = "warning") -> None:
        self.issue_type = issue_type  # 'duplicate_instruction', 'contradiction', 'excessive_length', 'unreachable_placeholder'
        self.message = message
        self.severity = severity  # 'info', 'warning', 'error'


class PromptLintResult:

    def __init__(self) -> None:
        self.issues: list[LintIssue] = []

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)


class PromptLinter:
    """Analyzes prompt template text for quality defects, contradictory statements, duplicated instructions, and excessive length."""

    def lint(
        self,
        messages: list[PromptMessage],
        system_instruction: Optional[str] = None,
        declared_variables: Optional[list[PromptVariable]] = None,
    ) -> PromptLintResult:
        result = PromptLintResult()
        declared_names = {v.name for v in declared_variables} if declared_variables else set()

        # 1. System prompt length check
        if system_instruction and len(system_instruction) > 2000:
            result.issues.append(
                LintIssue(
                    issue_type="excessive_length",
                    message="System instruction exceeds 2000 characters. Consider truncating or splitting instructions.",
                    severity="warning",
                )
            )

        # 2. Check for duplicate content across messages
        seen_templates = set()
        for idx, msg in enumerate(messages):
            normalized = msg.content_template.strip().lower()
            if normalized in seen_templates:
                result.issues.append(
                    LintIssue(
                        issue_type="duplicate_instruction",
                        message=f"Message at index {idx} repeats identical content template.",
                        severity="warning",
                    )
                )
            seen_templates.add(normalized)

        # 3. Check for undeclared placeholders
        for msg in messages:
            placeholders = PromptVariableStore.extract_placeholders(msg.content_template)
            for ph in placeholders:
                if declared_names and ph not in declared_names:
                    result.issues.append(
                        LintIssue(
                            issue_type="unreachable_placeholder",
                            message=f"Placeholder '{ph}' is used in message but not declared in template variables.",
                            severity="info",
                        )
                    )

        return result
