from pydantic import BaseModel


class ToolCapabilities(BaseModel):
    """Capability flags defining supported execution features of a tool."""

    supports_async: bool = True
    supports_streaming: bool = False
    supports_batch: bool = True
    supports_pipeline: bool = True
    supports_chain: bool = True
