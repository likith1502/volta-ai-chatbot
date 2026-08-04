class GraphException(Exception):
    """Base exception for all graph framework errors."""

    pass


class BuilderException(GraphException):
    """Exception raised during graph construction and validation."""

    pass


class DuplicateNodeException(BuilderException):
    """Exception raised when attempting to register a node with an existing node_id."""

    pass


class DuplicateEdgeException(BuilderException):
    """Exception raised when attempting to register a duplicate edge between same source and target nodes."""

    pass


class NodeNotFoundException(GraphException):
    """Exception raised when a referenced node ID cannot be found in the graph."""

    pass


class GraphValidationException(GraphException):
    """Exception raised when graph structural integrity rules are violated."""

    pass


class RegistryException(GraphException):
    """Exception raised during graph template registration or lookup failures."""

    pass
