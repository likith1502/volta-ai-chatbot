import pytest
from app.integrations.adapters.messaging.webhook_adapter import WebhookMessagingAdapter
from app.integrations.adapters.messaging.kafka_adapter import KafkaMessagingAdapter
from app.integrations.adapters.messaging.rabbitmq_adapter import RabbitMQMessagingAdapter
from app.integrations.adapters.search.elasticsearch_adapter import ElasticsearchSearchAdapter
from app.integrations.adapters.search.typesense_adapter import TypesenseSearchAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.status import IntegrationStatus


@pytest.mark.asyncio
async def test_messaging_adapter_provider_ids_and_defaults():
    webhook = WebhookMessagingAdapter()
    kafka = KafkaMessagingAdapter()
    rabbitmq = RabbitMQMessagingAdapter()

    assert webhook.provider_id == "messaging.webhook"
    assert kafka.provider_id == "messaging.kafka"
    assert rabbitmq.provider_id == "messaging.rabbitmq"


@pytest.mark.asyncio
async def test_search_adapter_provider_ids_and_defaults():
    es = ElasticsearchSearchAdapter()
    typesense = TypesenseSearchAdapter()

    assert es.provider_id == "search.elasticsearch"
    assert typesense.provider_id == "search.typesense"


@pytest.mark.asyncio
async def test_initialization_safety_and_health_without_credentials():
    ctx = IntegrationContext()

    kafka = KafkaMessagingAdapter()
    await kafka.initialize(ctx)
    report_k = await kafka.check_health()
    assert report_k.provider_id == "messaging.kafka"

    es = ElasticsearchSearchAdapter()
    await es.initialize(ctx)
    report_es = await es.check_health()
    assert report_es.provider_id == "search.elasticsearch"
    assert report_es.is_healthy is False


@pytest.mark.asyncio
async def test_resource_cleanup_disconnect():
    webhook = WebhookMessagingAdapter()
    await webhook.disconnect()
    assert webhook.status == IntegrationStatus.DISCONNECTED

    es = ElasticsearchSearchAdapter()
    await es.disconnect()
    assert es.status == IntegrationStatus.DISCONNECTED
