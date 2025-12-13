"""
Persistence Package - Phase 12: Checkpointing & Resume

This package provides checkpoint management for LangGraph workflows,
enabling:
- Workflow state persistence to SQLite/PostgreSQL
- Resume interrupted workflows
- Debug by inspecting checkpoint history
- Long-running research support

Usage:
    from company_researcher.graphs.persistence import (
        get_checkpointer,
        create_checkpointed_workflow,
        research_with_checkpoint,
        resume_research,
        list_checkpoints,
    )

    # Research with automatic checkpointing
    result, thread_id = research_with_checkpoint("Tesla")

    # Resume if interrupted
    result = resume_research(thread_id)
"""

from .checkpointer import (
    get_checkpointer,
    get_memory_checkpointer,
    CheckpointerConfig,
    create_checkpointed_workflow,
)
from .resume import (
    research_with_checkpoint,
    resume_research,
    get_workflow_state,
    list_checkpoints,
    delete_checkpoint,
    CheckpointInfo,
)

__all__ = [
    # Checkpointer
    "get_checkpointer",
    "get_memory_checkpointer",
    "CheckpointerConfig",
    "create_checkpointed_workflow",
    # Resume
    "research_with_checkpoint",
    "resume_research",
    "get_workflow_state",
    "list_checkpoints",
    "delete_checkpoint",
    "CheckpointInfo",
]
