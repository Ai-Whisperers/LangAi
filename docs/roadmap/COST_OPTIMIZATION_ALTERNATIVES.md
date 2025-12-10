# Cost Optimization: Cheaper & Free Alternatives

This document identifies all cost centers in the project and recommends cheaper alternatives.

## Summary of Potential Savings

| Category | Current Est. Cost | With Alternatives | Savings |
|----------|-------------------|-------------------|---------|
| LLM Providers | $500-2000/mo | $50-200/mo | 80-90% |
| Search APIs | $100-500/mo | $0-50/mo | 90%+ |
| Web Scraping | $50-200/mo | $0-20/mo | 90%+ |
| Financial Data | $0-100/mo | $0/mo | 100% |
| News APIs | $30-100/mo | $0/mo | 100% |
| Observability | $50-200/mo | $0/mo | 100% |
| **TOTAL** | **$730-3100/mo** | **$50-270/mo** | **~90%** |

---

## 1. Search APIs

### Current: Tavily (~$5/1K queries)

**Free Alternatives:**

#### DuckDuckGo (Already in project!)
```python
# Already configured in requirements.txt
from duckduckgo_search import DDGS

def free_search(query: str, max_results: int = 10):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
    return results
```
- Cost: FREE
- Rate limit: ~20-30 queries/minute
- Quality: Good for general search

#### Serper.dev ($50/50K queries = $0.001/query)
```python
# 10x cheaper than Tavily
import requests

def serper_search(query: str, api_key: str):
    response = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": api_key},
        json={"q": query}
    )
    return response.json()
```
- Cost: $50 for 50,000 queries
- Quality: Google results
- Speed: Fast

#### Brave Search API
```python
# Similar price to Tavily but with AI summaries
import requests

def brave_search(query: str, api_key: str):
    response = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={"X-Subscription-Token": api_key},
        params={"q": query}
    )
    return response.json()
```
- Cost: Free tier (2K/mo), then $5/1K
- Includes AI summaries

### Recommendation
```python
# Hybrid search strategy
def smart_search(query: str, quality_required: bool = False):
    if quality_required:
        return tavily_search(query)  # Use for important queries
    else:
        return duckduckgo_search(query)  # Free for bulk
```

---

## 2. Web Scraping

### Current: Firecrawl + ScrapeGraph (~$15-20/1K pages)

**Free Alternatives:**

#### Playwright (Already in project!)
```python
# requirements.txt: playwright==1.48.0
from playwright.async_api import async_playwright

async def free_scrape(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        content = await page.content()
        await browser.close()
    return content
```
- Cost: FREE
- Handles JavaScript rendering
- Can bypass many anti-bot measures

#### Crawl4AI (Open Source)
```bash
pip install crawl4ai
```
```python
from crawl4ai import WebCrawler

crawler = WebCrawler()
result = crawler.run(url="https://example.com")
print(result.markdown)  # LLM-ready output
```
- Cost: FREE, open source
- Returns markdown (like Firecrawl)
- Built-in LLM extraction

#### Jina Reader (Free tier)
```python
import requests

def jina_read(url: str) -> str:
    # Free: 1M tokens/month
    response = requests.get(f"https://r.jina.ai/{url}")
    return response.text  # Returns clean markdown
```
- Cost: FREE (1M tokens/month)
- Returns LLM-ready markdown
- No API key needed

### Recommendation
Use Playwright for general scraping, Jina Reader for quick markdown conversion.

---

## 3. Financial Data

### Current Mix: FMP, Finnhub, Polygon, Alpha Vantage

**yfinance is FREE and covers 90% of needs:**

```python
import yfinance as yf

def get_company_financials(ticker: str):
    stock = yf.Ticker(ticker)
    return {
        "info": stock.info,
        "financials": stock.financials,
        "balance_sheet": stock.balance_sheet,
        "cashflow": stock.cashflow,
        "earnings": stock.earnings,
        "recommendations": stock.recommendations
    }
```

