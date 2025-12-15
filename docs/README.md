# Company Researcher Documentation

Comprehensive documentation for the AI-powered multi-agent company research system.

---

## Quick Navigation

| I want to... | Go to... |
|--------------|----------|
| Get started quickly | [Quick Start](01-overview/QUICKSTART.md) |
| Install the system | [Installation Guide](01-overview/INSTALLATION.md) |
| Understand how it works | [Architecture](02-architecture/README.md) |
| Learn about agents | [Agent Documentation](03-agents/README.md) |
| Configure the system | [Configuration Guide](06-configuration/README.md) |
| Run research | [Scripts & CLI](09-scripts/README.md) |
| Write tests | [Testing Guide](10-testing/README.md) |
| Deploy the system | [Deployment](11-deployment/README.md) |
| Call the API | [API Reference](12-api-reference/README.md) |
| See future plans | [Roadmap](roadmap/) |

---

## Documentation Structure

```
docs/
├── 01-overview/                    # Getting started
│   ├── README.md                   # Project overview
│   ├── INSTALLATION.md             # Setup guide
│   └── QUICKSTART.md               # 5-minute start
│
├── 02-architecture/                # System design
│   ├── README.md                   # Architecture overview
│   ├── SYSTEM_DESIGN.md            # Detailed design
│   └── diagrams/                   # Visual diagrams
│
├── 03-agents/                      # AI agents
│   ├── README.md                   # Agent overview
│   ├── AGENT_CONTRACTS.md          # Input/output specifications
│   ├── AGENT_DEVELOPMENT_GUIDE.md  # Creating agents
│   ├── core/                       # Core agents
│   ├── specialists/                # Specialist agents
│   └── quality/                    # Quality agents
│
├── 04-workflows/                   # LangGraph workflows
│   ├── README.md                   # Workflow documentation
│   ├── WORKFLOW_LOGIC.md           # Decision logic & state transitions
│   └── LANGGRAPH_STUDIO_GUIDE.md   # Visual debugging
│
├── 05-integrations/                # External APIs
│   ├── README.md                   # Integration overview
│   ├── INTEGRATION_PATTERNS.md     # Fallback & selection logic
│   ├── search/                     # Search providers
│   └── financial/                  # Financial data
│
├── 06-configuration/               # Configuration
│   ├── README.md                   # Config options
│   ├── THRESHOLD_RATIONALE.md      # Why thresholds are set
│   ├── PROMPT_ENGINEERING.md       # Prompt design decisions
│   └── llm-setup.md                # LLM configuration
│
├── 07-state-management/            # State flow
├── 08-quality-system/              # Quality scoring
│   ├── README.md                   # Quality overview
│   └── QUALITY_LOGIC.md            # Scoring algorithms & detection
├── 09-scripts/                     # CLI tools
├── 10-testing/                     # Testing guide
├── 11-deployment/                  # Deployment (Docker/K8s)
├── 12-api-reference/               # REST/WebSocket API reference
│
├── roadmap/                        # Future development
│   ├── TECHNOLOGY_IMPROVEMENT_PLAN.md
│   ├── API_IMPLEMENTATION_PLAN.md
│   ├── IMPROVEMENT_ROADMAP.md
│   └── CODEBASE_IMPROVEMENT_ROADMAP.md
│
└── README.md                       # This index
```

---

## System Overview

**Company Researcher** is an AI-powered multi-agent system that automatically generates comprehensive company research reports.

### Key Features

- **Multi-Agent Architecture**: 5+ specialized agents analyze different business aspects
- **Parallel Execution**: Agents run concurrently for faster research
- **Quality Assurance**: Automatic fact verification and contradiction detection
- **Iterative Improvement**: Automatically improves until 85%+ quality score
- **Cost Tracking**: Real-time token and cost monitoring (~$0.08/report)

### Technology Stack

| Component | Technology |
|-----------|------------|
| Agent Orchestration | LangGraph |
| LLM Framework | LangChain |
| Primary LLM | Claude (Anthropic) |
| Web Search | Tavily + DuckDuckGo |
| Financial Data | yfinance, Alpha Vantage, FMP |
| Observability | AgentOps, LangSmith |

### Current Status

**Phase**: Phase 4 Complete - Parallel Multi-Agent System

| Metric | Target | Current |
|--------|--------|---------|
| Quality Score | 85%+ | 84.7% avg |
| Cost per Report | ~$0.05 | ~$0.08 |
| Time per Report | <5 min | 2-5 min |

