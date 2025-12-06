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

# Core modules
from . import agents, workflows, tools, graphs

# Initialize observability on import
from .observability import init_observability
init_observability()

# Quality module (Phases 10-11)
from . import quality

# Memory module (Phase 11)
from . import memory

# Context module (Phase 12)
from . import context

# Output module (Phase 16)
from . import output

# Orchestration module (Phase 17)
from . import orchestration
from .orchestration import execute_research, ResearchDepth

# API module (Phase 18)
from . import api

# Monitoring module (Phase 19)
from . import monitoring

# Production module (Phase 20)
from . import production

__all__ = [
    # Core
    "agents",
    "workflows",
    "tools",
    "graphs",
    "init_observability",
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