**Comparison:**

| Source | Cost | Data Quality | Real-time |
|--------|------|--------------|-----------|
| yfinance | FREE | Good | 15-min delay |
| FMP | $15/mo+ | Excellent | Yes |
| Finnhub | $0+ | Good | Yes |
| SEC EDGAR | FREE | Official filings | N/A |

### Recommendation
```python
# Use yfinance as primary, others as fallback
def get_financials(ticker: str):
    try:
        return yfinance_get(ticker)  # Free
    except:
        return fmp_get(ticker)  # Paid fallback
```

---

## 4. News APIs

### Current: NewsAPI, GNews, Mediastack

**Free Alternatives:**

#### Google News RSS (Completely FREE)
```python
import feedparser

def google_news_search(query: str) -> list:
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    return [
        {
            "title": entry.title,
            "link": entry.link,
            "published": entry.published
        }
        for entry in feed.entries
    ]
```
- Cost: FREE
- No API key
- Unlimited queries

#### Tavily Already Includes News
If using Tavily for search, news is included. No need for separate news API.

#### The News API (Generous free tier)
```python
# 100 requests/day free
import requests

def thenewsapi_search(query: str, api_key: str):
    response = requests.get(
        "https://api.thenewsapi.com/v1/news/all",
        params={"api_token": api_key, "search": query}
    )
    return response.json()
```

### Recommendation
Use Google News RSS (free) for bulk, Tavily for integrated results.

---

## 5. Observability

### Current: LangSmith ($39/mo+), AgentOps

**Free Alternatives:**

#### Langfuse (FREE, Open Source)
```bash
pip install langfuse
```
```python
from langfuse import Langfuse
from langfuse.callback import CallbackHandler

# Initialize
langfuse = Langfuse(
    public_key="pk-lf-...",
    secret_key="sk-lf-...",
    host="https://cloud.langfuse.com"  # Or self-host
)

# Use with LangChain
handler = CallbackHandler()
# Pass to LangChain as callback
```
- Cost: FREE cloud tier, or self-host
- Full LangSmith replacement
- Open source

#### OpenTelemetry + Jaeger (FREE)
```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Free distributed tracing
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("llm_call"):
    response = client.messages.create(...)
```
- Cost: FREE
- Industry standard
- Self-hosted

#### Phoenix by Arize (FREE)
```bash
pip install arize-phoenix
```
- Cost: FREE
- LLM observability
- Local or cloud

### Recommendation
Replace LangSmith with Langfuse (free tier generous, or self-host).

---

## 6. Company Data

### Current: Hunter.io, Crunchbase (limited)

**Free Alternatives:**

#### OpenCorporates (Free API)
```python
import requests

def get_company_info(name: str):
    response = requests.get(
        f"https://api.opencorporates.com/v0.4/companies/search",
        params={"q": name}
    )
    return response.json()
```
- Cost: FREE tier available
- Official company registrations

#### SEC EDGAR (FREE)
```python
import requests

def get_sec_filings(cik: str):
    url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
    response = requests.get(url, headers={"User-Agent": "your@email.com"})
    return response.json()
```
- Cost: FREE
- All US public company filings
- Official source

#### Wikipedia API (FREE)
```python
import wikipedia

def get_company_summary(company_name: str):
    try:
        return wikipedia.summary(company_name)
    except:
        return None
```
- Cost: FREE
- Good for basic company info

### Recommendation
Combine SEC EDGAR (financials) + Wikipedia (overview) + OpenCorporates (legal).

---

## 7. Email/Contact Discovery

### Current: Hunter.io (25 free/mo)

**Alternatives:**

| Service | Free Tier | Paid |
|---------|-----------|------|
| Hunter.io | 25/mo | $49/mo |
| Apollo.io | 250/mo | $49/mo |
| Snov.io | 50/mo | $39/mo |
| RocketReach | 5/mo | $39/mo |
| Clearbit | 0 | Enterprise |

