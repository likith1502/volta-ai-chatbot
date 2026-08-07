from enum import Enum
from pydantic import BaseModel, Field


class IntegrationCapability(str, Enum):
    """Categories of integration capabilities."""

    STORAGE = "storage"
    VECTOR = "vector"
    LLM = "llm"
    AUTH = "auth"
    DATABASE = "database"
    OBSERVABILITY = "observability"
    MESSAGING = "messaging"
    SEARCH = "search"
    SCHEDULER = "scheduler"
    SECRETS = "secrets"


class CapabilityFeatureFlags(BaseModel):
    """Boolean feature flags describing specific capabilities of an adapter."""

    supports_streaming: bool = True
    supports_batch: bool = True
    supports_transactions: bool = False
    supports_async: bool = True
    supports_tls: bool = True
