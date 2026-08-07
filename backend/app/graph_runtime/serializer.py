from app.graph_runtime.execution_plan import GraphExecutionPlan
from app.graph_runtime.execution_result import GraphExecutionResult


class GraphRuntimeSerializer:
    """Serializes Graph Execution plans and results into JSON strings."""

    @staticmethod
    def result_to_json(result: GraphExecutionResult) -> str:
        return result.model_dump_json(indent=2)

    @staticmethod
    def plan_to_json(plan: GraphExecutionPlan) -> str:
        return plan.model_dump_json(indent=2)
