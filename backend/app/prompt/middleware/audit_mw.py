import logging
from typing import Awaitable, Callable

from app.prompt.contracts import PromptRequest
from app.prompt.middleware.base import PromptMiddleware
from app.prompt.result import PromptResult

logger = logging.getLogger("app.prompt.middleware.audit")


class AuditMiddleware(PromptMiddleware):
    """Pipeline middleware stage auditing prompt requests and completion status."""

    async def process(
        self,
        request: PromptRequest,
        call_next: Callable[[PromptRequest], Awaitable[PromptResult]],
    ) -> PromptResult:
        logger.info(
            f"Auditing prompt rendering for template '{request.template_id}' (Revision: {request.revision_id or 'v1'})"
        )
        result = await call_next(request)
        logger.info(
            f"Prompt rendering completed for template '{request.template_id}' "
            f"[Status: {result.execution_status}, Chars: {result.metrics.rendered_size_chars}, Tokens: {result.metrics.token_estimate}]"
        )
        return result
