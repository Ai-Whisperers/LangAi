"""
Workflow Orchestration Module (Phase 17).

Advanced workflow orchestration capabilities:
- Dynamic workflow engine
- Parallel and sequential execution
- Conditional routing
- Workflow scheduling
- Pre-built research workflows

Usage:
    from src.company_researcher.orchestration import (
        WorkflowEngine,
        WorkflowScheduler,
        create_research_workflow,
        execute_research
    )

    # Create and execute a research workflow
    result = execute_research(
        company_name="Tesla",
        depth="comprehensive"
    )

    # Or use the scheduler for batch processing
    scheduler = WorkflowScheduler()
    scheduler.schedule_batch(["Tesla", "Apple", "Microsoft"])
"""

from .workflow_engine import (
    # Enums
    NodeType,
    ExecutionStatus,
    RouteCondition,
    # Data Models
    NodeConfig,
    ExecutionResult,
    WorkflowState,
    # Core Engine
    WorkflowEngine,
    create_workflow_engine,
)

from .scheduler import (
    WorkflowScheduler,
    ScheduleConfig,
    BatchResult,
    create_scheduler,
)

from .research_workflow import (
    create_research_workflow,
    create_quick_research_workflow,
    create_comprehensive_research_workflow,
    execute_research,
    ResearchDepth,
)

__all__ = [
    # Workflow Engine
    "NodeType",
    "ExecutionStatus",
    "RouteCondition",
    "NodeConfig",
    "ExecutionResult",
    "WorkflowState",
    "WorkflowEngine",
    "create_workflow_engine",
    # Scheduler
    "WorkflowScheduler",
    "ScheduleConfig",
    "BatchResult",
    "create_scheduler",
    # Research Workflows
    "create_research_workflow",
    "create_quick_research_workflow",
    "create_comprehensive_research_workflow",
    "execute_research",
    "ResearchDepth",
]
