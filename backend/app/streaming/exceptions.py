class StreamError(Exception):
    """Base exception for all streaming system errors."""

    pass


class StreamValidationError(StreamError):
    """Raised when stream message payload, schema, or predicate validation fails."""

    pass


class StreamSerializationError(StreamError):
    """Raised when stream payload serialization or deserialization fails."""

    pass


class StreamDispatcherError(StreamError):
    """Raised when an unhandled error occurs during stream message dispatching."""

    pass


class StreamAdapterError(StreamError):
    """Raised when a stream adapter connection, transport, or flush operation fails."""

    pass


class StreamChannelError(StreamError):
    """Raised when stream channel creation, lookup, or subscription operations fail."""

    pass


class StreamSubscriptionError(StreamError):
    """Raised when stream subscription binding or processing operations fail."""

    pass
