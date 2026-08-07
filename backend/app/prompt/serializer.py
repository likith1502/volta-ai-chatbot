import json
from typing import Any
from app.prompt.result import PromptResult
from app.prompt.templates.base_template import BasePromptTemplate


class PromptSerializer:
    """Import and export helpers formatting templates and rendered prompts as JSON, Markdown, or YAML."""

    @staticmethod
    def template_to_json(template: BasePromptTemplate) -> str:
        data = {
            "template_id": template.template_id,
            "template_type": template.template_type,
            "system_instruction": template.system_instruction,
            "messages": [m.model_dump() for m in template.messages],
            "variables": [v.model_dump() for v in template.variables],
            "parent_template_id": template.parent_template_id,
            "metadata": template.metadata.model_dump(),
        }
        return json.dumps(data, indent=2, default=str)

    @staticmethod
    def result_to_markdown(result: PromptResult) -> str:
        lines = [
            f"# Prompt Execution Result — {result.context.prompt_id}",
            f"- **Template ID**: `{result.context.template_id}` | **Revision**: `{result.context.revision_id}`",
            f"- **Execution Status**: `{result.execution_status}`",
            f"- **Render Latency**: `{result.metrics.render_time_ms:.2f}ms` | **Token Estimate**: `{result.metrics.token_estimate}`",
            "",
            "## Rendered Messages",
        ]
        if result.rendered_prompt:
            if result.rendered_prompt.system_prompt:
                lines.append("### SYSTEM")
                lines.append(result.rendered_prompt.system_prompt)
                lines.append("")
            for msg in result.rendered_prompt.messages:
                lines.append(f"### {msg.role.upper()}")
                lines.append(msg.content)
                lines.append("")

        if result.runtime_result and result.runtime_result.response:
            lines.append("## LLM Generation Response")
            lines.append(result.runtime_result.response.content)

        return "\n".join(lines)
