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
# Legacy Graphs (backward compatibility)
# ============================================================================
from .research_graph import (
    graph as research_graph,
    ResearchState,
    node_generate_queries,
    node_search_web,
    node_extract_data,
    node_generate_report,
)

from .simple_graph import (
    graph as simple_graph,
    SimpleState,
)

# ============================================================================
# Main Workflows (Phase 11+)
# ============================================================================
from .main_graph import (
    # Configurations
    WorkflowConfig,
    # Workflow creation
    create_research_workflow,
    create_quick_workflow,
    create_comprehensive_workflow,
    create_adaptive_workflow,
    # Research functions
    research_company,
    research_company_adaptive,
)

# ============================================================================
# Subgraphs (Phase 11)
# ============================================================================
from .subgraphs import (
    # Data Collection
    create_data_collection_subgraph,
    DataCollectionConfig,
    # Analysis
    create_analysis_subgraph,
    create_parallel_analysis_subgraph,
    AnalysisConfig,
    # Quality
    create_quality_subgraph,
    QualityConfig,
    # Output
    create_output_subgraph,
    OutputConfig,
)

# ============================================================================
# Persistence (Phase 12)
# ============================================================================
from .persistence import (
    # Checkpointer
    get_checkpointer,
    get_memory_checkpointer,
    CheckpointerConfig,
    create_checkpointed_workflow,
    # Resume
    research_with_checkpoint,
    resume_research,
    get_workflow_state,
    list_checkpoints,
    delete_checkpoint,
    CheckpointInfo,
)

# ============================================================================
# Streaming (Phase 13)
# ============================================================================
from .streaming import (
    # Event streaming
    stream_research,
    stream_research_events,
    StreamEvent,
    StreamConfig,
    # WebSocket
    create_websocket_router,
    WebSocketManager,
    research_websocket_handler,
)

# ============================================================================
# Human-in-the-Loop (Phase 15)
# ============================================================================
from .human_in_loop import (
    # Workflow
    create_human_reviewed_workflow,
    # Research functions
    research_with_review,
    approve_and_continue,
    reject_and_revise,
    modify_and_continue,
    get_pending_reviews,
    # Types
    HumanReviewConfig,
    ReviewDecision,
    PendingReview,
)

# ============================================================================
# Error Handling (Phase 16)
# ============================================================================
from .error_handling import (
    # Retry
    with_retry,
    RetryConfig,
    RetryStrategy,
    # Fallback
    with_fallback,
    create_error_boundary,
    FallbackConfig,
    # Circuit Breaker
    CircuitBreaker,
    CircuitState,
    CircuitBreakerConfig,
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
