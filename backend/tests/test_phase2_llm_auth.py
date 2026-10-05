import pytest
from app.integrations.adapters.llm.openai_adapter import OpenAILLMAdapter
from app.integrations.adapters.llm.anthropic_adapter import AnthropicLLMAdapter
from app.integrations.adapters.llm.ollama_adapter import OllamaLLMAdapter
from app.integrations.adapters.llm.llm_adapter import GeminiLLMAdapter
from app.integrations.adapters.auth.oauth2_adapter import OAuth2AuthAdapter
from app.integrations.adapters.auth.auth0_adapter import Auth0Adapter
from app.integrations.adapters.auth.keycloak_adapter import KeycloakAdapter
from app.integrations.adapters.auth.auth_adapter import JWTAuthAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.status import IntegrationStatus


@pytest.mark.asyncio
async def test_llm_adapter_provider_ids_and_defaults():
    openai = OpenAILLMAdapter()
    anthropic = AnthropicLLMAdapter()
    ollama = OllamaLLMAdapter()
    gemini = GeminiLLMAdapter()

    assert openai.provider_id == "llm.openai"
    assert anthropic.provider_id == "llm.anthropic"
    assert ollama.provider_id == "llm.ollama"
    assert gemini.provider_id == "llm.gemini"


@pytest.mark.asyncio
async def test_auth_adapter_provider_ids_and_defaults():
    oauth2 = OAuth2AuthAdapter()
    auth0 = Auth0Adapter()
    keycloak = KeycloakAdapter()
    jwt = JWTAuthAdapter()

    assert oauth2.provider_id == "auth.oauth2"
    assert auth0.provider_id == "auth.auth0"
    assert keycloak.provider_id == "auth.keycloak"
    assert jwt.provider_id == "auth.jwt"


@pytest.mark.asyncio
async def test_gemini_and_jwt_reference_operations():
    gemini = GeminiLLMAdapter()
    await gemini.initialize()
    resp = await gemini.generate_response("Hello test")
    assert "Gemini" in resp

    jwt = JWTAuthAdapter()
    await jwt.initialize()
    auth_data = await jwt.authenticate_token("mock_token")
    assert auth_data.get("token_valid") is True


@pytest.mark.asyncio
async def test_initialization_safety_without_secrets():
    ctx = IntegrationContext()

    openai = OpenAILLMAdapter()
    await openai.initialize(ctx)
    report = await openai.check_health()
    assert report.is_healthy is False

    auth0 = Auth0Adapter()
    await auth0.initialize(ctx)
    report_auth = await auth0.check_health()
    assert report_auth.is_healthy is False
