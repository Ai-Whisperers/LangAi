# Company Researcher - Project Overview

## What is Company Researcher?

**Company Researcher** is an AI-powered multi-agent research system that automatically generates comprehensive company research reports. Using specialized agents running in parallel, it delivers detailed analysis in 2-5 minutes at approximately $0.08 per research.

## Key Capabilities

| Capability | Description |
|------------|-------------|
| **Automated Research** | Input a company name, receive a complete research report |
| **Multi-Agent System** | 5+ specialized agents analyze different aspects simultaneously |
| **Quality Assurance** | Logic Critic agent verifies facts and detects contradictions |
| **Iterative Refinement** | Automatically improves until reaching 85%+ quality score |
| **Cost Tracking** | Real-time token and cost monitoring (~$0.08 per report) |
| **Multiple Formats** | Output in Markdown, PDF, Excel, and more |

## System Architecture Summary

```
USER INPUT (Company Name)
         |
         v
    RESEARCHER AGENT
    (Query Generation + Search)
         |
    [FAN-OUT] - Parallel Execution
    /    |    \       \
   v     v     v       v
FINANCIAL MARKET PRODUCT COMPETITOR
  AGENT   AGENT  AGENT    SCOUT
   \     |     /       /
    [FAN-IN] - Synchronize
         |
         v
  SYNTHESIZER AGENT
  (Combine Results)
         |
         v
  LOGIC CRITIC AGENT
  (Quality Assurance)
         |
         v
  QUALITY CHECK NODE
  (Iterate if < 85%)
         |
         v
   MARKDOWN REPORT
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Agent Orchestration** | LangGraph | Workflow definition and execution |
| **LLM Framework** | LangChain | LLM abstractions and utilities |
| **Primary LLM** | Claude (Anthropic) | Analysis and synthesis |
| **Web Search** | Tavily + DuckDuckGo | Information gathering |
| **Financial Data** | yfinance, Alpha Vantage, FMP | Market and financial metrics |
| **Data Validation** | Pydantic | Type safety and validation |
| **Observability** | AgentOps, LangSmith | Monitoring and debugging |

## Current Status

**Phase**: Phase 4 Complete - Parallel Multi-Agent System

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Success Rate | 85%+ quality | 67% (2/3) | In Progress |
| Cost per Report | $0.05 | $0.08 | Acceptable |
| Time per Report | < 5 min | 2-5 min | On Target |
| Quality Score | 85%+ | 84.7% avg | On Target |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp env.example .env   # macOS/Linux
# Windows PowerShell:
#   Copy-Item env.example .env
# Edit .env with your API keys

# 3. Run research
python run_research.py --company "Microsoft"
```

## Codebase Tour

If you want a guided map of the code (entrypoints, workflows, agents, outputs), read:

- [Codebase Tour](CODEBASE_TOUR.md)

## Project Structure

```
company-researcher/
├── src/company_researcher/     # Main source code
│   ├── agents/                 # AI agents
│   ├── workflows/              # LangGraph workflows
│   ├── integrations/           # External API clients
│   ├── quality/                # Quality assurance
│   ├── state.py                # State management
│   └── config.py               # Configuration
├── scripts/research/           # Research orchestration
├── tests/                      # Test suites
├── outputs/                    # Research reports
└── docs/                       # Documentation (you are here)
```

## Documentation Map

| Section | Description |
|---------|-------------|
| [01-overview/](.) | Project overview and introduction |
| [02-architecture/](../02-architecture/) | System design and patterns |
| [03-agents/](../03-agents/) | Agent documentation |
| [04-workflows/](../04-workflows/) | Workflow definitions |
| [05-integrations/](../05-integrations/) | External API integrations |
| [06-configuration/](../06-configuration/) | Configuration guide |
| [07-state-management/](../07-state-management/) | State and data flow |
| [08-quality-system/](../08-quality-system/) | Quality assurance |
| [09-scripts/](../09-scripts/) | Scripts and CLI tools |
| [10-testing/](../10-testing/) | Testing guide |
| [11-deployment/](../11-deployment/) | Deployment guide |
| [12-api-reference/](../12-api-reference/) | API documentation |

## Key Concepts

### Agents

Specialized AI workers that handle specific research domains:
- **Researcher**: Generates search queries and gathers sources
- **Financial Agent**: Analyzes revenue, profitability, financial health
- **Market Agent**: Evaluates market position, trends, competitive dynamics
- **Product Agent**: Catalogs products, technology stack, roadmap
- **Competitor Scout**: Identifies competitors and positioning
- **Synthesizer**: Combines all analyses into a coherent report
- **Logic Critic**: Verifies facts and detects contradictions

### Workflows

LangGraph-based orchestration that defines:
- Node execution order
- Parallel vs sequential processing
- Conditional branching (iterate vs finish)
- State updates and merging

### Quality-Driven Iteration

The system iteratively improves research quality:
1. Initial research generates baseline report
2. Quality check evaluates completeness (0-100 score)
3. If score < 85%, identify gaps and iterate
4. Maximum 2 iterations to control costs
5. Final report saved when quality threshold met

## Example Output

A typical research report includes:

```
outputs/research/microsoft/
├── 00_full_report.md       # Complete integrated report
├── 01_executive_summary.md # Key findings and recommendations
├── 02_company_overview.md  # Company background and history
├── 03_financials.md        # Financial analysis
├── 04_market_position.md   # Market positioning
├── 05_competitive_analysis.md # Competitor comparison
├── 06_strategy.md          # Strategic outlook
├── 07_sources.md           # Source citations
├── metrics.json            # Quality and cost metrics
└── financial_data.json     # Raw financial data
```

## Next Steps

1. **Get Started**: Follow the [Installation Guide](INSTALLATION.md)
2. **Learn Architecture**: Read [System Architecture](../02-architecture/README.md)
3. **Understand Agents**: Explore [Agent Documentation](../03-agents/README.md)
4. **Configure System**: See [Configuration Guide](../06-configuration/README.md)

---

**Last Updated**: December 2024
