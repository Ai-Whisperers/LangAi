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

# Conditional Router (intelligent workflow routing)
from .conditional_router import LANGGRAPH_AVAILABLE, CompanyType
from .conditional_router import ResearchDepth as ConditionalResearchDepth
from .conditional_router import RoutingDecision as ConditionalRoutingDecision
from .conditional_router import (
    SimpleRouter,
    classify_company_type,
    determine_research_depth,
    make_routing_decision,
)
from .research_workflow import (
    ResearchDepth,
    create_comprehensive_research_workflow,
    create_quick_research_workflow,
    create_research_workflow,
    execute_research,
)
from .scheduler import BatchResult, ScheduleConfig, WorkflowScheduler, create_scheduler
from .swarm_collaboration import (
    AgentResult,
    AgentRole,
    AgentWrapper,
    ConflictResolution,
    ConsensusResult,
    ConsensusStrategy,
    SwarmConfig,
    SwarmOrchestrator,
    SwarmResult,
    create_analysis_swarm,
    create_research_swarm,
)
from .workflow_engine import (  # Enums; Data Models; Core Engine
    ExecutionResult,
    ExecutionStatus,
    NodeConfig,
    NodeType,
    RouteCondition,
    WorkflowEngine,
    WorkflowState,
    create_workflow_engine,
)

# LangGraph conditional workflows (if available)
try:
    from .conditional_router import (
        create_company_type_router,
        create_conditional_research_graph,
        create_iterative_research_graph,
        create_quality_checker,
    )
except ImportError:
    # LangGraph not available
    pass

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
    # Swarm Collaboration
    "SwarmOrchestrator",
    "SwarmConfig",
    "SwarmResult",
    "ConsensusStrategy",
    "ConflictResolution",
    "AgentRole",
    "AgentWrapper",
    "AgentResult",
    "ConsensusResult",
    "create_research_swarm",
    "create_analysis_swarm",
    # Conditional Router
    "CompanyType",
    "ConditionalResearchDepth",
    "ConditionalRoutingDecision",
    "classify_company_type",
    "determine_research_depth",
    "make_routing_decision",
    "SimpleRouter",
    "LANGGRAPH_AVAILABLE",
    "create_conditional_research_graph",
    "create_iterative_research_graph",
    "create_company_type_router",
    "create_quality_checker",
]
