class GraphError(Exception):
    """Base exception for all graph framework errors."""

    pass


class BuilderError(GraphError):
    """Exception raised during graph construction and validation."""

    pass


class DuplicateNodeError(BuilderError):
    """Exception raised when attempting to register a node with an existing node_id."""

    pass


class DuplicateEdgeError(BuilderError):
    """Exception raised when attempting to register a duplicate edge between same source and target nodes."""

    pass


class NodeNotFoundError(GraphError):
    """Exception raised when a referenced node ID cannot be found in the graph."""

    pass


class GraphValidationError(GraphError):
    """Exception raised when graph structural integrity rules are violated."""

    pass


class RegistryError(GraphError):
    """Exception raised during graph template registration or lookup failures."""

    pass
