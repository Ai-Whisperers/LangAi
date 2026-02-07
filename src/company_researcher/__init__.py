"""
Company Researcher - Multi-agent AI system for comprehensive company research.

A modular, production-ready system with 20 integrated phases:

Phases 1-9: Core Infrastructure
- Multi-agent architecture
- Search integration (Tavily)
- LLM integration (Anthropic Claude)
- Observability (AgentOps, LangSmith)

Phases 10-15: Intelligence Agents
- Financial Analysis
- Market Analysis
- Competitive Intelligence
- News & Sentiment
- Brand Audit
- Social Media Analysis
- Sales Intelligence
- Investment Analysis
- Logic Critic (Quality)

Phases 16-17: Orchestration
- Workflow Engine
- Parallel Execution
- Scheduling

Phase 18: API Layer
- REST API
- WebSocket
- Authentication

Phase 19: Monitoring
- Metrics Collection
- Cost Tracking
- Performance Monitoring
- Alerting

Phase 20: Production Hardening
- Circuit Breakers
- Retry Policies
- Health Checks
- Graceful Shutdown

Usage:
    from src.company_researcher import execute_research

    result = execute_research(
        company_name="Tesla",
        depth="comprehensive"
    )
"""

from __future__ import annotations

from typing import Any

__version__ = "1.0.0"


def init_observability() -> None:
    """
    Initialize observability integrations (if installed).

    This is intentionally NOT executed on import so optional dependencies
    (AgentOps/LangSmith/etc.) don't break lightweight usage and unit tests.
    """
    from .observability import init_observability as _init

    _init()


def __getattr__(name: str) -> Any:  # pragma: no cover
    """
    Lazy attribute loader to avoid importing heavy optional dependencies at import time.
    """
    if name in {"execute_research", "ResearchDepth"}:
        from .orchestration import ResearchDepth, execute_research

        return {"execute_research": execute_research, "ResearchDepth": ResearchDepth}[name]

    if name in {
        "api",
        "context",
        "memory",
        "monitoring",
        "output",
        "production",
        "quality",
        "agents",
        "graphs",
        "tools",
        "types",
        "workflows",
    }:
        return __import__(f"{__name__}.{name}", fromlist=[name])

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "init_observability",
    "execute_research",
    "ResearchDepth",
    "api",
    "context",
    "memory",
    "monitoring",
    "output",
    "production",
    "quality",
    "agents",
    "graphs",
    "tools",
    "types",
    "workflows",
]
