# Provider Hierarchy & Cost Optimization Guide

This document describes the cost-optimized provider architecture that reduces API costs by ~90%.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    COST OPTIMIZATION LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐        │
│  │ SearchRouter │   │ScrapingRouter│   │  NewsRouter  │        │
│  │              │   │              │   │              │        │
│  │ DuckDuckGo   │   │  Crawl4AI    │   │ Google RSS   │        │
│  │     ↓        │   │     ↓        │   │     ↓        │        │
│  │  Serper      │   │ Jina Reader  │   │   GNews      │        │
│  │     ↓        │   │     ↓        │   │     ↓        │        │
│  │  Tavily      │   │  Firecrawl   │   │  NewsAPI     │        │
│  └──────────────┘   └──────────────┘   └──────────────┘        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    CostTracker                            │  │
│  │  - Real-time cost tracking per provider                   │  │
│  │  - Daily/monthly budget alerts                            │  │
│  │  - Cost optimization recommendations                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Provider Tiers

### FREE Tier ($0/request)
| Provider | Category | Use Case |
|----------|----------|----------|
| DuckDuckGo | Search | Bulk/low-priority searches |
| Crawl4AI | Scraping | Most web pages, JS rendering |
| Jina Reader | Scraping | Quick markdown conversion |
| Google News RSS | News | Unlimited news queries |
| Wikipedia | Company Data | Company overviews |
| SEC EDGAR | Financial | US public company filings |
| Nominatim | Geocoding | OpenStreetMap geocoding |

### CHEAP Tier (<$0.001/request)
| Provider | Category | Cost | Use Case |
|----------|----------|------|----------|
| Serper.dev | Search | $0.001/query | Quality Google search |
| DeepSeek | LLM | $0.14/1M tokens | Drafts, analysis |
| Groq Llama | LLM | $0.05-0.59/1M | Fast inference |
| GPT-4o-mini | LLM | $0.15/1M | Simple tasks |

### STANDARD Tier ($0.001-$0.01/request)
| Provider | Category | Cost | Use Case |
|----------|----------|------|----------|
| Tavily | Search | $0.005/query | Quality-critical |
| NewsAPI | News | $0.003/req | Best news quality |
| GNews | News | $0.003/req | Good news results |
| FMP | Financial | $0.004/req | Financial data |
| Finnhub | Financial | Free tier | Real-time quotes |

### PREMIUM Tier (>$0.01/request)
| Provider | Category | Cost | Use Case |
|----------|----------|------|----------|
| Claude 3.5 Sonnet | LLM | $15/1M tokens | Final outputs |
| GPT-4o | LLM | $15/1M tokens | Complex reasoning |
| Firecrawl | Scraping | $0.01/page | Anti-bot, complex JS |
| ScrapeGraph | Scraping | $0.01/page | AI extraction |

---

## Smart Routers

### SearchRouter
Routes search requests based on quality requirements.

```python
from company_researcher.integrations import get_search_router, SearchQuality

router = get_search_router()

# FREE: DuckDuckGo only
results = await router.search("Tesla news", quality=SearchQuality.FREE)

# STANDARD: DuckDuckGo → Serper → Tavily (fallback)
results = await router.search("Tesla financials", quality=SearchQuality.STANDARD)

# PREMIUM: Tavily first for best quality
results = await router.search("SEC filing analysis", quality=SearchQuality.PREMIUM)
```

### ScrapingRouter
Routes scraping requests with automatic fallback.

```python
from company_researcher.integrations import get_scraping_router, ScrapingQuality

router = get_scraping_router()

# FREE: Crawl4AI → Jina (fallback)
result = await router.scrape("https://example.com", quality=ScrapingQuality.FREE)

# STANDARD: Crawl4AI → Jina → Firecrawl (fallback)
result = await router.scrape("https://complex-site.com", quality=ScrapingQuality.STANDARD)

# Sync version
result = router.scrape_sync("https://example.com")
```

### NewsRouter
Routes news searches with quota management.

```python
from company_researcher.integrations import get_news_router, NewsQuality

router = get_news_router()

# FREE: Google News RSS only
results = await router.search("Apple earnings", quality=NewsQuality.FREE)

# STANDARD: Google RSS → GNews → NewsAPI → Mediastack
results = await router.search("Apple earnings", quality=NewsQuality.STANDARD)

# Get quota status
print(router.get_quota_status())
```

---

## Cost Tracker

Unified cost tracking across all providers.

```python
from company_researcher.integrations import (
    get_cost_tracker,
    track_cost,
    print_cost_summary
)

# Initialize tracker
tracker = get_cost_tracker(daily_budget=10.0, monthly_budget=200.0)

# Track usage
tracker.track("tavily", units=5)  # 5 searches
tracker.track_llm("claude-3-5-sonnet", input_tokens=5000, output_tokens=2000)

# Get summary
summary = tracker.get_summary()
print(f"Today: ${summary['daily']['cost']:.4f}")
print(f"This month: ${summary['monthly']['cost']:.4f}")

# Get recommendations
for rec in tracker.get_recommendations():
    print(f"- {rec}")

# Print formatted summary
print_cost_summary()
```

### Budget Alerts

```python
from company_researcher.integrations import CostAlert, get_cost_tracker

tracker = get_cost_tracker()

# Custom alert
tracker.add_alert(CostAlert(
    name="llm_high_usage",
    threshold=5.0,  # $5
    category=ProviderCategory.LLM,
    period="daily",
    callback=lambda current, threshold: print(f"LLM spending high: ${current:.2f}")
))
```

---

## Integration Examples

