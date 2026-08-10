"""Hooks (Re-exported from consolidated telemetry module)."""

from app.integrations.telemetry import BeforeProviderConnectHook, AfterProviderFailoverHook

__all__ = ["BeforeProviderConnectHook", "AfterProviderFailoverHook"]
