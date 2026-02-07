"""
ISOLATE Strategy (Phase 12.4) - Backward Compatibility Module.

This module re-exports all components from the modular isolation/ package
for backward compatibility. New code should import directly from:

    from company_researcher.context.isolation import (
        ContextIsolationManager,
        AgentContextBuilder,
        IsolationLevel,
        ...
    )

This file maintains backward compatibility with existing imports:
    from company_researcher.context.isolate_strategy import ContextIsolationManager
"""

# Re-export all components from modular structure
from .isolation import (  # Enums; Data Models; Classes; Factory Functions
    AgentContext,
    AgentContextBuilder,
    ContextFilter,
    ContextIsolationManager,
    ContextItem,
    ContextVisibility,
    IsolationLevel,
    SharePolicy,
    build_agent_context,
    create_isolation_manager,
)

__all__ = [
    # Enums
    "IsolationLevel",
    "SharePolicy",
    "ContextVisibility",
    # Data Models
    "ContextItem",
    "AgentContext",
    # Classes
    "ContextFilter",
    "ContextIsolationManager",
    "AgentContextBuilder",
    # Factory Functions
    "create_isolation_manager",
    "build_agent_context",
]
