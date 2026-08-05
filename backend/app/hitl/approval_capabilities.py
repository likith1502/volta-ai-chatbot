from pydantic import BaseModel


class ApprovalCapabilities(BaseModel):
    """Capabilities supported by an approval handler or system subsystem."""

    supports_escalation: bool = True
    supports_parallel_review: bool = False
    supports_timeout: bool = True
    supports_reassignment: bool = True
    supports_delegation: bool = True
    supports_quorum: bool = False
    supports_checkpoint_resume: bool = True
    supports_audit: bool = True
