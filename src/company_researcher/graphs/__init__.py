"""
Graphs Package - LangGraph Workflow Definitions

This package provides the complete LangGraph workflow architecture:

Phase 11 - Subgraph Architecture:
    - data_collection: Query generation, search, SEC data, scraping
    - analysis: Parallel specialist agents
    - quality: Fact extraction, contradiction detection, gap analysis
    - output: Report generation

Phase 12 - Checkpointing & Persistence:
    - SQLite/PostgreSQL checkpointing
    - Workflow resume capabilities
    - State inspection

Phase 13 - Streaming:
    - Real-time event streaming
    - WebSocket support for web apps
    - Server-Sent Events (SSE)

Phase 14 - Adaptive Routing:
    - Company type classification
    - Dynamic workflow routing
    - Type-specific data collection

Phase 15 - Human-in-the-Loop:
    - Interrupt for human review
    - Approve/reject/revise decisions
    - State modification

Phase 16 - Error Handling:
    - Retry with exponential backoff
    - Fallback node chains
    - Circuit breaker pattern

Usage:
    from company_researcher.graphs import (
        # Main workflows
        create_research_workflow,
        create_adaptive_workflow,
        research_company,
        # Checkpointing
        research_with_checkpoint,
        resume_research,
        # Streaming
        stream_research,
        # Human review
        research_with_review,
    )
"""

# ============================================================================
# Error Handling (Phase 16)
# ============================================================================
from .error_handling import (  # Retry; Fallback; Circuit Breaker
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    FallbackConfig,
    RetryConfig,
    RetryStrategy,
    create_error_boundary,
    with_fallback,
    with_retry,
)

# ============================================================================
# Human-in-the-Loop (Phase 15)
# ============================================================================
from .human_in_loop import (  # Workflow; Research functions; Types
    HumanReviewConfig,
    PendingReview,
    ReviewDecision,
    approve_and_continue,
    create_human_reviewed_workflow,
    get_pending_reviews,
    modify_and_continue,
    reject_and_revise,
    research_with_review,
)

# ============================================================================
# Main Workflows (Phase 11+)
# ============================================================================
from .main_graph import (  # Configurations; Workflow creation; Research functions
    WorkflowConfig,
    create_adaptive_workflow,
    create_comprehensive_workflow,
    create_quick_workflow,
    create_research_workflow,
    research_company,
    research_company_adaptive,
)

# ============================================================================
# Persistence (Phase 12)
# ============================================================================
from .persistence import (  # Checkpointer; Resume
    CheckpointerConfig,
    CheckpointInfo,
    create_checkpointed_workflow,
    delete_checkpoint,
    get_checkpointer,
    get_memory_checkpointer,
    get_workflow_state,
    list_checkpoints,
    research_with_checkpoint,
    resume_research,
)

# ============================================================================
# Legacy Graphs (backward compatibility)
# ============================================================================
from .research_graph import ResearchState
from .research_graph import graph as research_graph
from .research_graph import (
    node_extract_data,
    node_generate_queries,
    node_generate_report,
    node_search_web,
)
from .simple_graph import SimpleState
from .simple_graph import graph as simple_graph

# ============================================================================
# Streaming (Phase 13)
# ============================================================================
from .streaming import (  # Event streaming; WebSocket
    StreamConfig,
    StreamEvent,
    WebSocketManager,
    create_websocket_router,
    research_websocket_handler,
    stream_research,
    stream_research_events,
)

# ============================================================================
# Subgraphs (Phase 11)
# ============================================================================
from .subgraphs import (  # Data Collection; Analysis; Quality; Output
    AnalysisConfig,
    DataCollectionConfig,
    OutputConfig,
    QualityConfig,
    create_analysis_subgraph,
    create_data_collection_subgraph,
    create_output_subgraph,
    create_parallel_analysis_subgraph,
    create_quality_subgraph,
)

__all__ = [
    # Legacy graphs (backward compatibility)
    "research_graph",
    "ResearchState",
    "node_generate_queries",
    "node_search_web",
    "node_extract_data",
    "node_generate_report",
    "simple_graph",
    "SimpleState",
    # Main Workflows
    "WorkflowConfig",
    "create_research_workflow",
    "create_quick_workflow",
    "create_comprehensive_workflow",
    "create_adaptive_workflow",
    "research_company",
    "research_company_adaptive",
    # Subgraphs
    "create_data_collection_subgraph",
    "DataCollectionConfig",
    "create_analysis_subgraph",
    "create_parallel_analysis_subgraph",
    "AnalysisConfig",
    "create_quality_subgraph",
    "QualityConfig",
    "create_output_subgraph",
    "OutputConfig",
    # Persistence
    "get_checkpointer",
    "get_memory_checkpointer",
    "CheckpointerConfig",
    "create_checkpointed_workflow",
    "research_with_checkpoint",
    "resume_research",
    "get_workflow_state",
    "list_checkpoints",
    "delete_checkpoint",
    "CheckpointInfo",
    # Streaming
    "stream_research",
    "stream_research_events",
    "StreamEvent",
    "StreamConfig",
    "create_websocket_router",
    "WebSocketManager",
    "research_websocket_handler",
    # Human-in-the-Loop
    "create_human_reviewed_workflow",
    "research_with_review",
    "approve_and_continue",
    "reject_and_revise",
    "modify_and_continue",
    "get_pending_reviews",
    "HumanReviewConfig",
    "ReviewDecision",
    "PendingReview",
    # Error Handling
    "with_retry",
    "RetryConfig",
    "RetryStrategy",
    "with_fallback",
    "create_error_boundary",
    "FallbackConfig",
    "CircuitBreaker",
    "CircuitState",
    "CircuitBreakerConfig",
]
