"""
Context Isolation Module.

Provides multi-agent context separation and management:
- Agent-specific context boundaries
- Information flow control
- Context inheritance management
- Cross-agent communication protocols

Usage:
    from company_researcher.context.isolation import (
        ContextIsolationManager,
        AgentContextBuilder,
        IsolationLevel,
        SharePolicy,
        create_isolation_manager,
        build_agent_context
    )
"""

from .builder import AgentContextBuilder, build_agent_context, create_isolation_manager
from .filter import ContextFilter
from .manager import ContextIsolationManager
from .models import AgentContext, ContextItem, ContextVisibility, IsolationLevel, SharePolicy

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
