from app.graph_runtime.exceptions import GraphPlanningError
from app.graph_runtime.execution_plan import GraphExecutionPlan


class GraphRuntimeValidator:
    """Validates execution DAG plans and node input context before execution."""

    def validate_plan(self, plan: GraphExecutionPlan) -> bool:
        if not plan or not plan.execution_order:
            raise GraphPlanningError("GraphExecutionPlan must contain at least one execution node.")
        return True
