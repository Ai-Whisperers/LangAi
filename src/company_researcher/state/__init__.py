"""
State Management Module for Company Researcher.

Advanced state management capabilities:
- State checkpointing and recovery
- SQLite/MongoDB persistence
- State versioning and migration
- Immutable state patterns
- State snapshots
- Workflow state definitions
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
]
