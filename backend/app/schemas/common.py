from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ResponseEnvelope(BaseModel, Generic[T]):
    """Standardized API response JSON envelope."""

    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None
    errors: Optional[Any] = None
