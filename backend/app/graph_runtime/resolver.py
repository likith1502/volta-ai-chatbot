class GraphResolver:
    """Resolves Workflow -> Node -> Runtime Action without embedding business logic."""

    def resolve_action(self, node_id: str) -> str:
        n_lower = node_id.lower()
        if "prompt" in n_lower or "llm" in n_lower:
            return "execute_prompt"
        elif "tool" in n_lower:
            return "execute_tool"
        elif "memory" in n_lower:
            return "assemble_memory"
        return "noop"
