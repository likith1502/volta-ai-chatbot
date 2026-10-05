from abc import ABC, abstractmethod
from typing import Awaitable, Callable
from app.runtime.contracts import RuntimeRequest
from app.runtime.result import RuntimeResult


class RuntimeMiddleware(ABC):
    """Abstract middleware interface for processing runtime execution turns."""

    @abstractmethod
    async def process(
        self,
        request: RuntimeRequest,
        call_next: Callable[[RuntimeRequest], Awaitable[RuntimeResult]],
    ) -> RuntimeResult:
        """Processes request before call_next and intercepts result afterwards."""
        pass
