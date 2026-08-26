from pydantic import BaseModel


class DocumentAddedEvent(BaseModel):
    document_id: str
    title: str


class DocumentIngestedEvent(BaseModel):
    document_id: str
    job_id: str
    chunks_count: int


class QueryExecutedEvent(BaseModel):
    query: str
    citations_count: int
    latency_ms: float
