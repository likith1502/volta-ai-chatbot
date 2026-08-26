import pytest
import uuid
from app.tools.builtin.calculator_tool import CalculatorTool
from app.tools.builtin.datetime_tool import DatetimeTool
from app.tools.builtin.echo_tool import EchoTool
from app.tools.builtin.uuid_tool import UUIDTool
from app.tools.chain import ToolChain, ToolChainStep
from app.tools.contracts import ToolExecutePayload
from app.tools.discovery import ToolDiscoveryService
from app.tools.executor import ToolExecutor
from app.tools.factory import ToolFactory
from app.tools.filter import ToolFilter
from app.tools.inmemory_repository import InMemoryToolRepository
from app.tools.manager import ToolManager
from app.tools.manifest import ToolManifest
from app.tools.permission import ToolPermission
from app.tools.pipeline import ToolPipeline
from app.tools.registry import ToolRegistry
from app.tools.request import ToolRequest
from app.tools.type import ToolType
from app.tools.validator import ToolValidator


@pytest.mark.asyncio
async def test_builtin_tools_execution():
    echo = EchoTool()
    calc = CalculatorTool()
    dt_tool = DatetimeTool()
    uuid_tool = UUIDTool()

    # 1. EchoTool
    res_echo = await echo.execute(ToolRequest(tool_name="echo", arguments={"message": "hello"}))
    assert res_echo.success is True
    assert res_echo.output["echo"] == "hello"

    # 2. CalculatorTool (add)
    res_calc = await calc.execute(ToolRequest(tool_name="calculator", arguments={"a": 5, "b": 10, "operation": "add"}))
    assert res_calc.success is True
    assert res_calc.output["result"] == 15.0

    # 3. CalculatorTool (divide by zero)
    res_div0 = await calc.execute(ToolRequest(tool_name="calculator", arguments={"a": 5, "b": 0, "operation": "divide"}))
    assert res_div0.success is False
    assert len(res_div0.errors) > 0

    # 4. DatetimeTool
    res_dt = await dt_tool.execute(ToolRequest(tool_name="datetime", arguments={}))
    assert res_dt.success is True
    assert "utc_timestamp" in res_dt.output

    # 5. UUIDTool
    res_uuid = await uuid_tool.execute(ToolRequest(tool_name="uuid", arguments={}))
    assert res_uuid.success is True
    assert "uuid" in res_uuid.output


@pytest.mark.asyncio
async def test_tool_repository_and_discovery():
    repo = await ToolFactory.create_default_repository()
    discovery = ToolDiscoveryService(repo)

    manifests = await discovery.find_tools(supports_async=True)
    assert len(manifests) == 4

    math_tools = await discovery.find_tools(permission=ToolPermission.ALLOW)
    assert len(math_tools) == 4


@pytest.mark.asyncio
async def test_tool_manager_and_pipeline():
    manager = ToolManager()
    await manager.initialize()

    # Execute single
    payload = ToolExecutePayload(tool_name="echo", arguments={"message": "test pipeline"})
    res = await manager.execute_tool(payload)
    assert res.success is True
    assert res.output["echo"] == "test pipeline"

    # Execute pipeline
    pipe_res = await manager.execute_pipeline(payload)
    assert pipe_res.success is True
    assert "Validation" in pipe_res.successful_steps
    assert "Events" in pipe_res.successful_steps


@pytest.mark.asyncio
async def test_tool_chain_execution():
    manager = ToolManager()
    await manager.initialize()

    chain = ToolChain(
        steps=[
            ToolChainStep(step_id="s1", tool_name="calculator", arguments={"a": 10, "b": 2, "operation": "multiply"}),
            ToolChainStep(step_id="s2", tool_name="echo", arguments={"message": "chain complete"}),
        ]
    )

    chain_res = await manager.execute_chain(chain)
    assert chain_res.success is True
    assert chain_res.completed_steps == 2
    assert chain_res.final_output["echo"] == "chain complete"


@pytest.mark.asyncio
async def test_tool_schema_and_discovery_query():
    manager = ToolManager()
    await manager.initialize()

    manifest = await manager.get_manifest("calculator")
    assert manifest.schema_spec is not None
    assert manifest.schema_spec.name == "calculator"
    assert manifest.schema_spec.input_schema["type"] == "object"

    tools = await manager.discovery.find_tools(supports_async=True)
    assert len(tools) == 4
