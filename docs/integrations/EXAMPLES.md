# VOLTA AI Platform Production Integration Layer Examples

This document outlines configuration and usage examples for all production adapters implemented under `backend/app/integrations/adapters/`.

---

## 1. Storage Adapters

### AWS S3 (`storage.s3`)
```python
from app.integrations.adapters.storage.s3_adapter import S3StorageAdapter
from app.integrations.context import IntegrationContext

context = IntegrationContext(
    resolved_secrets={
        "AWS_ACCESS_KEY_ID": "ak-12345",
        "AWS_SECRET_ACCESS_KEY": "sk-67890",
        "AWS_REGION": "us-east-1",
        "AWS_S3_BUCKET": "my-volta-bucket",
    }
)

adapter = S3StorageAdapter()
await adapter.initialize(context)
await adapter.upload("documents/report.pdf", b"pdf content", metadata={"owner": "alice"})
data = await adapter.download("documents/report.pdf")
```

---

## 2. Vector DB Adapters

### Qdrant (`vector.qdrant`)
```python
from app.integrations.adapters.vector.qdrant_adapter import QdrantVectorAdapter
from app.integrations.context import IntegrationContext

context = IntegrationContext(
    resolved_secrets={
        "QDRANT_HOST": "localhost",
        "QDRANT_PORT": 6333,
        "QDRANT_COLLECTION": "my_vectors",
    }
)

adapter = QdrantVectorAdapter()
await adapter.initialize(context)
await adapter.upsert_vector("v101", [0.1, 0.2, 0.3], {"label": "sample"})
results = await adapter.query_vector([0.1, 0.2, 0.3], top_k=5)
```

---

## 3. LLM Adapters

### OpenAI (`llm.openai`)
```python
from app.integrations.adapters.llm.openai_adapter import OpenAILLMAdapter
from app.integrations.context import IntegrationContext

context = IntegrationContext(
    resolved_secrets={
        "OPENAI_API_KEY": "sk-proj-...",
        "OPENAI_MODEL": "gpt-4o",
    }
)

adapter = OpenAILLMAdapter()
await adapter.initialize(context)
response = await adapter.generate_response("Explain quantum computing in one sentence.")
```

---

## 4. Authentication Adapters

### Auth0 (`auth.auth0`)
```python
from app.integrations.adapters.auth.auth0_adapter import Auth0Adapter
from app.integrations.context import IntegrationContext

context = IntegrationContext(
    resolved_secrets={
        "AUTH0_DOMAIN": "dev-tenant.us.auth0.com",
        "AUTH0_AUDIENCE": "https://api.volta.ai",
    }
)

adapter = Auth0Adapter()
await adapter.initialize(context)
claims = await adapter.authenticate_token("eyJhbGciOiJSUzI1NiI...")
```

---

## 5. Database Adapters

### PostgreSQL (`database.postgres`)
```python
from app.integrations.adapters.database.postgres_adapter import PostgresDatabaseAdapter
from app.integrations.context import IntegrationContext

context = IntegrationContext(
    resolved_secrets={"DATABASE_URL": "postgresql://user:pass@localhost:5432/volta_db"}
)

adapter = PostgresDatabaseAdapter()
await adapter.initialize(context)
rows = await adapter.execute_query("SELECT * FROM users WHERE active = $1", True)
```

### Redis Cache (`database.redis`)
```python
from app.integrations.adapters.database.redis_adapter import RedisDatabaseAdapter
from app.integrations.context import IntegrationContext

context = IntegrationContext(
    resolved_secrets={"REDIS_URL": "redis://localhost:6379/0"}
)

adapter = RedisDatabaseAdapter()
await adapter.initialize(context)
await adapter.set("user:session:101", "active_token", ttl=3600)
val = await adapter.get("user:session:101")
```

---

## 6. Observability Adapters

### Prometheus (`observability.prometheus`)
```python
from app.integrations.adapters.observability.prometheus_adapter import PrometheusObservabilityAdapter

adapter = PrometheusObservabilityAdapter()
await adapter.initialize()
await adapter.record_metric("http_requests_total", 1.0)
```

---

## 7. Messaging Adapters

### Apache Kafka (`messaging.kafka`)
```python
from app.integrations.adapters.messaging.kafka_adapter import KafkaMessagingAdapter
from app.integrations.context import IntegrationContext

context = IntegrationContext(
    resolved_secrets={"KAFKA_BOOTSTRAP_SERVERS": "localhost:9092"}
)

adapter = KafkaMessagingAdapter()
await adapter.initialize(context)
await adapter.publish_message("volta-events", {"event": "user_logged_in", "timestamp": 1700000000})
```

---

## 8. Search Adapters

### Elasticsearch (`search.elasticsearch`)
```python
from app.integrations.adapters.search.elasticsearch_adapter import ElasticsearchSearchAdapter
from app.integrations.context import IntegrationContext

context = IntegrationContext(
    resolved_secrets={"ELASTICSEARCH_HOSTS": "http://localhost:9200"}
)

adapter = ElasticsearchSearchAdapter()
await adapter.initialize(context)
results = await adapter.search("quantum architecture", limit=10)
```
