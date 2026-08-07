from enum import Enum
from pydantic import BaseModel, Field


class AgentPermission(str, Enum):
    """Specific permission capabilities granted to an agent."""

    CAN_DELEGATE = "can_delegate"
    CAN_APPROVE = "can_approve"
    CAN_EXECUTE_TOOLS = "can_execute_tools"
    CAN_ACCESS_MEMORY = "can_access_memory"
    CAN_RENDER_PROMPTS = "can_render_prompts"
    CAN_CREATE_TASKS = "can_create_tasks"
    CAN_SUPERVISE = "can_supervise"


class AgentPermissionSet(BaseModel):
    """Set of permissions governing agent actions."""

    permissions: set[AgentPermission] = Field(
        default_factory=lambda: {
            AgentPermission.CAN_ACCESS_MEMORY,
            AgentPermission.CAN_RENDER_PROMPTS,
        }
    )

    def has_permission(self, permission: AgentPermission) -> bool:
        return permission in self.permissions

    def grant(self, permission: AgentPermission) -> None:
        self.permissions.add(permission)

    def revoke(self, permission: AgentPermission) -> None:
        self.permissions.discard(permission)
