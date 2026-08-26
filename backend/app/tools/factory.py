import logging

from app.tools.builtin.calculator_tool import CalculatorTool
from app.tools.builtin.datetime_tool import DatetimeTool
from app.tools.builtin.echo_tool import EchoTool
from app.tools.builtin.uuid_tool import UUIDTool
from app.tools.inmemory_repository import InMemoryToolRepository
from app.tools.repository import ToolRepository

logger = logging.getLogger("app.tools.factory")


class ToolFactory:
    """Factory creating ToolRepository instances populated with default in-memory built-in reference tools."""

    @staticmethod
    async def create_default_repository() -> ToolRepository:
        repo = InMemoryToolRepository()
        await repo.register(EchoTool())
        await repo.register(CalculatorTool())
        await repo.register(DatetimeTool())
        await repo.register(UUIDTool())
        logger.info(
            "Constructed InMemoryToolRepository with default reference tools (echo, calculator, datetime, uuid)."
        )
        return repo
