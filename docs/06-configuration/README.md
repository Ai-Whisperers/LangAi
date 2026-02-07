# Configuration Guide

This section documents how the Company Researcher is configured at runtime.

---

## Sources of configuration

Configuration comes from:

1. **Environment variables** (recommended): `.env` loaded via `python-dotenv`
2. **Defaults** defined in code: `src/company_researcher/config.py`

The authoritative configuration model is:

- `company_researcher.config.ResearchConfig`

---

## Quick setup

1. Copy the example file:

```bash
cp env.example .env   # macOS/Linux
# Windows PowerShell:
#   Copy-Item env.example .env
```

2. Fill in the keys you need.

---

## Required keys

These are required for the default “LLM + web research” flows:

- `ANTHROPIC_API_KEY` (Claude)
- `TAVILY_API_KEY` (web search)

See `env.example` for full commentary and placeholders.

---

## Optional keys

The system can enrich research using additional providers when keys are present:

- **Financial**: `ALPHA_VANTAGE_API_KEY`, `FMP_API_KEY`, `FINNHUB_API_KEY`, `POLYGON_API_KEY`
- **News**: `NEWSAPI_KEY`, `GNEWS_API_KEY`, `MEDIASTACK_API_KEY`
- **Company data**: `HUNTER_API_KEY`, `GITHUB_TOKEN`, `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`

`env.example` also includes optional LLM providers for cost/performance tradeoffs (DeepSeek, Gemini, Groq, etc.).

---

## Observability / tracing (optional)

Configured via `.env`:

- `AGENTOPS_API_KEY` (AgentOps)
- `LANGSMITH_API_KEY`, `LANGCHAIN_TRACING_V2`, `LANGCHAIN_PROJECT` (LangSmith)
- `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`, `LANGFUSE_ENABLED` (Langfuse)

---

## AI feature toggles (optional)

Feature flags:

- `AI_GLOBAL_ENABLED`
- `AI_SENTIMENT_ENABLED`
- `AI_QUERY_ENABLED`
- `AI_QUALITY_ENABLED`
- `AI_EXTRACTION_ENABLED`

Cost guardrails:

- `AI_COST_WARN_THRESHOLD`
- `AI_COST_MAX_THRESHOLD`

Defaults and guidance are documented in `env.example`.

---

## Code usage

To access validated configuration in Python:

```python
from company_researcher.config import get_config

config = get_config()
print(config.output_dir)
```

`get_config()` creates a singleton and validates key formats where applicable.

---

## Output directory

Some LangGraph workflows write reports under `config.output_dir` (default: `outputs/`).

Other entrypoints (like the CLI wrapper) may write to a separate folder (default: `outputs/research/`) via their own `--output` flag.

---

**Related documentation**

- [Installation Guide](../01-overview/INSTALLATION.md)
- [Codebase Tour](../01-overview/CODEBASE_TOUR.md)
- [Deployment](../11-deployment/README.md)
