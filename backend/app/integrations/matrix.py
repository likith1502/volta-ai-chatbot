from typing import Any, NamedTuple, Optional


class ProviderCapabilityInfo(NamedTuple):
    provider_id: str
    name: str
    category: str
    sdk_dependency: Optional[str]
    capabilities: list[str]
    supports_async: bool
    fail_fast_timeout: bool


PROVIDER_CAPABILITY_MATRIX: dict[str, dict[str, Any]] = {
    "storage.filesystem": {
        "name": "Local Filesystem Storage Adapter",
        "category": "STORAGE",
        "sdk_dependency": None,
        "capabilities": ["upload", "download", "delete", "list_keys"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "storage.filesystem_sandbox": {
        "name": "Sandbox Filesystem Storage Adapter",
        "category": "STORAGE",
        "sdk_dependency": None,
        "capabilities": ["upload", "download", "delete", "list_keys", "sandbox_isolate"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "storage.s3": {
        "name": "AWS S3 Storage Adapter",
        "category": "STORAGE",
        "sdk_dependency": "boto3",
        "capabilities": ["upload", "download", "delete", "list_keys", "metadata"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "storage.azure_blob": {
        "name": "Azure Blob Storage Adapter",
        "category": "STORAGE",
        "sdk_dependency": "azure-storage-blob",
        "capabilities": ["upload", "download", "delete", "list_keys"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "storage.gcs": {
        "name": "Google Cloud Storage Adapter",
        "category": "STORAGE",
        "sdk_dependency": "google-cloud-storage",
        "capabilities": ["upload", "download", "delete", "list_keys"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "vector.inmemory": {
        "name": "In-Memory Vector DB Adapter",
        "category": "VECTOR",
        "sdk_dependency": None,
        "capabilities": ["upsert_vector", "query_vector"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "vector.qdrant": {
        "name": "Qdrant Vector DB Adapter",
        "category": "VECTOR",
        "sdk_dependency": "qdrant-client",
        "capabilities": ["upsert_vector", "query_vector", "payload_filtering"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "vector.pinecone": {
        "name": "Pinecone Vector DB Adapter",
        "category": "VECTOR",
        "sdk_dependency": "pinecone-client",
        "capabilities": ["upsert_vector", "query_vector", "metadata_filtering"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "vector.faiss": {
        "name": "FAISS Vector DB Adapter",
        "category": "VECTOR",
        "sdk_dependency": "faiss-cpu",
        "capabilities": ["upsert_vector", "query_vector"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "vector.chroma": {
        "name": "Chroma Vector DB Adapter",
        "category": "VECTOR",
        "sdk_dependency": "chromadb",
        "capabilities": ["upsert_vector", "query_vector"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "llm.gemini": {
        "name": "Google Gemini LLM Adapter",
        "category": "LLM",
        "sdk_dependency": None,
        "capabilities": ["generate_response", "system_prompt"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "llm.openai": {
        "name": "OpenAI GPT-4 LLM Adapter",
        "category": "LLM",
        "sdk_dependency": "openai",
        "capabilities": ["generate_response", "system_prompt", "chat_completions"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "llm.anthropic": {
        "name": "Anthropic Claude LLM Adapter",
        "category": "LLM",
        "sdk_dependency": "anthropic",
        "capabilities": ["generate_response", "system_prompt", "messages_api"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "llm.ollama": {
        "name": "Ollama Local LLM Adapter",
        "category": "LLM",
        "sdk_dependency": "httpx",
        "capabilities": ["generate_response", "system_prompt", "local_execution"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "auth.jwt": {
        "name": "JWT Local Authentication Adapter",
        "category": "AUTH",
        "sdk_dependency": None,
        "capabilities": ["authenticate_token", "claims_verification"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "auth.oauth2": {
        "name": "OAuth2 Authentication Adapter",
        "category": "AUTH",
        "sdk_dependency": "httpx",
        "capabilities": ["authenticate_token", "token_introspection"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "auth.auth0": {
        "name": "Auth0 Authentication Adapter",
        "category": "AUTH",
        "sdk_dependency": "pyjwt",
        "capabilities": ["authenticate_token", "jwks_verification"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "auth.keycloak": {
        "name": "Keycloak Identity Adapter",
        "category": "AUTH",
        "sdk_dependency": "pyjwt",
        "capabilities": ["authenticate_token", "realm_jwks_verification"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "database.postgres": {
        "name": "PostgreSQL Async Database Adapter",
        "category": "DATABASE",
        "sdk_dependency": "asyncpg",
        "capabilities": ["execute_query", "connection_pooling", "relational_sql"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "database.redis": {
        "name": "Redis Cache & Key-Value Adapter",
        "category": "DATABASE",
        "sdk_dependency": "redis",
        "capabilities": ["get", "set", "delete", "expire", "key_value_caching"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "observability.prometheus": {
        "name": "Prometheus Observability Adapter",
        "category": "OBSERVABILITY",
        "sdk_dependency": "prometheus_client",
        "capabilities": ["record_metric", "counters", "gauges"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "observability.opentelemetry": {
        "name": "OpenTelemetry Collector Adapter",
        "category": "OBSERVABILITY",
        "sdk_dependency": "opentelemetry-api",
        "capabilities": ["record_metric", "distributed_tracing"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "observability.grafana": {
        "name": "Grafana Dashboard Adapter",
        "category": "OBSERVABILITY",
        "sdk_dependency": "httpx",
        "capabilities": ["check_health", "dashboard_annotations"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "messaging.webhook": {
        "name": "HTTP Webhook Messaging Adapter",
        "category": "MESSAGING",
        "sdk_dependency": "httpx",
        "capabilities": ["publish_message", "http_post_dispatch"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "messaging.kafka": {
        "name": "Apache Kafka Event Bus Adapter",
        "category": "MESSAGING",
        "sdk_dependency": "aiokafka",
        "capabilities": ["publish_message", "topic_event_streaming"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "messaging.rabbitmq": {
        "name": "RabbitMQ AMQP Queue Adapter",
        "category": "MESSAGING",
        "sdk_dependency": "aio-pika",
        "capabilities": ["publish_message", "amqp_queue_routing"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "search.elasticsearch": {
        "name": "Elasticsearch Enterprise Search Adapter",
        "category": "SEARCH",
        "sdk_dependency": "elasticsearch",
        "capabilities": ["search", "fulltext_match", "cluster_health"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
    "search.typesense": {
        "name": "Typesense Fast Search Adapter",
        "category": "SEARCH",
        "sdk_dependency": "typesense",
        "capabilities": ["search", "fuzzy_matching"],
        "supports_async": True,
        "fail_fast_timeout": True,
    },
}


def get_provider_capability_matrix() -> dict[str, dict[str, Any]]:
    """Returns machine-readable provider capability matrix."""
    return PROVIDER_CAPABILITY_MATRIX
