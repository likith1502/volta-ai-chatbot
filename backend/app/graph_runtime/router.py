from typing import Any, Optional


class GraphRuntimeRouter:
    """Evaluates conditional routing logic to select next target node."""

    def route_next(self, current_node: str, state_data: dict[str, Any]) -> str:
        if current_node == "START":
            return "input_node"
        elif current_node == "input_node":
            return "llm_node"
        elif current_node == "llm_node":
            return "tool_node" if state_data.get("requires_tool") else "END"
        elif current_node == "tool_node":
            return "END"
        return "END"
