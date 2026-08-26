from pydantic import BaseModel, Field


class ToolDependencyNode(BaseModel):
    tool_name: str
    depends_on: list[str] = Field(default_factory=list)


class ToolDependencyGraph(BaseModel):
    """Represents tool dependency structure for sequential pipeline or multi-agent execution."""

    nodes: list[ToolDependencyNode] = Field(default_factory=list)

    def add_dependency(self, tool_name: str, depends_on: str) -> None:
        for node in self.nodes:
            if node.tool_name == tool_name:
                if depends_on not in node.depends_on:
                    node.depends_on.append(depends_on)
                return
        self.nodes.append(
            ToolDependencyNode(tool_name=tool_name, depends_on=[depends_on])
        )
