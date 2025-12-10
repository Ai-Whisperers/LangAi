# Free & Self-Hosted Services Implementation Plan

This document outlines the plan to add free and self-hosted alternatives to reduce costs by ~90%.

## Overview

| Service | Replaces | Cost Savings | Priority | Effort |
|---------|----------|--------------|----------|--------|
| **Crawl4AI** | Firecrawl, ScrapeGraph | $50-200/mo | HIGH | Low |
| **Jina Reader** | Firecrawl | $50-100/mo | HIGH | Low |
| **Google News RSS** | NewsAPI, GNews, Mediastack | $50-150/mo | HIGH | Low |
| **Langfuse** | LangSmith | $39-100/mo | MEDIUM | Medium |
| **SEC EDGAR** | Financial APIs | $0-50/mo | MEDIUM | Low |
| **Serper.dev** | Tavily (partial) | $100-400/mo | MEDIUM | Low |
| **DuckDuckGo Router** | Tavily (bulk) | $100-400/mo | HIGH | Low |
| **Wikipedia API** | Company data | $0 | LOW | Low |
| **OpenCorporates** | Crunchbase | $0-100/mo | LOW | Medium |

**Total Estimated Savings: $400-1500/month**

---

## Phase 1: Web Scraping (Week 1)

### 1.1 Crawl4AI - FREE Firecrawl Alternative

**What it does:**
- Converts any webpage to LLM-ready markdown
- Handles JavaScript rendering
- Structured data extraction with schemas
- Async support for high performance
- 100% free and open source

**Installation:**
```bash
pip install crawl4ai
playwright install  # For browser automation
```

**Implementation Location:** `src/company_researcher/integrations/crawl4ai_client.py`

**Features to implement:**
- [x] Basic page scraping to markdown
- [x] JavaScript rendering support
- [x] Structured extraction with LLM
- [x] Multi-page crawling
- [x] Rate limiting and caching
- [x] Fallback integration with existing WebScraper

**STATUS: IMPLEMENTED** - See `src/company_researcher/integrations/crawl4ai_client.py`

**Usage pattern:**
```python
from crawl4ai import AsyncWebCrawler

async def scrape_to_markdown(url: str) -> str:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        return result.markdown
```

---

### 1.2 Jina Reader - FREE Markdown Conversion

**What it does:**
- Converts any URL to clean markdown instantly
- No API key required for basic usage
- 1M tokens/month free with API key
- Perfect for quick content extraction

**Implementation Location:** `src/company_researcher/integrations/jina_reader.py`

**Features to implement:**
- [ ] Basic URL to markdown
- [ ] Search functionality (r.jina.ai/search)
- [ ] Fact extraction (r.jina.ai/facts)
- [ ] Caching layer
- [ ] Rate limiting

**Usage pattern:**
```python
import requests

def jina_read(url: str) -> str:
    response = requests.get(f"https://r.jina.ai/{url}")
    return response.text
```

---

## Phase 2: News & Search (Week 1-2)

### 2.1 Google News RSS - FREE News

**What it does:**
- Free access to Google News
- No API key required
- Unlimited queries
- Real-time news

**Implementation Location:** `src/company_researcher/integrations/google_news_rss.py`

**Features to implement:**
- [ ] Topic search
- [ ] Company news search
- [ ] Geographic filtering
- [ ] Date filtering
- [ ] Result parsing and normalization

**Usage pattern:**
```python
import feedparser

def google_news_search(query: str, lang: str = "en") -> list:
    url = f"https://news.google.com/rss/search?q={query}&hl={lang}"
    feed = feedparser.parse(url)
    return feed.entries
```

---

### 2.2 DuckDuckGo Search Router - FREE Search

**What it does:**
- Route bulk/low-priority searches to free DuckDuckGo
- Already in project, just needs smart routing
- Save Tavily for quality-critical searches

**Implementation Location:** `src/company_researcher/integrations/search_router.py`

**Features to implement:**
- [ ] Quality-based routing (free/standard/premium)
- [ ] Automatic fallback on rate limits
- [ ] Cost tracking per provider
- [ ] Result normalization across providers

---

### 2.3 Serper.dev - 10x Cheaper Than Tavily

**What it does:**
- Google search results via API
- $50 for 50,000 queries ($0.001/query)
- 10x cheaper than Tavily
- High quality results

**Implementation Location:** `src/company_researcher/integrations/serper_client.py`

