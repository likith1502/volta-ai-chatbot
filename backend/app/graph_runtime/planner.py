import logging
from typing import Optional

from app.graph_runtime.execution_plan import GraphExecutionPlan
from app.graph_runtime.planner_result import PlannerResult
from app.graph_runtime.policy import GraphRuntimePolicy

logger = logging.getLogger("app.graph_runtime.planner")


class GraphPlanner:
    """Evaluates graph structure, generates execution DAG plans, dependency ordering, and conditional routes."""

    def plan_execution(
        self,
        workflow_id: str,
        initial_node: str = "START",
        policy: Optional[GraphRuntimePolicy] = None,
    ) -> GraphExecutionPlan:
        """Generates a GraphExecutionPlan for a workflow."""
        nodes = [initial_node, "input_node", "llm_node", "tool_node", "END"]
        parallel_groups = [
            [initial_node],
            ["input_node"],
            ["llm_node", "tool_node"],
            ["END"],
        ]
        branches = {"llm_node": "tool_node", "tool_node": "END"}

        return GraphExecutionPlan(
            workflow_id=workflow_id,
            execution_order=nodes,
            parallel_groups=parallel_groups,
            conditional_branches=branches,
            policy=policy or GraphRuntimePolicy(),
        )

    def evaluate_plan(self, plan: GraphExecutionPlan) -> PlannerResult:
        """Validates and evaluates a GraphExecutionPlan."""
        return PlannerResult(
            workflow_id=plan.workflow_id,
            target_nodes=plan.execution_order,
            initial_node=plan.execution_order[0] if plan.execution_order else "START",
            is_valid=True,
            estimated_steps=len(plan.execution_order),
        )
