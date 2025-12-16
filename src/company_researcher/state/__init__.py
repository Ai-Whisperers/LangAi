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

from .checkpoint import (
    Checkpoint,
    CheckpointManager,
    create_checkpoint,
    list_checkpoints,
    restore_checkpoint,
)

# State constants
from .constants import AgentName, DefaultValue, EventType, NodeName, ReviewDecision, StateKey
from .persistence import (
    InMemoryPersistence,
    SQLitePersistence,
    StatePersistence,
    create_persistence,
)
from .snapshot import SnapshotStore, StateSnapshot, create_snapshot, restore_snapshot
from .typed_models import (  # Enums; Source Models; Financial Models; Agent Output Models; Quality Models; Complete State
    AgentOutput,
    CitedClaim,
    CompanyProfile,
    CompanySize,
    CompetitorAgentOutput,
    ConfidenceLevel,
    DataFreshness,
    FinancialAgentOutput,
    FinancialMetrics,
    IndustryCategory,
    MarketAgentOutput,
    MarketMetrics,
    ProductAgentOutput,
    ProductMetrics,
    QualityAssessment,
    SourceReference,
    TypedAgentOutputs,
    TypedResearchState,
)

# Type safety with Pydantic (Phase 11+)
from .types import (  # Enums; Base models; Node outputs; Quality; Synthesis; Report; Agent tracking; State validation; Helpers
    AgentMetrics,
    AnalysisOutput,
    ClassificationOutput,
    CompanyType,
    CompetitorOutput,
    Contradiction,
    CostMetrics,
    ESGAnalysisOutput,
    FinancialAnalysisOutput,
    Gap,
    InputStateModel,
    MarketAnalysisOutput,
    NodeOutput,
    NodeStatus,
    OutputStateModel,
    QualityMetrics,
    QualityOutput,
    ReportOutput,
    ResearchDepth,
    SearchNodeOutput,
    SearchResult,
    Source,
    SynthesisOutput,
    TokenUsage,
    WorkflowMetrics,
    create_node_output,
    merge_token_usage,
    validate_node_output,
)
from .versioning import Migration, StateVersion, VersionManager, migrate_state

# Workflow state definitions (core state types)
from .workflow import (
    InputState,
    OutputState,
    OverallState,
    add_tokens,
    create_initial_state,
    create_output_state,
    merge_dicts,
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
