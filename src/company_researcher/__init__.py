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

# Centralized types (shared enums and dataclasses)
# Core modules
from . import agents, graphs, tools, types, workflows

# Initialize observability on import
from .observability import init_observability
from .types import (
    AgentMetrics,
    ConfidenceLevel,
    DataQuality,
    EventType,
    FreshnessLevel,
    HealthStatus,
    InsightType,
    ReasoningType,
)
from .types import (
    ResearchDepth as ResearchDepthType,  # Research types; Quality types; Infrastructure types; Common dataclasses
)
from .types import SourceInfo, SourceQuality, TaskStatus, TokenUsage

init_observability()

# Production module (Phase 20)
# Monitoring module (Phase 19)
# API module (Phase 18)
# Orchestration module (Phase 17)
# Output module (Phase 16)
# Context module (Phase 12)
# Memory module (Phase 11)
# Quality module (Phases 10-11)
from . import api, context, memory, monitoring, orchestration, output, production, quality
from .orchestration import ResearchDepth, execute_research

__all__ = [
    # Core
    "agents",
    "workflows",
    "tools",
    "graphs",
    "init_observability",
    # Types
    "types",
    "ResearchDepthType",
    "DataQuality",
    "ReasoningType",
    "InsightType",
    "ConfidenceLevel",
    "SourceQuality",
    "FreshnessLevel",
    "TaskStatus",
    "EventType",
    "HealthStatus",
    "TokenUsage",
    "AgentMetrics",
    "SourceInfo",
    # Quality
    "quality",
    # Memory
    "memory",
    # Context
    "context",
    # Output
    "output",
    # Orchestration
    "orchestration",
    "execute_research",
    "ResearchDepth",
    # API
    "api",
    # Monitoring
    "monitoring",
    # Production
    "production",
]

__version__ = "1.0.0"
