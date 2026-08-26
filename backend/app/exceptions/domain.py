from typing import Any, Optional

from app.core.exceptions import AppError


class UserAlreadyExistsError(AppError):
    """Raised when attempting to create a user with an email or phone that already exists."""

    def __init__(
        self,
        message: str = "User with this email already exists",
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message=message, status_code=409, details=details)


class UserNotFoundError(AppError):
    """Raised when a requested user entity cannot be found."""

    def __init__(
        self, message: str = "User not found", details: Optional[Any] = None
    ) -> None:
        super().__init__(message=message, status_code=404, details=details)


class ConversationNotFoundError(AppError):
    """Raised when a requested conversation entity cannot be found."""

    def __init__(
        self,
        message: str = "Conversation session not found",
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message=message, status_code=404, details=details)


class ConversationClosedError(AppError):
    """Raised when attempting to append messages or recommendations to an inactive or archived conversation."""

    def __init__(
        self,
        message: str = "Conversation session is closed or archived",
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message=message, status_code=400, details=details)


class RecommendationNotFoundError(AppError):
    """Raised when a requested recommendation entity cannot be found."""

    def __init__(
        self, message: str = "Recommendation not found", details: Optional[Any] = None
    ) -> None:
        super().__init__(message=message, status_code=404, details=details)


class RecommendationExpiredError(AppError):
    """Raised when attempting to book an expired recommendation."""

    def __init__(
        self,
        message: str = "Recommendation has expired or is no longer valid",
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message=message, status_code=400, details=details)


class BookingNotFoundError(AppError):
    """Raised when a requested booking entity cannot be found."""

    def __init__(
        self,
        message: str = "Booking reservation not found",
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message=message, status_code=404, details=details)


class InvalidBookingStatusError(AppError):
    """Raised when attempting an invalid status transition on a booking."""

    def __init__(
        self,
        message: str = "Invalid booking status transition",
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message=message, status_code=400, details=details)


class NotificationNotFoundError(AppError):
    """Raised when a requested notification cannot be found."""

    def __init__(
        self, message: str = "Notification not found", details: Optional[Any] = None
    ) -> None:
        super().__init__(message=message, status_code=404, details=details)
