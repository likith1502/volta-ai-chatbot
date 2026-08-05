class StreamException(Exception):
    """Base exception for all streaming system errors."""

    pass


class StreamValidationException(StreamException):
    """Raised when stream message payload, schema, or predicate validation fails."""

    pass


class StreamSerializationException(StreamException):
    """Raised when stream payload serialization or deserialization fails."""

    pass


class StreamDispatcherException(StreamException):
    """Raised when an unhandled error occurs during stream message dispatching."""

    pass


class StreamAdapterException(StreamException):
    """Raised when a stream adapter connection, transport, or flush operation fails."""

    pass


class StreamChannelException(StreamException):
    """Raised when stream channel creation, lookup, or subscription operations fail."""

    pass


class StreamSubscriptionException(StreamException):
    """Raised when stream subscription binding or processing operations fail."""

    pass