### Recommendation
Apollo.io has best free tier (250 credits/month vs Hunter's 25).

---

## 8. Geocoding

### Current: OpenCage (2,500/day free)

**Already Have Free Alternative:**
```python
# Nominatim is already configured in the project
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="company_researcher")
location = geolocator.geocode("1600 Amphitheatre Parkway")
```
- Cost: FREE
- 1 request/second limit
- Good for batch geocoding

---

## Implementation Priority

### Quick Wins (Implement This Week)

1. **Use DuckDuckGo for bulk search** - Already in project, just needs routing
2. **Use yfinance as primary** - Already in requirements
3. **Add Google News RSS** - 10 lines of code, completely free
4. **Use Nominatim for geocoding** - Already configured

### Medium Term (This Month)

1. **Replace LangSmith with Langfuse** - Free, similar features
2. **Add Crawl4AI** - Free Firecrawl alternative
3. **Add Serper.dev** - 10x cheaper than Tavily for quality search

### Consider Later

1. **Apollo.io** for better email discovery free tier
2. **Phoenix** for LLM observability
3. **Self-host Langfuse** for unlimited traces

---

## Environment Variables to Add

```bash
# Free/Cheaper alternatives
SERPER_API_KEY=           # $50/50K queries (optional)
LANGFUSE_PUBLIC_KEY=      # Free LangSmith alternative
LANGFUSE_SECRET_KEY=
JINA_API_KEY=             # Free 1M tokens/month (optional)

# Remove/reduce usage of:
# NEWSAPI_KEY             # Replace with Google News RSS
# MEDIASTACK_API_KEY      # Replace with Google News RSS
# OPENCAGE_API_KEY        # Use Nominatim instead
```

---

## Code Changes Required

### 1. Smart Search Router
```python
# src/company_researcher/integrations/search_router.py

def search(query: str, quality: str = "standard") -> list:
    """
    Route search to appropriate provider based on quality needs.

    quality options:
    - "free": DuckDuckGo (0 cost)
    - "standard": Serper ($0.001/query)
    - "premium": Tavily ($0.005/query)
    """
    if quality == "free":
        return duckduckgo_search(query)
    elif quality == "standard":
        return serper_search(query)
    else:
        return tavily_search(query)
```

### 2. Financial Data Priority
```python
# Update financial_provider.py fallback order

PROVIDER_PRIORITY = [
    "yfinance",      # FREE - use first
    "sec_edgar",     # FREE - official filings
    "fmp",           # 250/day free
    "finnhub",       # 60/min free
    "polygon",       # 5/min free - last resort
]
```

### 3. News Aggregator
```python
# Add free news sources

def get_news(company: str) -> list:
    results = []

    # Free: Google News RSS
    results.extend(google_news_rss(company))

    # Free: Included in Tavily search
    if tavily_available:
        results.extend(tavily_news(company))

    # Paid fallback only if needed
    if len(results) < 5:
        results.extend(gnews_search(company))

    return results
```

---

## Monthly Cost Comparison

### Before Optimization
| Service | Est. Monthly Cost |
|---------|-------------------|
| Claude (LLM) | $500-2000 |
| Tavily | $100-500 |
| Firecrawl | $50-100 |
| NewsAPI + GNews + Mediastack | $50-150 |
| LangSmith | $39-100 |
| FMP + Finnhub | $0-50 |
| Hunter.io | $0-50 |
| **TOTAL** | **$739-2950** |

### After Optimization
| Service | Est. Monthly Cost |
|---------|-------------------|
| Claude + DeepSeek/Groq (hybrid) | $50-200 |
| DuckDuckGo + Serper | $0-50 |
| Playwright + Crawl4AI | $0 |
| Google News RSS | $0 |
| Langfuse (free tier) | $0 |
| yfinance + SEC EDGAR | $0 |
| Apollo.io (free tier) | $0 |
| **TOTAL** | **$50-250** |

### **Potential Savings: 85-95%**
