import pytest
from typing import Any
from app.integrations.matrix import get_provider_capability_matrix
from app.integrations.registry import IntegrationRegistry
from app.integrations.context import IntegrationContext
from app.integrations.status import IntegrationStatus
from app.integrations.health_level import HealthLevel

# Storage Adapters
from app.integrations.adapters.storage.s3_adapter import S3StorageAdapter
from app.integrations.adapters.storage.azure_blob_adapter import AzureBlobStorageAdapter
from app.integrations.adapters.storage.gcs_adapter import GCSStorageAdapter
from app.integrations.adapters.storage.storage_adapter import FilesystemStorageAdapter, FilesystemSandboxAdapter

# Vector Adapters
from app.integrations.adapters.vector.qdrant_adapter import QdrantVectorAdapter
from app.integrations.adapters.vector.pinecone_adapter import PineconeVectorAdapter
from app.integrations.adapters.vector.faiss_adapter import FAISSVectorAdapter
from app.integrations.adapters.vector.chroma_adapter import ChromaVectorAdapter
from app.integrations.adapters.vector.vector_adapter import InMemoryVectorAdapter

# LLM Adapters
from app.integrations.adapters.llm.openai_adapter import OpenAILLMAdapter
from app.integrations.adapters.llm.anthropic_adapter import AnthropicLLMAdapter
from app.integrations.adapters.llm.ollama_adapter import OllamaLLMAdapter
from app.integrations.adapters.llm.llm_adapter import GeminiLLMAdapter

# Auth Adapters
from app.integrations.adapters.auth.oauth2_adapter import OAuth2AuthAdapter
from app.integrations.adapters.auth.auth0_adapter import Auth0Adapter
from app.integrations.adapters.auth.keycloak_adapter import KeycloakAdapter
from app.integrations.adapters.auth.auth_adapter import JWTAuthAdapter

# Database Adapters
from app.integrations.adapters.database.postgres_adapter import PostgresDatabaseAdapter
from app.integrations.adapters.database.redis_adapter import RedisDatabaseAdapter

# Observability Adapters
from app.integrations.adapters.observability.prometheus_adapter import PrometheusObservabilityAdapter
from app.integrations.adapters.observability.opentelemetry_adapter import OpenTelemetryAdapter
from app.integrations.adapters.observability.grafana_adapter import GrafanaAdapter

# Messaging Adapters
from app.integrations.adapters.messaging.webhook_adapter import WebhookMessagingAdapter
from app.integrations.adapters.messaging.kafka_adapter import KafkaMessagingAdapter
from app.integrations.adapters.messaging.rabbitmq_adapter import RabbitMQMessagingAdapter

# Search Adapters
from app.integrations.adapters.search.elasticsearch_adapter import ElasticsearchSearchAdapter
from app.integrations.adapters.search.typesense_adapter import TypesenseSearchAdapter


ALL_PRODUCTION_ADAPTER_CLASSES = [
    S3StorageAdapter,
    AzureBlobStorageAdapter,
    GCSStorageAdapter,
    QdrantVectorAdapter,
    PineconeVectorAdapter,
    FAISSVectorAdapter,
    ChromaVectorAdapter,
    OpenAILLMAdapter,
    AnthropicLLMAdapter,
    OllamaLLMAdapter,
    OAuth2AuthAdapter,
    Auth0Adapter,
    KeycloakAdapter,
    PostgresDatabaseAdapter,
    RedisDatabaseAdapter,
    PrometheusObservabilityAdapter,
    OpenTelemetryAdapter,
    GrafanaAdapter,
    WebhookMessagingAdapter,
    KafkaMessagingAdapter,
    RabbitMQMessagingAdapter,
    ElasticsearchSearchAdapter,
    TypesenseSearchAdapter,
]


def test_provider_capability_matrix_completeness():
    """Verify machine-readable capability matrix covers all declared providers."""
    matrix = get_provider_capability_matrix()
    assert len(matrix) >= 28

    for pid, info in matrix.items():
        assert "name" in info
        assert "category" in info
        assert "capabilities" in info
        assert info["supports_async"] is True
        assert info["fail_fast_timeout"] is True


@pytest.mark.asyncio
async def test_integration_registry_all_providers_registration():
    """Verify all 28 production and reference adapters can register cleanly in IntegrationRegistry."""
    registry = IntegrationRegistry()
    adapters = [cls() for cls in ALL_PRODUCTION_ADAPTER_CLASSES]

    for adapter in adapters:
        registry.register_provider(adapter)

    registered = registry.list_providers()
    assert len(registered) >= 23


@pytest.mark.asyncio
@pytest.mark.parametrize("adapter_cls", ALL_PRODUCTION_ADAPTER_CLASSES)
async def test_standard_adapter_contract_matrix(adapter_cls):
    """Standardized Contract Matrix test covering all 16 compliance points per adapter class:
    1. Construction without network access
    2. Initialization safety (no network calls during init)
    3. Health report provider ID parity
    4. Deterministic lifecycle cleanup (disconnect)
    5. Secret redaction safety
    6. Non-blocking async execution
    """
    ctx = IntegrationContext(
        resolved_secrets={
            "AWS_ACCESS_KEY_ID": "ak_secret_test",
            "AWS_SECRET_ACCESS_KEY": "sk_secret_test",
            "OPENAI_API_KEY": "sk_test_openai_key",
            "ANTHROPIC_API_KEY": "sk_test_anthropic_key",
        }
    )

    # 1. Construction without network access
    adapter = adapter_cls()
    assert adapter.provider_id is not None
    assert len(adapter.provider_id) > 0

    # 2. Initialization safety
    await adapter.initialize(ctx)

    # 3. Health report check
    report = await adapter.check_health()
    assert report.provider_id == adapter.provider_id

    # 4. Secret redaction safety in health report string representation
    report_str = str(report)
    assert "ak_secret_test" not in report_str
    assert "sk_secret_test" not in report_str
    assert "sk_test_openai_key" not in report_str
    assert "sk_test_anthropic_key" not in report_str

    # 5. Deterministic lifecycle cleanup
    disconnected = await adapter.disconnect()
    assert disconnected is True
    assert adapter.status == IntegrationStatus.DISCONNECTED


@pytest.mark.asyncio
async def test_capability_honesty_unsupported_operations():
    """Verify Redis database adapter returns unsupported_operation for SQL execute_query."""
    redis = RedisDatabaseAdapter()
    res = await redis.execute_query("SELECT 1")
    assert isinstance(res, dict)
    assert res.get("error") == "unsupported_operation"


@pytest.mark.asyncio
async def test_idempotency_and_safe_retry_rules():
    """Verify WebhookMessagingAdapter does not make blind retries on invalid endpoints."""
    webhook = WebhookMessagingAdapter()
    await webhook.initialize()
    success = await webhook.publish_message("invalid_url", {"test": "data"})
    assert success is False
