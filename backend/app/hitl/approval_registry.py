from typing import Callable, List, Optional, Type, Union

from app.hitl.approval_policy import ApprovalPolicy
from app.hitl.exceptions import ApprovalNotFoundError, ApprovalRegistryError


class ApprovalRegistry:
    """Registry for managing approval policies, handlers, and factory instantiations."""

    def __init__(self) -> None:
        self._policies: dict[
            str,
            Union[ApprovalPolicy, Type[ApprovalPolicy], Callable[[], ApprovalPolicy]],
        ] = {}

    def register(
        self,
        policy: Union[
            ApprovalPolicy, Type[ApprovalPolicy], Callable[[], ApprovalPolicy]
        ],
        policy_id: Optional[str] = None,
        overwrite: bool = False,
    ) -> None:
        """Registers an ApprovalPolicy instance, class, or factory."""
        target_id = policy_id
        if target_id is None:
            if isinstance(policy, ApprovalPolicy):
                target_id = policy.__class__.__name__
            elif isinstance(policy, type) and issubclass(policy, ApprovalPolicy):
                target_id = policy.__name__
            elif callable(policy):
                target_id = getattr(policy, "__name__", str(id(policy)))
            else:
                target_id = str(policy)

        if target_id in self._policies and not overwrite:
            raise ApprovalRegistryError(
                f"Approval policy '{target_id}' is already registered."
            )

        self._policies[target_id] = policy

    def register_factory(
        self,
        policy_id: str,
        factory: Callable[[], ApprovalPolicy],
        overwrite: bool = False,
    ) -> None:
        """Registers a policy factory."""
        self.register(policy=factory, policy_id=policy_id, overwrite=overwrite)

    def unregister(self, policy_id: str) -> None:
        """Unregisters a policy by ID."""
        if policy_id not in self._policies:
            raise ApprovalNotFoundError(f"Approval policy '{policy_id}' not found.")
        del self._policies[policy_id]

    def exists(self, policy_id: str) -> bool:
        """Returns True if policy_id is registered."""
        return policy_id in self._policies

    def lookup(self, policy_id: str) -> ApprovalPolicy:
        """Retrieves and instantiates an ApprovalPolicy by ID."""
        if policy_id not in self._policies:
            raise ApprovalNotFoundError(f"Approval policy '{policy_id}' not found.")
        target = self._policies[policy_id]

        if isinstance(target, ApprovalPolicy):
            return target
        elif isinstance(target, type) and issubclass(target, ApprovalPolicy):
            return target()
        elif callable(target):
            res = target()
            if isinstance(res, ApprovalPolicy):
                return res
            raise ApprovalRegistryError(
                f"Factory for policy '{policy_id}' did not return ApprovalPolicy."
            )
        raise ApprovalRegistryError(
            f"Invalid registration type for policy '{policy_id}'."
        )

    def list(self) -> List[str]:
        """Lists IDs of registered policies."""
        return list(self._policies.keys())

    def clear(self) -> None:
        """Clears all registered policies."""
        self._policies.clear()