**Features to implement:**
- [ ] Web search
- [ ] News search
- [ ] Image search
- [ ] Cost tracking

---

## Phase 3: Observability (Week 2)

### 3.1 Langfuse - FREE LangSmith Alternative

**What it does:**
- Full LLM observability (traces, metrics, prompts)
- Free cloud tier (50K observations/month)
- Can self-host for unlimited usage
- Drop-in LangChain integration

**Installation:**
```bash
pip install langfuse
```

**Implementation Location:** `src/company_researcher/llm/langfuse_setup.py`

**Features to implement:**
- [ ] Trace initialization
- [ ] LangChain callback handler
- [ ] Custom span creation
- [ ] Cost tracking integration
- [ ] Prompt management
- [ ] Migration guide from LangSmith

**Self-hosting option:**
```bash
# Docker compose for self-hosted Langfuse
docker-compose up -d langfuse
```

---

## Phase 4: Financial & Company Data (Week 2-3)

### 4.1 SEC EDGAR - FREE US Company Filings

**What it does:**
- Official SEC filings for all US public companies
- 10-K, 10-Q, 8-K filings
- Financial statements
- Insider trading data
- 100% free, unlimited

**Implementation Location:** `src/company_researcher/integrations/sec_edgar.py`

**Features to implement:**
- [ ] Company search by name/ticker
- [ ] Filing retrieval (10-K, 10-Q, 8-K)
- [ ] Financial statement extraction
- [ ] Filing history
- [ ] XBRL data parsing

---

### 4.2 OpenCorporates - FREE Company Registry

**What it does:**
- Official company registrations worldwide
- 200M+ companies
- Free API tier
- Legal entity data

**Implementation Location:** `src/company_researcher/integrations/opencorporates.py`

**Features to implement:**
- [ ] Company search
- [ ] Officer/director lookup
- [ ] Filing history
- [ ] Jurisdiction data

---

### 4.3 Wikipedia API - FREE Company Overview

**What it does:**
- Company summaries and history
- Infobox data (founding date, HQ, employees)
- Related companies
- 100% free

**Implementation Location:** `src/company_researcher/integrations/wikipedia_client.py`

**Features to implement:**
- [ ] Company summary extraction
- [ ] Infobox parsing
- [ ] Related articles
- [ ] Multi-language support

---

## Phase 5: Self-Hosted Options (Week 3-4)

### 5.1 Self-Hosted Langfuse

**Benefits:**
- Unlimited traces (no 50K/month limit)
- Data stays on your infrastructure
- Custom retention policies
- ~$20-50/month on cloud VM

**Docker setup:**
```yaml
# docker-compose.langfuse.yml
version: '3.8'
services:
  langfuse:
    image: langfuse/langfuse:latest
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://...
      - NEXTAUTH_SECRET=...
```

---

### 5.2 Self-Hosted Qdrant (Vector DB)

**Benefits:**
- No cloud costs for vector storage
- Full control over data
- Already in requirements.txt

**Docker setup:**
```yaml
# docker-compose.qdrant.yml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage
```

---

### 5.3 Self-Hosted Redis (Caching)

**Benefits:**
- Free caching layer
- Already in requirements.txt
- Reduces API calls significantly

---

## Implementation Order

### Week 1 (High Impact, Low Effort)
1. **Crawl4AI client** - Replace Firecrawl for most scraping
2. **Jina Reader client** - Quick markdown conversion
3. **Google News RSS** - Replace paid news APIs
4. **DuckDuckGo router** - Route bulk searches to free

### Week 2 (Medium Impact)
5. **Serper.dev client** - 10x cheaper than Tavily
6. **Langfuse setup** - Replace LangSmith
7. **SEC EDGAR client** - Free US company data

### Week 3 (Polish & Extend)
8. **Wikipedia client** - Company overviews
9. **OpenCorporates client** - Legal entity data
10. **Search router** - Smart multi-provider routing

### Week 4 (Self-Hosting)
11. **Self-host Langfuse** - Unlimited observability
12. **Self-host Qdrant** - Free vector storage
13. **Docker compose setup** - One-command deployment

---

## File Structure

