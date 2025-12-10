# Integration Patterns

Documentation of external API integration strategies, fallback mechanisms, and selection logic.

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    INTEGRATION LAYER                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   SEARCH     │  │  FINANCIAL   │  │    NEWS      │       │
│  │  PROVIDERS   │  │    DATA      │  │   SOURCES    │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │                │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐       │
│  │  - Tavily    │  │  - yfinance  │  │  - GNews     │       │
│  │  - DuckDuckGo│  │  - Alpha V.  │  │  - NewsAPI   │       │
│  │              │  │  - FMP       │  │  - Mediastack│       │
│  │              │  │  - Finnhub   │  │              │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   COMPANY    │  │   GEO/MAP    │  │    ML/AI     │       │
│  │    DATA      │  │    DATA      │  │   SERVICES   │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │                │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐       │
│  │  - Hunter.io │  │  - OpenCage  │  │  - HuggingF. │       │
│  │  - DomainsDB │  │  - Nominatim │  │              │       │
│  │  - GitHub    │  │              │  │              │       │
│  │  - Reddit    │  │              │  │              │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Search Provider Strategy

### Primary: Tavily

**Configuration**: `TAVILY_API_KEY`

**Characteristics**:
- LLM-optimized results (content summarized for AI)
- Cost: ~$0.001 per query
- Speed: 2-5 seconds
- Quality: Excellent for company research

**Usage**:
```python
from tavily import TavilyClient

client = TavilyClient(api_key=config.tavily_api_key)
results = client.search(
    query=query,
    max_results=config.search_results_per_query
)
```

### Fallback: DuckDuckGo

**Configuration**: None (free, no API key)

**Characteristics**:
- Free, unlimited
- Speed: 1-3 seconds
- Quality: Good for general queries

**When Used**:
1. Tavily API key not configured
2. Tavily rate limit reached
3. Tavily timeout/error

**Fallback Logic**:
```python
def search(query: str) -> List[Dict]:
    try:
        if config.tavily_api_key:
            return tavily_search(query)
    except (TavilyError, Timeout):
        pass

    # Fallback to DuckDuckGo
    return duckduckgo_search(query)
```

---

## Financial Data Strategy

### Priority Order

```
1. yfinance       (free, best for public companies)
      ↓
2. Alpha Vantage  (API key required, 25 req/day free)
      ↓
3. FMP            (API key required, 250 req/day free)
      ↓
4. Finnhub        (API key required, 60 req/min free)
```

### Provider Selection Logic

```python
def get_financial_data(ticker: str) -> Dict:
    providers = [
        ("yfinance", yfinance_fetch, True),
        ("alpha_vantage", alpha_vantage_fetch, bool(config.alpha_vantage_api_key)),
        ("fmp", fmp_fetch, bool(config.fmp_api_key)),
        ("finnhub", finnhub_fetch, bool(config.finnhub_api_key)),
    ]

    combined_data = {}

    for name, fetch_fn, enabled in providers:
        if not enabled:
            continue

        try:
            data = fetch_fn(ticker)
            combined_data = merge_financial_data(combined_data, data)
        except Exception as e:
            logger.warning(f"{name} failed: {e}")
            continue

    return combined_data
```

### Data Priority

| Field | Primary Source | Fallback |
|-------|---------------|----------|
| Stock Price | yfinance | Finnhub |
| Market Cap | yfinance | FMP |
| Revenue | yfinance | Alpha Vantage |
| Earnings | Alpha Vantage | FMP |
| Ratios (P/E) | yfinance | FMP |
| Historical Data | yfinance | Polygon |

### yfinance Integration

**Cost**: Free

**Rate Limits**: Unofficial, ~2000 req/hour

```python
import yfinance as yf

def yfinance_fetch(ticker: str) -> Dict:
    stock = yf.Ticker(ticker)

    return {
        "info": stock.info,
        "financials": stock.financials,
        "balance_sheet": stock.balance_sheet,
        "cashflow": stock.cashflow,
        "dividends": stock.dividends,
        "splits": stock.splits,
    }
```

### Alpha Vantage Integration

**Cost**: Free tier (25 req/day), Premium available

