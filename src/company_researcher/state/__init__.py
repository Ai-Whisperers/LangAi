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
]
