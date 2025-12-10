# External Integrations

This section documents all external API integrations used by the Company Researcher.

## Overview

The system integrates with 20+ external services for data collection:

```
INTEGRATIONS
    |
    +-- Search Providers
    |   +-- Tavily (Primary)
    |   +-- DuckDuckGo (Fallback)
    |   +-- Firecrawl
    |   +-- ScrapeGraph
    |
    +-- Financial Data
    |   +-- yfinance (Free)
    |   +-- Alpha Vantage
    |   +-- Financial Modeling Prep
    |   +-- Finnhub
    |   +-- Polygon.io
    |   +-- SEC EDGAR
    |
    +-- News & Media
    |   +-- GNews
    |   +-- NewsAPI
    |   +-- Mediastack
    |
    +-- Company Data
    |   +-- Hunter.io
    |   +-- Domainsdb
    |   +-- GitHub API
    |   +-- Reddit API
    |
    +-- LLM Providers
    |   +-- Anthropic (Claude)
    |   +-- OpenAI (Fallback)
    |
    +-- Observability
        +-- AgentOps
        +-- LangSmith
```

## Integration Categories

| Category | Primary Provider | Fallback | Documentation |
|----------|------------------|----------|---------------|
| Web Search | Tavily | DuckDuckGo | [Search](search/) |
| Financial | yfinance | Alpha Vantage, FMP | [Financial](financial/) |
| News | GNews | NewsAPI | [News](news/) |
| Company | Hunter.io | Domainsdb | [Company Data](company-data/) |
| LLM | Claude | OpenAI | [LLM Setup](../llm-setup.md) |

## Quick Reference

### API Keys Required

| Service | Environment Variable | Required | Free Tier |
|---------|---------------------|----------|-----------|
| Anthropic | `ANTHROPIC_API_KEY` | Yes | No |
| Tavily | `TAVILY_API_KEY` | Recommended | 1000/month |
| Alpha Vantage | `ALPHA_VANTAGE_API_KEY` | Optional | 25/day |
| FMP | `FMP_API_KEY` | Optional | 250/day |
| Finnhub | `FINNHUB_API_KEY` | Optional | 60/min |
| GNews | `GNEWS_API_KEY` | Optional | 100/day |
| AgentOps | `AGENTOPS_API_KEY` | Optional | 500/month |

### Setting Up Keys

```bash
# Copy example file
cp env.example .env

# Edit with your keys
ANTHROPIC_API_KEY=sk-ant-api03-...
TAVILY_API_KEY=tvly-...
ALPHA_VANTAGE_API_KEY=...
```

## Integration Architecture

### Client Factory Pattern

```python
# integrations/__init__.py

def get_search_client(config: ResearchConfig) -> SearchClient:
    """Get search client with fallback."""
    if config.tavily_api_key:
        return TavilyClient(config)
    return DuckDuckGoClient()

def get_financial_client(config: ResearchConfig) -> FinancialClient:
    """Get financial client with fallback chain."""
    clients = []
    clients.append(YFinanceClient())  # Always available
    if config.alpha_vantage_api_key:
        clients.append(AlphaVantageClient(config))
    if config.fmp_api_key:
        clients.append(FMPClient(config))
    return ChainedFinancialClient(clients)
```

### Fallback Chain

```python
async def search_with_fallback(query: str) -> List[Dict]:
    """Search with automatic fallback."""
    providers = [
        ("tavily", tavily_search),
        ("duckduckgo", duckduckgo_search),
    ]

    for name, provider in providers:
        try:
            results = await provider(query)
            if results:
                return results
        except Exception as e:
            logger.warning(f"{name} failed: {e}")

    return []  # Empty results, don't fail
```

### Rate Limiting

```python
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=5, period=1)  # 5 calls per second
async def rate_limited_search(query: str) -> List[Dict]:
    """Rate-limited search call."""
    return await tavily_search(query)
```

## Integration Summaries

### Search Providers

| Provider | Strengths | Limitations |
|----------|-----------|-------------|
| **Tavily** | LLM-optimized, clean results | Paid after free tier |
| **DuckDuckGo** | Free, no API key | Rate limited, less clean |
| **Firecrawl** | Deep scraping, JS rendering | Paid, slower |
| **ScrapeGraph** | AI extraction | Paid |

### Financial Data

| Provider | Data Types | Best For |
|----------|------------|----------|
| **yfinance** | Stock prices, basic financials | Quick lookups, free |
| **Alpha Vantage** | Fundamentals, statements | Detailed financials |
| **FMP** | Comprehensive data | Full financial analysis |
| **SEC EDGAR** | Official filings | Public US companies |

### News Sources

| Provider | Coverage | Updates |
|----------|----------|---------|
| **GNews** | Google News aggregation | Real-time |
| **NewsAPI** | 80,000+ sources | Near real-time |
| **Mediastack** | 7,500+ sources | Real-time |

## Configuration

### Per-Integration Settings

```python
# config.py

# Search settings
tavily_max_results: int = 10
tavily_include_domains: List[str] = []
tavily_exclude_domains: List[str] = []

# Financial settings
financial_data_timeout: int = 30
financial_cache_ttl: int = 3600  # 1 hour

# News settings
news_lookback_days: int = 30
news_max_articles: int = 20
```

### Timeout Configuration

```python
# All integrations have configurable timeouts
INTEGRATION_TIMEOUTS = {
    "tavily": 30,
    "duckduckgo": 20,
    "alpha_vantage": 30,
    "fmp": 30,
    "gnews": 15,
}
```

## Adding New Integrations

### Step 1: Create Client

```python
# integrations/new_service.py

class NewServiceClient:
    def __init__(self, config: ResearchConfig):
        self.api_key = config.new_service_api_key
        self.base_url = "https://api.newservice.com"

    async def fetch_data(self, query: str) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/search",
                params={"q": query},
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.json()
```

### Step 2: Add Configuration

```python
# config.py

new_service_api_key: Optional[str] = Field(
    default=None,
    env="NEW_SERVICE_API_KEY"
)
```

### Step 3: Register in Factory

```python
# integrations/__init__.py

def get_new_service_client(config: ResearchConfig) -> Optional[NewServiceClient]:
    if config.new_service_api_key:
        return NewServiceClient(config)
    return None
```

## Documentation Index

| Document | Description |
|----------|-------------|
| [Search Providers](search/) | Web search integrations |
| [Financial Data](financial/) | Financial API clients |
| [News Sources](news/) | News API integrations |
| [Company Data](company-data/) | Company information APIs |

---

**Related Documentation**:
- [Configuration Guide](../06-configuration/)
- [Agent Documentation](../03-agents/)

---

**Last Updated**: December 2024