```python
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData

def alpha_vantage_fetch(ticker: str) -> Dict:
    ts = TimeSeries(key=config.alpha_vantage_api_key)
    fd = FundamentalData(key=config.alpha_vantage_api_key)

    data, _ = ts.get_quote_endpoint(symbol=ticker)
    overview, _ = fd.get_company_overview(symbol=ticker)

    return {
        "quote": data,
        "overview": overview,
    }
```

---

## News Provider Strategy

### Provider Comparison

| Provider | Free Tier | Coverage | Quality |
|----------|-----------|----------|---------|
| GNews | 100 req/day | Global | Good |
| NewsAPI | 100 req/day (dev) | Excellent | Excellent |
| Mediastack | 500 req/month | Global | Good |

### Selection Logic

```python
def get_news(company_name: str) -> List[Dict]:
    # Try providers in order of preference
    if config.newsapi_key:
        try:
            return newsapi_search(company_name)
        except NewsAPIError:
            pass

    if config.gnews_api_key:
        try:
            return gnews_search(company_name)
        except GNewsError:
            pass

    if config.mediastack_api_key:
        try:
            return mediastack_search(company_name)
        except MediastackError:
            pass

    # Fallback to web search for news
    return tavily_search(f"{company_name} news")
```

---

## Company Data Integrations

### Hunter.io (Email/Domain Intelligence)

**Cost**: 25 searches/month free

**Use Case**: Find company domain, employee emails

```python
def hunter_fetch(domain: str) -> Dict:
    url = f"https://api.hunter.io/v2/domain-search"
    params = {
        "domain": domain,
        "api_key": config.hunter_api_key
    }

    response = requests.get(url, params=params)
    return response.json()
```

### DomainsDB (Domain Info)

**Cost**: Free (no API key)

**Use Case**: Verify domain ownership, find related domains

```python
def domainsdb_fetch(domain: str) -> Dict:
    url = f"https://api.domainsdb.info/v1/domains/search"
    params = {"domain": domain}

    response = requests.get(url, params=params)
    return response.json()
```

### GitHub (Tech Stack Detection)

**Cost**: 5000 req/hour (authenticated)

**Use Case**: Analyze company's open source presence

```python
def github_fetch(company_name: str) -> Dict:
    headers = {"Authorization": f"token {config.github_token}"}

    # Search for organization
    search_url = f"https://api.github.com/search/users?q={company_name}+type:org"
    response = requests.get(search_url, headers=headers)

    return response.json()
```

### Reddit (Sentiment, Discussions)

**Cost**: 100 req/min (OAuth)

**Use Case**: Employee sentiment, product discussions

```python
def reddit_fetch(company_name: str) -> Dict:
    reddit = praw.Reddit(
        client_id=config.reddit_client_id,
        client_secret=config.reddit_client_secret,
        user_agent="CompanyResearcher/1.0"
    )

    # Search relevant subreddits
    subreddits = ["stocks", "investing", "technology"]
    posts = []

    for sub in subreddits:
        results = reddit.subreddit(sub).search(company_name, limit=10)
        posts.extend(results)

    return {"posts": posts}
```

---

## Geocoding Integrations

### OpenCage

**Cost**: 2,500 req/day free

**Use Case**: Convert addresses to coordinates

```python
def opencage_geocode(address: str) -> Dict:
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        "q": address,
        "key": config.opencage_api_key
    }

    response = requests.get(url, params=params)
    return response.json()["results"][0]
```

### Nominatim (OpenStreetMap)

**Cost**: Free (1 req/sec rate limit)

**Use Case**: Free geocoding fallback

```python
def nominatim_geocode(address: str) -> Dict:
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json"
    }

    response = requests.get(url, params=params)
    return response.json()[0]
```

---

## LLM Integration

### Primary: Anthropic (Claude)

**Models Used**:
| Model | Use Case | Cost |
|-------|----------|------|
| claude-3-5-haiku | Default analysis | $0.80/$4.00 per 1M |
| claude-3-5-sonnet | Complex analysis | $3.00/$15.00 per 1M |

**Client Factory Pattern**:
```python
from anthropic import Anthropic

def get_anthropic_client() -> Anthropic:
    return Anthropic(api_key=config.anthropic_api_key)

def safe_extract_text(response, agent_name: str) -> str:
    """Safely extract text from Claude response."""
    if response.content and len(response.content) > 0:
        return response.content[0].text
    return ""
```

