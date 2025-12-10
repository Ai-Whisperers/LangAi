# Configuration Guide

This section documents all configuration options for the Company Researcher.

## Overview

Configuration is managed through:

1. **Environment Variables** (`.env`) - API keys and secrets
2. **Python Config** (`config.py`) - Application settings
3. **YAML Config** (`research_config.yaml`) - Research parameters
4. **CLI Arguments** - Runtime overrides

```
Priority (highest to lowest):
CLI Arguments > Environment Variables > YAML Config > Default Values
```

## Environment Variables (.env)

### Required Keys

```env
# LLM Provider (Required)
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### Recommended Keys

```env
# Search (Recommended for better results)
TAVILY_API_KEY=tvly-...
```

### Optional Keys

```env
# Financial Data
ALPHA_VANTAGE_API_KEY=...
FMP_API_KEY=...
FINNHUB_API_KEY=...
POLYGON_API_KEY=...

# News
GNEWS_API_KEY=...
NEWSAPI_API_KEY=...
MEDIASTACK_API_KEY=...

# Company Data
HUNTER_API_KEY=...
GITHUB_TOKEN=...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...

# Observability
AGENTOPS_API_KEY=...
LANGSMITH_API_KEY=...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=company-researcher

# OpenAI (Fallback LLM)
OPENAI_API_KEY=...
```

## Python Configuration (config.py)

**Location**: `src/company_researcher/config.py`

### ResearchConfig Class

```python
@dataclass
class ResearchConfig:
    # API Keys
    anthropic_api_key: str
    tavily_api_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None
    fmp_api_key: Optional[str] = None

    # Model Settings
    llm_model: str = "claude-3-5-sonnet-20241022"
    llm_temperature: float = 0.0
    llm_max_tokens: int = 4096

    # Search Settings
    num_search_queries: int = 3
    max_search_results: int = 10
    search_strategy: str = "free_first"

    # Quality Settings
    quality_threshold: float = 85.0
    max_iterations: int = 2

    # Agent Settings (50+ parameters)
    researcher_max_tokens: int = 1000
    analyst_max_tokens: int = 2000
    financial_max_tokens: int = 2000
    market_max_tokens: int = 1500
    product_max_tokens: int = 1500
    synthesizer_max_tokens: int = 4000

    # Output Settings
    output_dir: str = "outputs/research"
    report_formats: List[str] = field(default_factory=lambda: ["md"])

    # Observability
    enable_agentops: bool = False
    enable_langsmith: bool = False
```

### Loading Configuration

```python
from company_researcher.config import ResearchConfig

# Load from environment
config = ResearchConfig.from_env()

# Override with YAML
config = config.merge_yaml("research_config.yaml")

# Override with CLI args
config = config.override(
    llm_model="claude-3-haiku-20240307",
    max_iterations=1
)
```

## YAML Configuration (research_config.yaml)

**Location**: `scripts/research/research_config.yaml`

### Full Configuration File

```yaml
# Research Configuration

# Research depth: quick, standard, comprehensive
depth: standard

# LLM Settings
llm:
  model: claude-3-5-sonnet-20241022
  temperature: 0.0
  max_tokens: 4096

# Search Settings
search:
  strategy: free_first  # free_first, auto, tavily_only
  num_queries: 3
  max_results: 10
  min_free_sources: 20
  tavily_refinement: true
  include_domains: []
  exclude_domains:
    - pinterest.com
    - instagram.com

# Quality Settings
quality:
  threshold: 85.0
  min_sections: 6
  require_financials: true

# Gap Filling
gap_filling:
  enabled: true
  max_iterations: 2
  min_quality_score: 85.0

# Output Settings
output:
  formats:
    - md
    - pdf  # Requires reportlab
    - excel  # Requires openpyxl
  base_dir: outputs/research
  sections:
    - executive_summary
    - company_overview
    - financials
    - market_position
    - competitive_analysis
    - strategy
    - sources

# Caching
cache:
  enabled: true
  ttl_days: 7
  directory: .research_cache

# Agent-Specific Settings
agents:
  researcher:
    max_tokens: 1000
    temperature: 0.0
  financial:
    max_tokens: 2000
    temperature: 0.0
    external_sources:
      - yfinance
      - alpha_vantage
      - fmp
  market:
    max_tokens: 1500
    temperature: 0.0
  product:
    max_tokens: 1500
    temperature: 0.0
  synthesizer:
    max_tokens: 4000
    temperature: 0.0

# Financial Data Sources
financial:
  primary: yfinance
  fallback:
    - alpha_vantage
    - fmp
  cache_ttl: 3600  # 1 hour

# News Settings
news:
  lookback_days: 30
  max_articles: 20
  sources:
    - gnews
    - newsapi

# Rate Limits (per minute)
rate_limits:
  tavily: 100
  duckduckgo: 10
  alpha_vantage: 5
  fmp: 10

# Timeouts (seconds)
timeouts:
  search: 30
  financial: 30
  llm: 120
  total: 600  # 10 minutes max

# Logging
logging:
  level: INFO
  format: structured
  file: logs/research.log
```

## Configuration by Use Case

### Quick Research (Minimal Cost)

```yaml
depth: quick
search:
  strategy: free_first
  max_results: 5
gap_filling:
  enabled: false
output:
  formats: [md]
```

### Standard Research (Balanced)

```yaml
depth: standard
search:
  strategy: free_first
  tavily_refinement: true
gap_filling:
  enabled: true
  max_iterations: 2
output:
  formats: [md]
```

### Comprehensive Research (Maximum Quality)

```yaml
depth: comprehensive
search:
  strategy: auto
  max_results: 20
gap_filling:
  enabled: true
  max_iterations: 3
quality:
  threshold: 90.0
output:
  formats: [md, pdf, excel]
```

### Cost-Optimized (Budget Limit)

```python
# config.py
max_cost_per_research: float = 0.10  # $0.10 max
llm_model: str = "claude-3-haiku-20240307"  # Cheaper model
```

## CLI Configuration

```bash
# Override config via CLI
python scripts/research/cli.py research "Microsoft" \
    --depth comprehensive \
    --format pdf \
    --iterations 3 \
    --quality-threshold 90

# Use custom config file
python scripts/research/cli.py research "Microsoft" \
    --config my_config.yaml

# Disable caching
python scripts/research/cli.py research "Microsoft" \
    --no-cache

# Verbose logging
python scripts/research/cli.py research "Microsoft" \
    --verbose
```

## Configuration Validation

```python
from company_researcher.config import validate_config

config = ResearchConfig.from_env()

# Validate configuration
errors = validate_config(config)
if errors:
    for error in errors:
        print(f"Config error: {error}")
    sys.exit(1)
```

### Validation Rules

| Check | Validation |
|-------|------------|
| API Key | ANTHROPIC_API_KEY is set |
| Model | Model is valid Claude model |
| Thresholds | quality_threshold between 0-100 |
| Iterations | max_iterations >= 1 |
| Output Dir | output_dir is writable |

## Environment-Specific Config

### Development

```env
# .env.development
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-3-haiku-20240307  # Cheaper
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=...
```

### Production

```env
# .env.production
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-3-5-sonnet-20241022
AGENTOPS_API_KEY=...
ENABLE_COST_TRACKING=true
```

---

**Related Documentation**:
- [Installation Guide](../01-overview/INSTALLATION.md)
- [Integrations](../05-integrations/)
- [Deployment](../11-deployment/)

---

**Last Updated**: December 2024
