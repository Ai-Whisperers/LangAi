"""
Workflow Orchestration Package.

Advanced workflow orchestration:
- Dynamic routing based on data
- Parallel and sequential execution
- Conditional branching
- Error handling and retries
- State management

Usage:
    from company_researcher.orchestration.workflow import (
        WorkflowEngine,
        NodeConfig,
        NodeType,
        ExecutionStatus,
        create_workflow_engine
    )
"""

from .engine import WorkflowEngine, create_workflow_engine
from .executor import NodeExecutor
from .models import (  # Enums; Dataclasses
    ExecutionResult,
    ExecutionStatus,
    NodeConfig,
    NodeType,
    RouteCondition,
    WorkflowState,
)

__all__ = [
    # Enums
    "NodeType",
    "ExecutionStatus",
    "RouteCondition",
    # Dataclasses
    "NodeConfig",
    "ExecutionResult",
    "WorkflowState",
    # Classes
    "NodeExecutor",
    "WorkflowEngine",
    # Functions
    "create_workflow_engine",
]
