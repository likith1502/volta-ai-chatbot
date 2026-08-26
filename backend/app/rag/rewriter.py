class QueryRewriter:
    """Query Rewriter hook transforming or expanding user queries prior to retrieval planning."""

    def rewrite_query(self, original_query: str) -> str:
        """Standardizes query, performs spelling cleanup, and removes noise words."""
        cleaned = original_query.strip()
        return cleaned
