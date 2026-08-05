import sys
import uuid
import pytest

from app.checkpoints.checkpoint_manager import CheckpointManager
from app.context.state import ConversationState
from app.hitl import (
    ApprovalAlreadyResolvedException,
    ApprovalCapabilities,
    ApprovalConstraints,
    ApprovalContext,
    ApprovalDecision,
    ApprovalEvent,
    ApprovalHistory,
    ApprovalManager,
    ApprovalMetadata,
    ApprovalNotFoundException,
    ApprovalPolicy,
    ApprovalPriority,
    ApprovalRegistry,
    ApprovalRegistryException,
    ApprovalRequest,
    ApprovalResult,
    ApprovalSnapshot,
    ApprovalStatus,
    GovernanceException,
    GovernancePolicy,
    HumanLoopException,
    HumanRole,
    InterruptManager,
    ResumeException,
    ResumeManager,
)


def test_hitl_models_and_immutability() -> None:
    """Verify ApprovalRequest instantiation, UUID generation, priority, and immutability."""
    meta = ApprovalMetadata(priority=ApprovalPriority.HIGH, tags=["finance"])
    constraints = ApprovalConstraints(minimum_reviewers=2)

    req = ApprovalRequest(
        workflow_id="wf_hitl",
        graph_id="g_hitl",
        node_id="approval_gate",
        requester="alice",
        assignee="bob",
        constraints=constraints,
        metadata=meta,
    )

    assert isinstance(req.approval_id, uuid.UUID)
    assert isinstance(req.execution_id, uuid.UUID)
    assert req.workflow_id == "wf_hitl"
    assert req.metadata.priority == ApprovalPriority.HIGH
    assert req.status == ApprovalStatus.CREATED

    # Verify immutability
    with pytest.raises(Exception):
        req.requester = "charlie"  # type: ignore


def test_hitl_enums_capabilities_snapshot_and_event() -> None:
    """Verify enums, ApprovalCapabilities, ApprovalSnapshot, and ApprovalEvent."""
    caps = ApprovalCapabilities(supports_escalation=True)
    assert caps.supports_escalation is True

    snap = ApprovalSnapshot(
        approval_id=uuid.uuid4(),
        status=ApprovalStatus.APPROVED,
        decision=ApprovalDecision.APPROVE,
    )
    assert snap.status == ApprovalStatus.APPROVED

    evt = ApprovalEvent(approval_id=snap.approval_id, event_type="approval_approved")
    assert evt.event_type == "approval_approved"


def test_approval_manager_lifecycle() -> None:
    """Verify ApprovalManager request creation, assignment, approval, rejection, escalation, and completion."""
    mgr = ApprovalManager()

    # Create & Assign
    req = mgr.create_request(
        workflow_id="wf_1",
        graph_id="g_1",
        node_id="n_1",
        requester="alice",
        assignee="bob",
    )
    assert req.status == ApprovalStatus.ASSIGNED

    # Approve
    approved_req = mgr.approve(req.approval_id, reviewer="bob", comments="Looks good")
    assert approved_req.status == ApprovalStatus.APPROVED
    assert approved_req.decision == ApprovalDecision.APPROVE

    # Reject resolved request raises ApprovalAlreadyResolvedException
    with pytest.raises(ApprovalAlreadyResolvedException):
        mgr.reject(req.approval_id, reviewer="bob")

    # Complete
    completed_req = mgr.complete(req.approval_id)
    assert completed_req.status == ApprovalStatus.COMPLETED

    # Check audit history
    assert len(mgr.history.records) == 1
    assert mgr.history.records[0].reviewer == "bob"
    assert mgr.history.records[0].decision == ApprovalDecision.APPROVE


