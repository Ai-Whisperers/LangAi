"""
Workflow Engine (Phase 17.1).

DEPRECATED: This module re-exports from the modular workflow package.
Import directly from company_researcher.orchestration.workflow instead:

    from company_researcher.orchestration.workflow import (
        WorkflowEngine,
        NodeConfig,
        NodeType,
        ExecutionStatus,
        create_workflow_engine
    )
"""

# Re-export all public API from the workflow package for backward compatibility
from .workflow import (  # Enums; Dataclasses; Classes; Functions
    ExecutionResult,
    ExecutionStatus,
    NodeConfig,
    NodeExecutor,
    NodeType,
    RouteCondition,
    WorkflowEngine,
    WorkflowState,
    create_workflow_engine,
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
