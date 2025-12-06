# Company Researcher Documentation

Welcome to the Company Researcher documentation. This multi-agent AI system provides comprehensive company research capabilities.

## Quick Navigation

### Getting Started
- [Installation Guide](getting-started/INSTALLATION.md) - Set up the project
- [Quickstart](getting-started/quickstart.md) - Get up and running quickly

### Guides
- [LangGraph Studio Guide](guides/LANGGRAPH_STUDIO_GUIDE.md) - Using LangGraph Studio
- [LLM Setup](llm-setup.md) - Configure language models

### Reference
- [API Reference](reference/api.md) - API documentation
- [Architecture](company-researcher/architecture.md) - System architecture

### Internal Documentation
- [Roadmap](internal/roadmap.md) - Development roadmap
- [Validation Report](internal/VALIDATION_REPORT.md) - Testing validation

## Architecture Overview

The Company Researcher system consists of 20 integrated phases:

```
Phases 1-9:   Core Infrastructure (Agents, Search, LLM, Observability)
Phases 10-15: Intelligence Agents (Financial, Market, Competitive, etc.)
Phases 16-17: Orchestration (Workflow Engine, Scheduling)
Phase 18:     API Layer (REST, WebSocket)
Phase 19:     Monitoring (Metrics, Cost Tracking, Alerts)
Phase 20:     Production Hardening (Circuit Breakers, Health Checks)
```

## Module Structure

```
src/company_researcher/
├── agents/        # AI agents for research
├── api/           # REST API and WebSocket
├── context/       # Context engineering
├── memory/        # Dual-layer memory system
├── monitoring/    # Metrics and alerting
├── orchestration/ # Workflow engine
├── output/        # Report generation (PDF, Excel, PPT)
├── production/    # Production hardening
├── quality/       # Quality assurance
├── tools/         # External API integrations
└── workflows/     # Research workflows
```

## Quick Example

```python
from company_researcher import execute_research, ResearchDepth

# Run comprehensive research
result = execute_research(
    company_name="Tesla",
    depth=ResearchDepth.COMPREHENSIVE
)

print(f"Research completed in {result.duration_seconds}s")
print(f"Total cost: ${result.total_cost:.4f}")
```