### Basic Research with Cost Optimization

```python
from company_researcher.integrations import (
    get_search_router,
    get_news_router,
    get_scraping_router,
    get_cost_tracker,
    SearchQuality,
    NewsQuality,
    ScrapingQuality
)

async def research_company_optimized(company_name: str):
    """Research a company using cost-optimized providers."""

    search = get_search_router()
    news = get_news_router()
    scraper = get_scraping_router()
    costs = get_cost_tracker()

    # 1. Search (FREE first)
    search_results = await search.search(
        f"{company_name} company information",
        quality=SearchQuality.STANDARD  # Free first, paid fallback
    )

    # 2. Get news (FREE Google RSS)
    news_results = await news.search(
        company_name,
        quality=NewsQuality.FREE  # Free only
    )

    # 3. Scrape key URLs (FREE Crawl4AI)
    for result in search_results.results[:3]:
        scraped = await scraper.scrape(
            result.url,
            quality=ScrapingQuality.FREE
        )

    # 4. Print cost summary
    costs.print_summary()
```

### Batch Processing

```python
# Scrape multiple URLs concurrently (max 5 concurrent)
urls = [
    "https://company1.com/about",
    "https://company2.com/about",
    "https://company3.com/about",
]
results = await scraper.scrape_batch(urls, quality=ScrapingQuality.FREE)

# Search multiple queries
queries = ["Tesla financials", "Tesla competitors", "Tesla news"]
results = await search.search_batch(queries, quality=SearchQuality.STANDARD)
```

---

## Cost Comparison

### Before (All Paid)
| Operation | Provider | Cost/Request | Monthly (1000 req) |
|-----------|----------|--------------|-------------------|
| Search | Tavily | $0.005 | $150 |
| Scraping | Firecrawl | $0.010 | $300 |
| News | NewsAPI | $0.003 | $90 |
| **Total** | | | **$540/month** |

### After (Cost Optimized)
| Operation | Provider | Cost/Request | Monthly (1000 req) |
|-----------|----------|--------------|-------------------|
| Search | DuckDuckGo (80%) | $0.000 | $0 |
| Search | Serper (20%) | $0.001 | $6 |
| Scraping | Crawl4AI (90%) | $0.000 | $0 |
| Scraping | Firecrawl (10%) | $0.010 | $30 |
| News | Google RSS (100%) | $0.000 | $0 |
| **Total** | | | **$36/month** |

**Savings: ~93%**

---

## Configuration

### Environment Variables

```bash
# FREE (no key needed)
# - DuckDuckGo, Crawl4AI, Google News RSS, Wikipedia, SEC EDGAR

# CHEAP ($0.001/query)
SERPER_API_KEY=              # serper.dev

# STANDARD
TAVILY_API_KEY=              # tavily.com
NEWSAPI_KEY=                 # newsapi.org
GNEWS_API_KEY=               # gnews.io

# PREMIUM (use sparingly)
FIRECRAWL_API_KEY=           # firecrawl.dev
```

### Default Quality Levels

Set default quality in config:

```python
# config.py
SEARCH_DEFAULT_QUALITY = SearchQuality.STANDARD
SCRAPING_DEFAULT_QUALITY = ScrapingQuality.FREE
NEWS_DEFAULT_QUALITY = NewsQuality.FREE
```

---

## Migration Guide

### From Direct Tavily to SearchRouter

```python
# Before
from tavily import TavilyClient
client = TavilyClient(api_key=...)
results = client.search(query)

# After
from company_researcher.integrations import get_search_router
router = get_search_router()
results = await router.search(query)  # Auto-routes to cheapest
```

### From Direct Firecrawl to ScrapingRouter

```python
# Before
from firecrawl import FirecrawlApp
app = FirecrawlApp(api_key=...)
result = app.scrape_url(url)

# After
from company_researcher.integrations import get_scraping_router
router = get_scraping_router()
result = await router.scrape(url)  # Uses Crawl4AI first (FREE)
```

### From NewsAPI to NewsRouter

```python
# Before
from newsapi import NewsApiClient
api = NewsApiClient(api_key=...)
results = api.get_everything(q=query)

# After
from company_researcher.integrations import get_news_router
router = get_news_router()
results = await router.search(query)  # Uses Google RSS first (FREE)
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `integrations/search_router.py` | Smart search routing |
| `integrations/scraping_router.py` | Smart scraping routing |
| `integrations/news_router.py` | Smart news routing |
| `integrations/cost_tracker.py` | Unified cost tracking |
| `integrations/serper_client.py` | Serper.dev client |
| `integrations/crawl4ai_client.py` | Crawl4AI client |
| `integrations/jina_reader.py` | Jina Reader client |
| `integrations/google_news_rss.py` | Google News RSS client |
| `integrations/sec_edgar.py` | SEC EDGAR client |
| `integrations/wikipedia_client.py` | Wikipedia client |

---

## Best Practices

1. **Always use routers** - Don't call providers directly
2. **Start with FREE** - Only upgrade quality if needed
3. **Monitor costs** - Check `print_cost_summary()` regularly
4. **Set budgets** - Configure daily/monthly limits
5. **Cache results** - All routers cache by default
6. **Use batch operations** - More efficient than individual calls

---

## Troubleshooting

### "All providers failed"
- Check API keys are set correctly
- Verify network connectivity
- Check provider quotas

### High costs despite optimization
- Review quality settings (should be FREE/STANDARD)
- Check for code bypassing routers
- Verify caching is enabled

### Missing data
- Try upgrading quality level
- Check if specific provider has better coverage
- Use `force_provider` parameter for testing
