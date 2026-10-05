"""Hooks (Re-exported from consolidated telemetry module)."""

from app.rag.telemetry import BeforeDocumentIngestHook, AfterQueryRetrievalHook

__all__ = ["BeforeDocumentIngestHook", "AfterQueryRetrievalHook"]
