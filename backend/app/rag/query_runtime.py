import time
import logging
from typing import Optional
from app.rag.budget import RetrievalBudget
from app.rag.cache import CacheProvider, InMemoryCacheProvider
from app.rag.context import RAGContext
from app.rag.context_builder import RAGContextBuilder
from app.rag.embedding_registry import EmbeddingRegistry
from app.rag.explanation import RetrievalExplanation
from app.rag.planner import RetrievalPlanner
from app.rag.repository import DocumentRepository
from app.rag.reranker import DocumentReranker
from app.rag.retriever import DocumentRetriever
from app.rag.rewriter import QueryRewriter
from app.rag.trace import RetrievalTrace
from app.rag.vector_repository import VectorRepository

logger = logging.getLogger("app.rag.query_runtime")


class QueryRuntime:
    """Orchestrates RAG query pipeline: Rewrite ➔ Plan ➔ Retrieve ➔ Rerank ➔ Context ➔ Citations."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        vector_repository: VectorRepository,
        embedding_registry: Optional[EmbeddingRegistry] = None,
        cache: Optional[CacheProvider] = None,
    ) -> None:
        self.document_repository = document_repository
        self.vector_repository = vector_repository
        self.embedding_registry = embedding_registry or EmbeddingRegistry()
        self.cache = cache or InMemoryCacheProvider()

        self.rewriter = QueryRewriter()
        self.planner = RetrievalPlanner()
        self.retriever = DocumentRetriever(document_repository, vector_repository, self.embedding_registry)
        self.reranker = DocumentReranker()
        self.context_builder = RAGContextBuilder(document_repository)

    async def execute_query(
        self,
        query: str,
        top_k: int = 5,
        strategy: str = "vector",
        reranker: str = "cosine",
        budget: Optional[RetrievalBudget] = None,
    ) -> tuple[RAGContext, RetrievalTrace, RetrievalExplanation]:
        """Executes query pipeline and returns assembled RAGContext, RetrievalTrace, and RetrievalExplanation."""
        t0 = time.perf_counter()
        trace = RetrievalTrace(query=query)
        b_limit = budget or RetrievalBudget()

        # Check cache
        cache_key = f"rag_query_{query}_{top_k}_{strategy}_{reranker}"
        cached_res = self.cache.get(cache_key)
        if cached_res:
            logger.info(f"QueryRuntime cache hit for query '{query}'")
            return cached_res

        # 1. Rewrite
        t_rw = time.perf_counter()
        clean_query = self.rewriter.rewrite_query(query)
        dt_rw = (time.perf_counter() - t_rw) * 1000.0
        trace.add_step("query_rewrite", dt_rw, {"rewritten_query": clean_query})

        # 2. Plan
        t_pl = time.perf_counter()
        plan = self.planner.create_plan(clean_query, strategy=strategy, top_k=top_k, reranker=reranker)
        dt_pl = (time.perf_counter() - t_pl) * 1000.0
        trace.add_step("retrieval_plan", dt_pl, plan.model_dump())

        # 3. Retrieve
        t_ret = time.perf_counter()
        retrieved_chunks = await self.retriever.retrieve(plan)
        dt_ret = (time.perf_counter() - t_ret) * 1000.0
        trace.add_step("retrieval", dt_ret, {"chunks_retrieved": len(retrieved_chunks)})

        # 4. Rerank
        t_rr = time.perf_counter()
        ranked_chunks = self.reranker.rerank(clean_query, retrieved_chunks, strategy=reranker)
        dt_rr = (time.perf_counter() - t_rr) * 1000.0
        trace.add_step("rerank", dt_rr, {"strategy": reranker, "chunks_ranked": len(ranked_chunks)})

        # 5. Build Context & Citations
        t_ctx = time.perf_counter()
        context = self.context_builder.build_context(clean_query, ranked_chunks, b_limit)
        dt_ctx = (time.perf_counter() - t_ctx) * 1000.0
        trace.add_step("context_assembly", dt_ctx, {"citations_count": len(context.citations)})

        explanation = RetrievalExplanation(
            query=query,
            selected_chunk_ids=[c.chunk_id for c in context.citations],
            reranker=reranker,
            reason=f"Top-{len(context.citations)} similarity search via '{strategy}' and '{reranker}' reranking.",
            average_score=round(sum(context.scores) / len(context.scores), 4) if context.scores else 1.0,
        )

        result_tuple = (context, trace, explanation)
        self.cache.set(cache_key, result_tuple)
        return result_tuple
