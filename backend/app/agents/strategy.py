from enum import Enum


class PlanningStrategy(str, Enum):
    """Strategies for decomposing tasks into execution plans."""

    DAG_DECOMPOSITION = "dag_decomposition"
    HIERARCHICAL = "hierarchical"
    LINEAR = "linear"


class DelegationStrategy(str, Enum):
    """Strategies for delegating tasks to worker agents."""

    ROUND_ROBIN = "round_robin"
    PRIORITY = "priority"
    CAPABILITY_BASED = "capability_based"
    COST_OPTIMIZED = "cost_optimized"


class SchedulingStrategy(str, Enum):
    """Strategies for dispatching queued tasks."""

    FIFO = "fifo"
    PRIORITY_FIRST = "priority_first"
    CAPACITY_LOAD = "capacity_load"
