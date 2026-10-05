import pytest
import uuid
from app.prompt.analytics import PromptAnalyticsManager
from app.prompt.analyzer import PromptQualityAnalyzer
from app.prompt.benchmark import PromptBenchmarkRunner
from app.prompt.chain import PromptChain, PromptStep
from app.prompt.compiler import PromptCompiler
from app.prompt.contracts import PromptRequest
from app.prompt.cost import PromptCostEstimator
from app.prompt.execution_store import InMemoryPromptExecutionStore, PromptSnapshot
from app.prompt.factory import PromptFactory
from app.prompt.health import PromptHealthManager
from app.prompt.manager import PromptManager
from app.prompt.processors import PromptLinter, PromptOptimizer, PromptRenderer, PromptValidator
from app.prompt.profile import PromptProfile
from app.prompt.registry import PromptRegistry
from app.prompt.repository import InMemoryPromptRepository
from app.prompt.security import PromptSecurityPolicy
from app.prompt.serializer import PromptSerializer
from app.prompt.templates.chat_template import ChatPromptTemplate
from app.prompt.variable_provider import DefaultVariableProvider


@pytest.mark.asyncio
async def test_prompt_template_and_renderer():
    template = ChatPromptTemplate(
        template_id="test_template_v1",
        system_instruction="You are assistant for {user_name}.",
    )
    template.add_variable(name="user_name", required=True)
    template.add_variable(name="destination", required=True)
    template.add_message(role="user", content_template="Take me to {destination}.")

    renderer = PromptRenderer()
    resp = renderer.render(
        template_id="test_template_v1",
        revision_id="v1",
        messages=template.messages,
        variables={"user_name": "Likith", "destination": "Airport"},
        system_instruction=template.system_instruction,
    )

    assert resp.template_id == "test_template_v1"
    assert resp.system_prompt == "You are assistant for Likith."
    assert len(resp.messages) == 1
    assert resp.messages[0].content == "Take me to Airport."


@pytest.mark.asyncio
async def test_prompt_repository_and_registry():
    repo = InMemoryPromptRepository()
    registry = PromptRegistry(repository=repo)

    template = PromptFactory.create_system_chat_template()
    await registry.register_template_async(template)

    assert registry.exists_template("system_chat_v1") is True
    looked_up = await registry.lookup_template_async("system_chat_v1")
    assert looked_up.template_id == "system_chat_v1"


@pytest.mark.asyncio
async def test_prompt_chain_contracts():
    chain = PromptChain(
        chain_id="multi_agent_chain_v1",
        display_name="Planner-Retriever-Critic Chain",
        steps=[
            PromptStep(step_id="step1", template_id="planner_v1", output_key="plan"),
            PromptStep(step_id="step2", template_id="critic_v1", input_mapping={"plan": "plan"}),
        ],
    )
    assert len(chain.steps) == 2
    assert chain.steps[0].step_id == "step1"


@pytest.mark.asyncio
async def test_prompt_cost_estimator():
    estimate = PromptCostEstimator.estimate(
        prompt_tokens=1000,
        completion_tokens=200,
        provider="gemini",
        model="gemini-2.5-flash",
    )
    assert estimate.prompt_tokens == 1000
    assert estimate.completion_tokens == 200
    assert estimate.estimated_request_cost_usd > 0.0
    assert estimate.projected_monthly_cost_usd > 0.0


@pytest.mark.asyncio
async def test_prompt_quality_analyzer():
    analyzer = PromptQualityAnalyzer()
    template = PromptFactory.create_mobility_assistant_template()

    report = analyzer.analyze(
        messages=template.messages,
        system_instruction=template.system_instruction,
        variables=template.variables,
    )
    assert report.readability_score > 0.0
    assert report.overall_quality_grade in ["A", "B", "C", "D"]


@pytest.mark.asyncio
async def test_prompt_benchmark_runner():
    manager = PromptManager()
    runner = PromptBenchmarkRunner(prompt_manager=manager)

    req = PromptRequest(
        template_id="mobility_assistant_v1",
        variables={"city_name": "San Francisco"},
    )
    res = await runner.benchmark(req, iterations=3)
    assert res.iterations == 3
    assert res.success_rate_pct == 100.0


@pytest.mark.asyncio
async def test_prompt_analytics_and_variable_provider():
    analytics = PromptAnalyticsManager()
    analytics.record_render("mobility_assistant_v1", 12.5, is_success=True)
    analytics.record_execution("mobility_assistant_v1")

    report = analytics.get_report()
    assert report.total_renders == 1
    assert report.total_executions == 1

    var_provider = DefaultVariableProvider()
    req = PromptRequest(template_id="mobility_assistant_v1", variables={"key": "val"})
    resolved = await var_provider.resolve_variables(req)
    assert resolved["key"] == "val"
