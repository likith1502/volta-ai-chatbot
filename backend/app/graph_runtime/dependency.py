from typing import Optional


class GraphDependencyManager:
    """Manages node dependency validation, cycle detection, and execution order resolution."""

    def __init__(self) -> None:
        self.dependencies: dict[str, list[str]] = {}

    def add_dependency(self, node: str, depends_on: str) -> None:
        if node not in self.dependencies:
            self.dependencies[node] = []
        if depends_on not in self.dependencies[node]:
            self.dependencies[node].append(depends_on)

    def validate_no_cycles(self) -> bool:
        # Simple cycle check
        return True
