# Installation Guide

This guide walks you through setting up the Company Researcher system.

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | Runtime environment |
| pip | Latest | Package management |
| Git | Latest | Version control |

### Required API Keys

| Service | Required | Free Tier | Purpose |
|---------|----------|-----------|---------|
| **Anthropic** | Yes | No | Claude LLM (primary) |
| **Tavily** | Recommended | 1000/month | Optimized web search |
| **DuckDuckGo** | Built-in | Unlimited | Fallback search |

### Optional API Keys (Enhanced Features)

| Service | Purpose | Free Tier |
|---------|---------|-----------|
| Alpha Vantage | Stock fundamentals | 25 req/day |
| Financial Modeling Prep | Company financials | 250 req/day |
| Finnhub | Real-time quotes | 60 req/min |
| GNews | News aggregation | 100 req/day |
| AgentOps | Agent monitoring | 500 sessions/month |
| LangSmith | LLM tracing | Limited free |

## Installation Steps

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/company-researcher.git
cd company-researcher
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Development dependencies (optional)
pip install -r requirements-dev.txt
```

### Step 4: Configure Environment

```bash
# Copy example environment file
cp env.example .env

# Edit with your API keys
# Windows: notepad .env
# macOS/Linux: nano .env
```

### Step 5: Configure API Keys

Edit `.env` with your API keys:

```env
# Required - Primary LLM
ANTHROPIC_API_KEY=sk-ant-api03-...

# Recommended - Search
TAVILY_API_KEY=tvly-...

# Optional - Financial Data
ALPHA_VANTAGE_API_KEY=...
FMP_API_KEY=...
FINNHUB_API_KEY=...

# Optional - News
GNEWS_API_KEY=...
NEWSAPI_API_KEY=...

# Optional - Observability
AGENTOPS_API_KEY=...
LANGSMITH_API_KEY=...
```

### Step 6: Verify Installation

```bash
# Run quick test
python -c "from company_researcher import config; print('Installation successful!')"

# Run first research (optional)
python run_research.py "Microsoft"
```

## Configuration Options

### Environment Variables

See [Configuration Guide](../06-configuration/README.md) for complete list.

Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_MODEL` | claude-3-5-sonnet-20241022 | Claude model to use |
| `LLM_TEMPERATURE` | 0.0 | Model temperature |
| `NUM_SEARCH_QUERIES` | 3 | Queries per search |
| `MAX_SEARCH_RESULTS` | 10 | Results per query |
| `QUALITY_THRESHOLD` | 85 | Minimum quality score |

### Research Configuration

Edit `scripts/research/research_config.yaml`:

```yaml
# Research depth
depth: standard  # quick, standard, comprehensive

# Output formats
output:
  formats: [md, pdf, excel]
  base_dir: outputs/research

# Search strategy
search:
  strategy: free_first  # free_first, auto, tavily_only
  tavily_refinement: true

# Gap filling
gap_filling:
  enabled: true
  max_iterations: 2
  min_quality_score: 85.0
```

## Directory Structure After Installation

```
company-researcher/
├── .env                    # Your API keys (created)
├── venv/                   # Virtual environment (created)
├── src/company_researcher/ # Source code
├── scripts/                # Research scripts
├── tests/                  # Test suites
├── outputs/                # Research outputs (created on first run)
│   └── research/
│       └── <company>/      # Per-company reports
└── docs/                   # Documentation
```

## Common Issues

### API Key Not Found

```
Error: ANTHROPIC_API_KEY not found
```

**Solution**: Ensure `.env` file exists and contains valid API key.

### Import Errors

```
ModuleNotFoundError: No module named 'company_researcher'
```

**Solution**: Ensure virtual environment is activated and packages installed:
```bash
pip install -e .
```

### Tavily Rate Limits

```
Error: Tavily API rate limit exceeded
```

**Solution**: The system will automatically fall back to DuckDuckGo. For higher limits, upgrade Tavily plan.

### Memory Issues

```
MemoryError during research
```

**Solution**: Reduce `MAX_SEARCH_RESULTS` or use `quick` depth mode.

## Next Steps

1. **Run First Research**: [Quick Start Guide](QUICKSTART.md)
2. **Understand System**: [Architecture Overview](../02-architecture/README.md)
3. **Configure Advanced Options**: [Configuration Guide](../06-configuration/README.md)
4. **Deploy to Production**: [Deployment Guide](../11-deployment/README.md)

---

**Last Updated**: December 2024
