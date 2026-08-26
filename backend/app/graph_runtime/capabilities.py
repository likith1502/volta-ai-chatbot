from pydantic import BaseModel


class GraphRuntimeCapabilities(BaseModel):
    """Capabilities supported by Graph Runtime Engine."""

    supports_dag_planning: bool = True
    supports_conditional_routing: bool = True
    supports_parallel_nodes: bool = True
    supports_auto_checkpointing: bool = True
    supports_hitl_interrupts: bool = True
    supports_realtime_streaming: bool = True
