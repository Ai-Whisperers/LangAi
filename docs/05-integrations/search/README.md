# Search Providers

Documentation for web search integrations.

## Overview

The system uses multiple search providers with automatic fallback:

```
Search Request
     |
     v
+----------+    Success    +--------+
|  Tavily  | ------------> | Results|
+----------+               +--------+
     |
     | Failure
     v
+------------+  Success    +--------+
| DuckDuckGo | ----------> | Results|
+------------+             +--------+
     |
     | Failure
     v
+--------+
| Empty  |
+--------+
```

## Tavily (Primary)

**Website**: https://tavily.com

Tavily is an LLM-optimized search engine providing clean, structured results.

### Features

- Optimized for AI consumption
- Clean text extraction
- Structured JSON response
- Domain filtering
- Fast response times

### Configuration

```env
TAVILY_API_KEY=tvly-your-api-key
```

```python
# config.py
tavily_api_key: str = Field(env="TAVILY_API_KEY")
tavily_max_results: int = 10
tavily_search_depth: str = "basic"  # basic, advanced
tavily_include_domains: List[str] = []
tavily_exclude_domains: List[str] = []
```

### Usage

```python
from company_researcher.integrations import TavilyClient

client = TavilyClient(config)
results = await client.search(
    query="Microsoft revenue 2024",
    max_results=10
)
```

### Response Format

```python
{
    "results": [
        {
            "title": "Microsoft Q3 2024 Earnings",
            "url": "https://...",
            "content": "Microsoft reported revenue of...",
            "score": 0.95
        }
    ],
    "query": "Microsoft revenue 2024"
}
```

### Pricing

| Tier | Price | API Calls |
|------|-------|-----------|
| Free | $0 | 1,000/month |
| Starter | $99/month | 10,000/month |
| Pro | $499/month | 100,000/month |

---

## DuckDuckGo (Fallback)

**Website**: https://duckduckgo.com

Free web search using DuckDuckGo's instant answer API.

### Features

- No API key required
- Free unlimited searches
- Privacy-focused
- Instant answers for common queries

### Limitations

- Rate limited (use with delays)
- Less clean text extraction
- Limited result depth
- No advanced filtering

### Usage

```python
from company_researcher.integrations import DuckDuckGoClient

client = DuckDuckGoClient()
results = await client.search(
    query="Microsoft company overview",
    max_results=10
)
```

### Configuration

```python
# config.py
duckduckgo_delay: float = 1.0  # Delay between requests
duckduckgo_max_results: int = 10
```

### Response Format

```python
{
    "results": [
        {
            "title": "Microsoft - Wikipedia",
            "url": "https://en.wikipedia.org/wiki/Microsoft",
            "snippet": "Microsoft Corporation is..."
        }
    ]
}
```

---

## Firecrawl (Advanced)

**Website**: https://firecrawl.dev

Advanced web scraping with JavaScript rendering.

### Features

- Full page rendering
- JavaScript execution
- Clean content extraction
- Bulk scraping
- Scheduled crawling

### Configuration

```env
FIRECRAWL_API_KEY=fc-your-api-key
```

```python
# config.py
firecrawl_api_key: str = Field(env="FIRECRAWL_API_KEY")
firecrawl_timeout: int = 60
```

### Usage

```python
from company_researcher.integrations import FirecrawlClient

client = FirecrawlClient(config)
content = await client.scrape(
    url="https://microsoft.com/about",
    render_js=True
)
```

### Pricing

| Tier | Price | Credits |
|------|-------|---------|
| Free | $0 | 500/month |
| Starter | $19/month | 3,000/month |
| Pro | $99/month | 20,000/month |

---

## Search Strategy

The system supports multiple search strategies:

### Strategy: `free_first`

Use free sources first, fall back to paid:

```yaml
# research_config.yaml
search:
  strategy: free_first
  min_free_sources: 20
  tavily_refinement: true
```

Flow:
1. DuckDuckGo search (free)
2. If results < 20, add Tavily search
3. Merge and deduplicate

### Strategy: `tavily_only`

Use only Tavily for all searches:

```yaml
search:
  strategy: tavily_only
```

### Strategy: `auto`

Automatically choose based on quality:

```yaml
search:
  strategy: auto
  quality_threshold: 80
```

---

## Implementation Details

### Search Client Interface

```python
class SearchClient(Protocol):
    async def search(
        self,
        query: str,
        max_results: int = 10
    ) -> List[SearchResult]:
        """Execute search and return results."""
        ...
```

### Search Result Format

```python
@dataclass
class SearchResult:
    title: str
    url: str
    content: str
    score: Optional[float] = None
    published_date: Optional[str] = None
```

### Deduplication

```python
def deduplicate_results(results: List[SearchResult]) -> List[SearchResult]:
    """Remove duplicate results by URL and content hash."""
    seen_urls = set()
    seen_hashes = set()
    unique = []

    for result in results:
        if result.url in seen_urls:
            continue
        content_hash = hash(result.content[:500])
        if content_hash in seen_hashes:
            continue

        seen_urls.add(result.url)
        seen_hashes.add(content_hash)
        unique.append(result)

    return unique
```

---

**Related Documentation**:
- [Financial Data](../financial/)
- [News Sources](../news/)
- [Configuration](../../06-configuration/)

---

**Last Updated**: December 2024
