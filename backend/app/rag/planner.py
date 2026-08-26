import logging
from typing import Any, Optional

from app.rag.plan import RetrievalPlan

logger = logging.getLogger("app.rag.planner")


class RetrievalPlanner:
    """Generates structured RetrievalPlan from user query and retrieval constraints."""

    def create_plan(
        self,
        query: str,
        strategy: str = "vector",
        top_k: int = 5,
        reranker: str = "cosine",
        filters: Optional[dict[str, Any]] = None,
    ) -> RetrievalPlan:
        plan = RetrievalPlan(
            query=query,
            strategy=strategy,
            top_k=top_k,
            reranker=reranker,
            filters=filters or {},
        )
        logger.info(
            f"RetrievalPlanner generated plan '{plan.plan_id}' using strategy '{strategy}' and top_k={top_k}"
        )
        return plan
