from typing import Optional
from app.integrations.adapters.auth.auth_adapter import JWTAuthAdapter
from app.integrations.adapters.database.database_adapter import PostgresDatabaseAdapter
from app.integrations.adapters.llm.llm_adapter import GeminiLLMAdapter
from app.integrations.adapters.messaging.messaging_adapter import WebhookMessagingAdapter
from app.integrations.adapters.observability.observability_adapter import PrometheusObservabilityAdapter
from app.integrations.adapters.scheduler.scheduler_adapter import CronSchedulerAdapter
from app.integrations.adapters.storage.storage_adapter import FilesystemStorageAdapter
from app.integrations.adapters.vector.vector_adapter import InMemoryVectorAdapter
from app.integrations.provider import IntegrationProvider


class IntegrationFactory:
    """Factory creating reference integration adapter instances."""

    @staticmethod
    def create_reference_adapters() -> list[IntegrationProvider]:
        return [
            FilesystemStorageAdapter(),
            InMemoryVectorAdapter(),
            GeminiLLMAdapter(),
            JWTAuthAdapter(),
            PostgresDatabaseAdapter(),
            PrometheusObservabilityAdapter(),
            WebhookMessagingAdapter(),
            CronSchedulerAdapter(),
        ]
