from typing import Any, Optional
from app.core.exceptions import AppException


class UserAlreadyExistsException(AppException):
    """Raised when attempting to create a user with an email or phone that already exists."""

    def __init__(self, message: str = "User with this email already exists", details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=409, details=details)


class UserNotFoundException(AppException):
    """Raised when a requested user entity cannot be found."""

    def __init__(self, message: str = "User not found", details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=404, details=details)


class ConversationNotFoundException(AppException):
    """Raised when a requested conversation entity cannot be found."""

    def __init__(self, message: str = "Conversation session not found", details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=404, details=details)


class ConversationClosedException(AppException):
    """Raised when attempting to append messages or recommendations to an inactive or archived conversation."""

    def __init__(self, message: str = "Conversation session is closed or archived", details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=400, details=details)


class RecommendationNotFoundException(AppException):
    """Raised when a requested recommendation entity cannot be found."""

    def __init__(self, message: str = "Recommendation not found", details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=404, details=details)


class RecommendationExpiredException(AppException):
    """Raised when attempting to book an expired recommendation."""

    def __init__(self, message: str = "Recommendation has expired or is no longer valid", details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=400, details=details)


class BookingNotFoundException(AppException):
    """Raised when a requested booking entity cannot be found."""

    def __init__(self, message: str = "Booking reservation not found", details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=404, details=details)


class InvalidBookingStatusException(AppException):
    """Raised when attempting an invalid status transition on a booking."""

    def __init__(self, message: str = "Invalid booking status transition", details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=400, details=details)


class NotificationNotFoundException(AppException):
    """Raised when a requested notification cannot be found."""

    def __init__(self, message: str = "Notification not found", details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=404, details=details)