```
src/company_researcher/
├── integrations/
│   ├── __init__.py           # Update exports
│   ├── crawl4ai_client.py    # NEW - Free scraping
│   ├── jina_reader.py        # NEW - Free markdown
│   ├── google_news_rss.py    # NEW - Free news
│   ├── serper_client.py      # NEW - Cheap search
│   ├── sec_edgar.py          # NEW - Free SEC data
│   ├── opencorporates.py     # NEW - Free company data
│   ├── wikipedia_client.py   # NEW - Free overviews
│   └── search_router.py      # NEW - Smart routing
├── llm/
│   ├── langfuse_setup.py     # NEW - Free observability
│   └── ...
└── ...

docker/
├── docker-compose.yml        # Full stack
├── docker-compose.langfuse.yml
├── docker-compose.qdrant.yml
└── docker-compose.redis.yml
```

---

## Environment Variables to Add

```bash
# Free services (no key required)
# - Google News RSS: No key needed
# - Jina Reader: No key for basic, optional for higher limits
# - Wikipedia: No key needed
# - SEC EDGAR: No key needed

# Optional API keys for free tiers
JINA_API_KEY=              # Optional: 1M tokens/month free
SERPER_API_KEY=            # $50/50K queries
OPENCORPORATES_API_KEY=    # Free tier available

# Langfuse (free cloud or self-hosted)
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com  # Or self-hosted URL

# Self-hosted services
QDRANT_HOST=localhost
QDRANT_PORT=6333
REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## Requirements.txt Additions

```txt
# Free Web Scraping
crawl4ai>=0.3.0            # FREE - Firecrawl alternative
feedparser>=6.0.0          # FREE - RSS parsing (Google News)

# Free Observability
langfuse>=2.0.0            # FREE - LangSmith alternative

# Already included but ensure present:
# playwright>=1.48.0       # FREE - Browser automation
# beautifulsoup4>=4.12.0   # FREE - HTML parsing
# duckduckgo-search>=6.3.0 # FREE - Search
# wikipedia>=1.4.0         # FREE - Wikipedia API (add if not present)
```

---

## Migration Strategy

### From Firecrawl to Crawl4AI
```python
# Before (Firecrawl - PAID)
from firecrawl import FirecrawlApp
app = FirecrawlApp(api_key="...")
result = app.scrape_url(url)

# After (Crawl4AI - FREE)
from crawl4ai import AsyncWebCrawler
async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(url=url)
    markdown = result.markdown
```

### From LangSmith to Langfuse
```python
# Before (LangSmith)
from langsmith import Client
client = Client()

# After (Langfuse - FREE)
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
langfuse = Langfuse()
handler = CallbackHandler()  # Use with LangChain
```

### From NewsAPI to Google News RSS
```python
# Before (NewsAPI - PAID)
from newsapi import NewsApiClient
api = NewsApiClient(api_key="...")
results = api.get_everything(q="Tesla")

# After (Google News RSS - FREE)
import feedparser
feed = feedparser.parse(f"https://news.google.com/rss/search?q=Tesla")
results = feed.entries
```

---

## Cost Impact Summary

| Current Service | Monthly Cost | Replacement | New Cost | Savings |
|-----------------|--------------|-------------|----------|---------|
| Firecrawl | $50-100 | Crawl4AI | $0 | 100% |
| ScrapeGraph | $50-100 | Crawl4AI + Jina | $0 | 100% |
| NewsAPI | $30-50 | Google News RSS | $0 | 100% |
| GNews | $30-80 | Google News RSS | $0 | 100% |
| Mediastack | $15-50 | Google News RSS | $0 | 100% |
| LangSmith | $39-100 | Langfuse | $0 | 100% |
| Tavily (bulk) | $100-400 | DuckDuckGo | $0 | 100% |
| Tavily (quality) | $50-100 | Serper.dev | $5-10 | 90% |
| **TOTAL** | **$364-980** | **FREE alternatives** | **$5-10** | **~98%** |

---

## Success Metrics

- [ ] 90%+ of web scraping uses free Crawl4AI/Jina
- [ ] 100% of news queries use Google News RSS
- [ ] 80%+ of search queries use free DuckDuckGo
- [ ] LangSmith fully replaced by Langfuse
- [ ] Monthly API costs reduced by 90%+
- [ ] No degradation in research quality

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Crawl4AI quality issues | Fallback to Firecrawl for critical pages |
| Google News rate limits | Implement caching, spread requests |
| Langfuse missing features | Gradual migration, keep LangSmith as backup |
| DuckDuckGo result quality | Use for bulk only, Tavily for important |

---

## Next Steps

1. **Approve this plan**
2. **Start Phase 1 implementation** (Crawl4AI, Jina, Google News)
3. **Test with sample companies**
4. **Measure cost reduction**
5. **Proceed to Phase 2**
