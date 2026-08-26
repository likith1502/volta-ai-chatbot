"""Deployment hooks — pre/post deploy, pre/post rollback, pre/post scale."""

from dataclasses import dataclass
from typing import Any, Awaitable, Callable


@dataclass
class DeploymentHookResult:
    hook_name: str
    passed: bool
    message: str = ""


class DeploymentHooks:
    """Registry for pre/post deployment lifecycle hooks."""

    def __init__(self) -> None:
        self._hooks: dict[str, list[Callable[..., Awaitable[bool]]]] = {}

    def register(self, event: str, fn: Callable[..., Awaitable[bool]]) -> None:
        self._hooks.setdefault(event, []).append(fn)

    async def run(
        self, event: str, context: dict[str, Any] | None = None
    ) -> list[DeploymentHookResult]:
        results: list[DeploymentHookResult] = []
        for fn in self._hooks.get(event, []):
            try:
                passed = await fn(context or {})
                results.append(
                    DeploymentHookResult(hook_name=fn.__name__, passed=passed)
                )
            except Exception as exc:
                results.append(
                    DeploymentHookResult(
                        hook_name=fn.__name__, passed=False, message=str(exc)
                    )
                )
        return results
