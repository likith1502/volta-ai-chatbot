from typing import Any, Dict, Optional


def success_response(
    data: Optional[Any] = None,
    message: str = "Operation successful",
) -> Dict[str, Any]:
    """Generates a standardized success response dictionary."""
    return {
        "success": True,
        "message": message,
        "data": data if data is not None else {},
        "errors": None,
    }


def error_response(
    message: str = "An error occurred",
    errors: Optional[Any] = None,
) -> Dict[str, Any]:
    """Generates a standardized error response dictionary."""
    return {
        "success": False,
        "message": message,
        "data": None,
        "errors": errors if errors is not None else {},
    }