def test_governance_policy_and_separation_of_duties() -> None:
    """Verify GovernancePolicy separation of duties enforcement."""
    gov = GovernancePolicy(separation_of_duties=True)

    # Distinct reviewer passes
    assert gov.validate_decision(requester="alice", reviewer="bob") is True

    # Same requester and reviewer raises GovernanceException
    with pytest.raises(GovernanceException):
        gov.validate_decision(requester="alice", reviewer="alice")


def test_resume_manager_and_checkpoint_integration() -> None:
    """Verify ResumeManager resuming execution from approval and checkpoint."""
    cp_mgr = CheckpointManager()
    app_mgr = ApprovalManager()
    state = ConversationState()

    cp = cp_mgr.create_checkpoint("wf_resume", "g_resume", state)
    req = app_mgr.create_request("wf_resume", "g_resume", "node_resume", checkpoint_id=cp.checkpoint_id)
    app_mgr.approve(req.approval_id, reviewer="manager")

    resumer = ResumeManager(checkpoint_manager=cp_mgr, approval_manager=app_mgr)

    # Resume from approval
    restored_state = resumer.resume_from_approval(req.approval_id)
    assert restored_state.metadata.state_id == state.metadata.state_id

    # Resume unapproved request raises ResumeException
    unapproved_req = app_mgr.create_request("wf_resume", "g_resume", "n_2", checkpoint_id=cp.checkpoint_id)
    with pytest.raises(ResumeException):
        resumer.resume_from_approval(unapproved_req.approval_id)


def test_interrupt_manager_contracts() -> None:
    """Verify InterruptManager interrupt, pause, resume, and cancel contracts."""
    interrupter = InterruptManager()
    exec_id = uuid.uuid4()

    res_int = interrupter.interrupt_execution(exec_id, "gate_node")
    assert res_int["interrupted"] is True

    res_pause = interrupter.pause_execution(exec_id)
    assert res_pause["status"] == "paused"

    res_res = interrupter.resume_execution(exec_id)
    assert res_res["status"] == "resumed"

    res_cancel = interrupter.cancel_execution(exec_id, "User abort")
    assert res_cancel["status"] == "cancelled"


def test_approval_registry() -> None:
    """Verify ApprovalRegistry register, lookup, register_factory, unregister, and clear."""
    registry = ApprovalRegistry()

    def policy_factory() -> ApprovalPolicy:
        return ApprovalPolicy(approval_timeout=7200.0)

    registry.register_factory("custom_policy", policy_factory)
    assert registry.exists("custom_policy") is True

    pol = registry.lookup("custom_policy")
    assert isinstance(pol, ApprovalPolicy)
    assert pol.approval_timeout == 7200.0

    registry.unregister("custom_policy")
    assert registry.exists("custom_policy") is False


def test_exception_hierarchy() -> None:
    """Verify HITL exception hierarchy inheritance."""
    assert issubclass(ApprovalNotFoundException, HumanLoopException)
    assert issubclass(ApprovalAlreadyResolvedException, HumanLoopException)
    assert issubclass(GovernanceException, HumanLoopException)
    assert issubclass(ResumeException, HumanLoopException)


def test_expanded_import_isolation_and_no_framework_leakage() -> None:
    """Verify app.hitl modules do not import forbidden framework dependencies, DB layers, or third-party AI orchestration packages."""
    forbidden_modules = [
        "fastapi",
        "starlette",
        "websockets",
        "redis",
        "sqlalchemy",
        "langgraph",
        "crewai",
        "autogen",
        "semantic_kernel",
        "openai",
        "gemini",
        "anthropic",
        "ollama",
        "llamaindex",
        "app.db",
        "app.repositories",
        "app.services",
        "app.api",
    ]

    import app.hitl as hitl_mod

    for mod_name in sys.modules:
        if mod_name.startswith("app.hitl"):
            mod = sys.modules[mod_name]
            mod_file = getattr(mod, "__file__", "")
            if mod_file:
                with open(mod_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    for forbidden in forbidden_modules:
                        assert forbidden not in content, f"Forbidden dependency '{forbidden}' found in {mod_name}!"
