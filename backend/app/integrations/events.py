from pydantic import BaseModel


class ProviderRegisteredEvent(BaseModel):
    provider_id: str
    category: str


class ProviderFailedEvent(BaseModel):
    provider_id: str
    error_message: str


class FailoverTriggeredEvent(BaseModel):
    category: str
    failed_provider_id: str
    active_provider_id: str
