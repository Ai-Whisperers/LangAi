"""
State Management Module for Company Researcher.

Advanced state management capabilities:
- State checkpointing and recovery
- SQLite/MongoDB persistence
- State versioning and migration
- Immutable state patterns
- State snapshots
- Workflow state definitions
- Pydantic type safety (Phase 11+)
- State constants
"""

# Workflow state definitions (core state types)
from .workflow import (
    OverallState,
    InputState,
    OutputState,
    create_initial_state,
    create_output_state,
    merge_dicts,
    add_tokens,
)

# Type safety with Pydantic (Phase 11+)
from .types import (
    # Enums
    NodeStatus,
    CompanyType,
    ResearchDepth,
    # Base models
    TokenUsage,
    CostMetrics,
    # Node outputs
    NodeOutput,
    SearchResult,
    Source,
    SearchNodeOutput,
    ClassificationOutput,
    AnalysisOutput,
    FinancialAnalysisOutput,
    MarketAnalysisOutput,
    CompetitorOutput,
    ESGAnalysisOutput,
    # Quality
    QualityMetrics,
    Contradiction,
    Gap,
    QualityOutput,
    # Synthesis
    SynthesisOutput,
    # Report
    ReportOutput,
    # Agent tracking
    AgentMetrics,
    WorkflowMetrics,
    # State validation
    InputStateModel,
    OutputStateModel,
    # Helpers
    validate_node_output,
    merge_token_usage,
    create_node_output,
)

# State constants
from .constants import (
    StateKey,
    DefaultValue,
    AgentName,
    NodeName,
    EventType,
    ReviewDecision,
)

from .checkpoint import (
    Checkpoint,
    CheckpointManager,
    create_checkpoint,
    restore_checkpoint,
    list_checkpoints,
)

from .persistence import (
    StatePersistence,
    SQLitePersistence,
    InMemoryPersistence,
    create_persistence,
)

from .versioning import (
    StateVersion,
    VersionManager,
    Migration,
    migrate_state,
)

from .snapshot import (
    StateSnapshot,
    SnapshotStore,
    create_snapshot,
    restore_snapshot,
)

from .typed_models import (
    # Enums
    CompanySize,
    IndustryCategory,
    DataFreshness,
    ConfidenceLevel,

    # Source Models
    SourceReference,
    CitedClaim,

    # Financial Models
    FinancialMetrics,
    MarketMetrics,
    ProductMetrics,
    CompanyProfile,

    # Agent Output Models
    AgentOutput,
    FinancialAgentOutput,
    MarketAgentOutput,
    ProductAgentOutput,
    CompetitorAgentOutput,
    TypedAgentOutputs,

    # Quality Models
    QualityAssessment,

    # Complete State
    TypedResearchState,
)

__all__ = [
    # Workflow State
    "OverallState",
    "InputState",
    "OutputState",
    "create_initial_state",
    "create_output_state",
    "merge_dicts",
    "add_tokens",
    # Checkpoint
    "Checkpoint",
    "CheckpointManager",
    "create_checkpoint",
    "restore_checkpoint",
    "list_checkpoints",
    # Persistence
    "StatePersistence",
    "SQLitePersistence",
    "InMemoryPersistence",
    "create_persistence",
    # Versioning
    "StateVersion",
    "VersionManager",
    "Migration",
    "migrate_state",
    # Snapshot
    "StateSnapshot",
    "SnapshotStore",
    "create_snapshot",
    "restore_snapshot",
    # Typed Models - Enums
    "CompanySize",
    "IndustryCategory",
    "DataFreshness",
    "ConfidenceLevel",
    # Typed Models - Source
    "SourceReference",
    "CitedClaim",
    # Typed Models - Financial
    "FinancialMetrics",
    "MarketMetrics",
    "ProductMetrics",
    "CompanyProfile",
    # Typed Models - Agent Outputs
    "AgentOutput",
    "FinancialAgentOutput",
    "MarketAgentOutput",
    "ProductAgentOutput",
    "CompetitorAgentOutput",
    "TypedAgentOutputs",
    # Typed Models - Quality
    "QualityAssessment",
    # Typed Models - Complete State
    "TypedResearchState",
    # Type Safety (Phase 11+) - Enums
    "NodeStatus",
    "CompanyType",
    "ResearchDepth",
    # Type Safety - Base Models
    "TokenUsage",
    "CostMetrics",
    # Type Safety - Node Outputs
    "NodeOutput",
    "SearchResult",
    "Source",
    "SearchNodeOutput",
    "ClassificationOutput",
    "AnalysisOutput",
    "FinancialAnalysisOutput",
    "MarketAnalysisOutput",
    "CompetitorOutput",
    "ESGAnalysisOutput",
    # Type Safety - Quality
    "QualityMetrics",
    "Contradiction",
    "Gap",
    "QualityOutput",
    # Type Safety - Synthesis & Report
    "SynthesisOutput",
    "ReportOutput",
    # Type Safety - Agent Tracking
    "AgentMetrics",
    "WorkflowMetrics",
    # Type Safety - State Validation
    "InputStateModel",
    "OutputStateModel",
    # Type Safety - Helpers
    "validate_node_output",
    "merge_token_usage",
    "create_node_output",
    # State Constants
    "StateKey",
    "DefaultValue",
    "AgentName",
    "NodeName",
    "EventType",
    "ReviewDecision",
]