---

## Quick Example

```bash
# Install
pip install -r requirements.txt
cp env.example .env   # macOS/Linux
# Windows PowerShell:
#   Copy-Item env.example .env
# Edit .env with API keys

# Run research
python run_research.py --company "Microsoft"
```

**Output:**

```
outputs/research/microsoft/
├── 00_full_report.md
├── 01_executive_summary.md
├── 02_company_overview.md
├── 03_financials.md
├── 04_market_position.md
├── 05_competitive_analysis.md
├── 06_strategy.md
├── 07_sources.md
└── metrics.json
```

---

## Documentation by Topic

### Getting Started

| Document | Description |
|----------|-------------|
| [Project Overview](01-overview/README.md) | What is Company Researcher? |
| [Installation](01-overview/INSTALLATION.md) | Setup and prerequisites |
| [Quick Start](01-overview/QUICKSTART.md) | First research in 5 minutes |

### Architecture & Design

| Document | Description |
|----------|-------------|
| [Architecture Overview](02-architecture/README.md) | System architecture |
| [System Design](02-architecture/SYSTEM_DESIGN.md) | Detailed design docs |
| [Diagrams](02-architecture/diagrams/README.md) | Visual diagrams |
| [State Management](07-state-management/README.md) | State flow and reducers |

### Agents

| Document | Description |
|----------|-------------|
| [Agent Overview](03-agents/README.md) | All agents summary |
| [Agent Contracts](03-agents/AGENT_CONTRACTS.md) | Input/output specifications |
| [Agent Development](03-agents/AGENT_DEVELOPMENT_GUIDE.md) | Creating new agents |
| [Core Agents](03-agents/core/README.md) | Researcher, Analyst, Synthesizer |
| [Specialist Agents](03-agents/specialists/README.md) | Financial, Market, Product |
| [Quality Agents](03-agents/quality/README.md) | Logic Critic, Quality Checker |

### Workflows

| Document | Description |
|----------|-------------|
| [Workflow Documentation](04-workflows/README.md) | LangGraph workflows |
| [Workflow Logic](04-workflows/WORKFLOW_LOGIC.md) | Decision logic, state transitions |
| [LangGraph Studio](04-workflows/LANGGRAPH_STUDIO_GUIDE.md) | Visual debugging |

### Integrations

| Document | Description |
|----------|-------------|
| [Integration Overview](05-integrations/README.md) | All integrations |
| [Integration Patterns](05-integrations/INTEGRATION_PATTERNS.md) | Fallback & selection logic |
| [Search Providers](05-integrations/search/README.md) | Tavily, DuckDuckGo |
| [Financial APIs](05-integrations/financial/README.md) | yfinance, Alpha Vantage |

### Configuration & Operations

| Document | Description |
|----------|-------------|
| [Configuration Guide](06-configuration/README.md) | All configuration options |
| [Threshold Rationale](06-configuration/THRESHOLD_RATIONALE.md) | Why thresholds are set |
| [Prompt Engineering](06-configuration/PROMPT_ENGINEERING.md) | Prompt design decisions |
| [LLM Setup](06-configuration/llm-setup.md) | LLM configuration |
| [Scripts & CLI](09-scripts/README.md) | Command-line tools |
| [Quality System](08-quality-system/README.md) | Quality scoring |
| [Quality Logic](08-quality-system/QUALITY_LOGIC.md) | Scoring algorithms |
| [Testing Guide](10-testing/README.md) | Test suites |

### Future Development

| Document | Description |
|----------|-------------|
| [Implementation Status](roadmap/IMPLEMENTATION_STATUS.md) | ⭐ What's complete vs planned |
| [Technology Improvements](roadmap/TECHNOLOGY_IMPROVEMENT_PLAN.md) | Tech stack optimization |
| [API Implementation](roadmap/API_IMPLEMENTATION_PLAN.md) | REST API roadmap |
| [Improvement Ideas](roadmap/IMPROVEMENT_ROADMAP.md) | 50 enhancement ideas |
| [Technical Debt](roadmap/CODEBASE_IMPROVEMENT_ROADMAP.md) | Codebase improvements |

---

## Getting Help

1. Check [Quick Start](01-overview/QUICKSTART.md)
2. Review [Configuration](06-configuration/README.md)
3. See [Testing Guide](10-testing/README.md) for troubleshooting

---

**Last Updated**: December 2025

**Current Version**: Phase 4 - Parallel Multi-Agent System with Quality Integration
