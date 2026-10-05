import pytest
import uuid
from app.graph_runtime.contracts import GraphExecutePayload
from app.graph_runtime.cursor import GraphCursor
from app.graph_runtime.dependency import GraphDependencyManager
from app.graph_runtime.execution_plan import GraphExecutionPlan
from app.graph_runtime.factory import GraphRuntimeFactory
from app.graph_runtime.manager import GraphRuntimeManager
from app.graph_runtime.planner import GraphPlanner
from app.graph_runtime.policy import GraphRuntimePolicy
from app.graph_runtime.retry import BackoffStrategy, RetryPolicy
from app.graph_runtime.scheduler import GraphScheduler
from app.graph_runtime.session import GraphRuntimeSession
from app.graph_runtime.state import GraphRuntimeState
from app.graph_runtime.timeout import TimeoutPolicy


@pytest.mark.asyncio
async def test_planner_and_execution_plan():
    planner = GraphPlanner()
    plan = planner.plan_execution(workflow_id="test_wf")

    assert plan.workflow_id == "test_wf"
    assert len(plan.execution_order) >= 4
    assert plan.execution_order[0] == "START"
    assert "END" in plan.execution_order

    res = planner.evaluate_plan(plan)
    assert res.is_valid is True
    assert res.estimated_steps >= 4


@pytest.mark.asyncio
async def test_scheduler_and_cursor():
    scheduler = GraphScheduler()
    plan = GraphExecutionPlan(workflow_id="wf1", execution_order=["START", "step1", "step2", "END"])
    cursor = GraphCursor()

    next_node = scheduler.schedule_next(plan, cursor)
    assert next_node == "step1"

    cursor.advance_to("step1")
    assert cursor.current_node == "step1"
    assert cursor.parent_node == "START"

    next_node2 = scheduler.schedule_next(plan, cursor)
    assert next_node2 == "step2"


@pytest.mark.asyncio
async def test_retry_policy_and_timeout_policy():
    retry_pol = RetryPolicy(max_retries=3, initial_delay_seconds=1.0, backoff_strategy=BackoffStrategy.EXPONENTIAL)
    d1 = retry_pol.evaluate(attempt=0)
    assert d1.should_retry is True
    assert d1.delay_seconds == 1.0

    d2 = retry_pol.evaluate(attempt=1)
    assert d2.should_retry is True
    assert d2.delay_seconds == 2.0

    d3 = retry_pol.evaluate(attempt=3)
    assert d3.should_retry is False

    timeout_pol = TimeoutPolicy(node_timeout_seconds=5.0)
    assert timeout_pol.node_timeout_seconds == 5.0


@pytest.mark.asyncio
async def test_graph_runtime_manager_execution():
    manager = GraphRuntimeManager()
    payload = GraphExecutePayload(workflow_id="unit_test_workflow", inputs={"test": True})

    result = await manager.execute_graph(payload)
    assert result.success is True
    assert result.status == GraphRuntimeState.COMPLETED
    assert len(result.visited_nodes) >= 4
    assert result.trace is not None
    assert len(result.trace.steps) >= 4
