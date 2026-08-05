from pydantic import BaseModel


class ExecutionPolicy(BaseModel):
    """Configuration rules controlling graph execution behavior."""

    stop_on_error: bool = True
    continue_on_warning: bool = True
    allow_cycles: bool = False
    max_depth: int = 50
    max_execution_time: float = 60.0
    collect_metrics: bool = True
    emit_events: bool = True