### Error Handling

```python
def call_llm(prompt: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=config.llm_model,
                max_tokens=config.llm_max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return safe_extract_text(response)

        except anthropic.RateLimitError:
            wait_time = 2 ** attempt
            time.sleep(wait_time)

        except anthropic.APIError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(1)

    raise Exception("Max retries exceeded")
```

---

## Observability Integrations

### AgentOps

**Purpose**: Agent execution tracking

```python
import agentops

if config.agentops_api_key:
    agentops.init(api_key=config.agentops_api_key)

    @agentops.track_agent(name="researcher")
    def researcher_agent(state):
        # Agent implementation
        pass
```

### LangSmith

**Purpose**: LLM call tracing

```python
# Environment variables
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = config.langsmith_api_key
os.environ["LANGCHAIN_PROJECT"] = config.langchain_project

# Automatic tracing enabled for LangChain/LangGraph calls
```

---

## Timeout & Retry Strategy

### Timeout Configuration

| Integration Type | Connect Timeout | Read Timeout |
|-----------------|-----------------|--------------|
| Search APIs | 10s | 30s |
| Financial APIs | 10s | 60s |
| LLM APIs | 10s | 60s |
| Web Scraping | 10s | 10s |

### Retry Strategy

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def api_call_with_retry(func, *args, **kwargs):
    return func(*args, **kwargs)
```

### Circuit Breaker Pattern

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.state = "CLOSED"
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitOpenError()

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
```

---

## Rate Limiting

### Rate Limit Tracking

```python
class RateLimitTracker:
    def __init__(self):
        self.limits = {
            "tavily": {"calls": 0, "limit": 1000, "reset": "daily"},
            "alpha_vantage": {"calls": 0, "limit": 25, "reset": "daily"},
            "newsapi": {"calls": 0, "limit": 100, "reset": "daily"},
            "gnews": {"calls": 0, "limit": 100, "reset": "daily"},
        }

    def can_call(self, provider: str) -> bool:
        limit_info = self.limits.get(provider)
        if not limit_info:
            return True
        return limit_info["calls"] < limit_info["limit"]

    def record_call(self, provider: str):
        if provider in self.limits:
            self.limits[provider]["calls"] += 1
```

### Rate Limit Response Handling

```python
def handle_rate_limit(response):
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 60))
        raise RateLimitExceeded(retry_after=retry_after)
```

---

## Data Merging Strategy

### Financial Data Merging

```python
def merge_financial_data(existing: Dict, new: Dict) -> Dict:
    """
    Merge financial data from multiple providers.

    Priority:
    1. More recent data wins
    2. More specific data wins
    3. Official sources win
    """
    merged = existing.copy()

    for key, value in new.items():
        if key not in merged:
            merged[key] = value
        elif is_more_recent(value, merged[key]):
            merged[key] = value
        elif is_more_specific(value, merged[key]):
            merged[key] = value

    return merged
```

### Source Deduplication

```python
def deduplicate_sources(sources: List[Dict]) -> List[Dict]:
    """Remove duplicate sources based on URL."""
    seen_urls = set()
    unique = []

    for source in sources:
        url = normalize_url(source.get("url", ""))
        if url not in seen_urls:
            seen_urls.add(url)
            unique.append(source)

    return unique
```

---

## Integration Testing

### Mock Responses

```python
@pytest.fixture
def mock_tavily():
    with patch("tavily.TavilyClient") as mock:
        mock.return_value.search.return_value = {
            "results": [
                {"title": "Test", "url": "https://test.com", "content": "..."}
            ]
        }
        yield mock
```

### Integration Health Check

```python
def check_integration_health() -> Dict[str, bool]:
    """Check availability of all integrations."""
    health = {}

    # Search
    health["tavily"] = check_tavily()
    health["duckduckgo"] = check_duckduckgo()

    # Financial
    health["yfinance"] = check_yfinance()
    health["alpha_vantage"] = check_alpha_vantage()

    # LLM
    health["anthropic"] = check_anthropic()

    return health
```

---

**Related Documentation**:
- [Search Providers](search/README.md)
- [Financial APIs](financial/README.md)
- [Configuration](../06-configuration/README.md)

---

**Last Updated**: December 2024
