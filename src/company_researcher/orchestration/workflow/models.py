"""
Workflow Models Module.

Enums and dataclasses for workflow orchestration.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from ...utils import utc_now


class NodeType(str, Enum):
    """Types of workflow nodes."""

    AGENT = "agent"  # Agent execution node
    ROUTER = "router"  # Conditional routing
    PARALLEL = "parallel"  # Parallel execution
    SEQUENCE = "sequence"  # Sequential execution
    TRANSFORM = "transform"  # Data transformation
    CHECKPOINT = "checkpoint"  # State checkpoint
    END = "end"  # End node


class ExecutionStatus(str, Enum):
    """Execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class RouteCondition(str, Enum):
    """Route condition types."""

    ALWAYS = "always"
    IF_DATA_PRESENT = "if_data_present"
    IF_QUALITY_HIGH = "if_quality_high"
    IF_COST_UNDER = "if_cost_under"
    CUSTOM = "custom"


@dataclass
class NodeConfig:
    """Configuration for a workflow node."""

    name: str
    node_type: NodeType
    handler: Optional[Callable] = None
    children: List[str] = field(default_factory=list)
    retry_count: int = 2
    timeout: int = 300  # seconds
    condition: Optional[RouteCondition] = None
    condition_value: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of node execution."""

    node_name: str
    status: ExecutionStatus
    output: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    retries: int = 0
    timestamp: datetime = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "node": self.node_name,
            "status": self.status.value,
            "output_type": type(self.output).__name__ if self.output else None,
            "error": self.error,
            "duration_ms": round(self.duration_ms, 2),
            "retries": self.retries,
        }


@dataclass
class WorkflowState:
    """State of workflow execution."""

    workflow_id: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    current_node: Optional[str] = None
    completed_nodes: List[str] = field(default_factory=list)
    failed_nodes: List[str] = field(default_factory=list)
    results: Dict[str, ExecutionResult] = field(default_factory=dict)
    data: Dict[str, Any] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_cost: float = 0.0

    @property
    def duration_seconds(self) -> float:
        """Calculate duration in seconds."""
        if not self.start_time:
            return 0
        end = self.end_time or utc_now()
        return (end - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "current_node": self.current_node,
            "completed": len(self.completed_nodes),
            "failed": len(self.failed_nodes),
            "duration_seconds": round(self.duration_seconds, 2),
            "total_cost": round(self.total_cost, 4),
        }
