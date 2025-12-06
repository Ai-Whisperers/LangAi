# Search & Data Tools - 27 Data Source Integrations

**Category:** Search & Data Tools
**Total Ideas:** 27
**Priority:** ⭐⭐⭐⭐⭐ CRITICAL (#34-35), ⭐⭐⭐⭐ HIGH (#36-60)
**Phase:** 1 (#34-35), 3 (#36-60)
**Total Effort:** 180-200 hours

---

## 📋 Overview

This document contains specifications for 27 search tools and data source integrations. These provide comprehensive data gathering capabilities across financial, company, social, technical, and specialized domains.

**Sources:** Company-researcher/src/tools/ + langchain-reference

---

## 🎯 Tool Catalog

### Core Search Infrastructure (Ideas #34-35)
1. [Multi-Provider Search Manager](#34-multi-provider-search-manager-) - Fallback chain, 7 providers
2. [Browser Automation](#35-browser-automation-) - Playwright, anti-bot, extraction

### Financial Data APIs (Ideas #36-40)
3-7. Alpha Vantage, SEC EDGAR, Yahoo Finance, Financial Modeling Prep, Bond Yield API

### Company Data APIs (Ideas #41-45)
8-12. Crunchbase, GitHub, OpenCorporates, WHOIS, LinkedIn

### Social Media APIs (Ideas #46-49)
13-16. Reddit, Twitter/X, YouTube, App Store

### Tech Intelligence (Ideas #50-53)
17-20. BuiltWith, Wappalyzer, GitHub Stats, Patents

### Content & Specialized (Ideas #54-60)
21-27. News Aggregator, PDF Parser, Structured Extractor, Crawler, File Manager, Local Search, Patent Search

---

## 🔍 Detailed Specifications

### 34. Multi-Provider Search Manager ⭐⭐⭐⭐⭐

**Priority:** CRITICAL
**Phase:** 1
**Effort:** Medium (8-12 hours)
**Source:** Company-researcher/src/tools/search/manager.py

#### What It Does

Unified search interface with automatic fallback across 7 search providers, ensuring 99.9%+ uptime and optimal results.

#### Supported Providers

```python
SEARCH_PROVIDERS = {
    "tavily": {
        "quality": 95,       # Best for research
        "cost": "$$$",
        "rate_limit": "1000/min",
        "features": ["deep_search", "summarization", "citations"],
    },
    "brave": {
        "quality": 90,       # Privacy-focused
        "cost": "$$",
        "rate_limit": "2000/min",
        "features": ["web_search", "news", "images"],
    },
    "duckduckgo": {
        "quality": 75,       # Free, no API key
        "cost": "$",
        "rate_limit": "Limited",
        "features": ["web_search", "instant_answers"],
    },
    "serper": {
        "quality": 92,       # Google results
        "cost": "$$$",
        "rate_limit": "1000/day",
        "features": ["google_search", "autocomplete", "images"],
    },
    "bing": {
        "quality": 85,       # Microsoft search
        "cost": "$$",
        "rate_limit": "3000/month",
        "features": ["web_search", "news", "images", "videos"],
    },
    "jina": {
        "quality": 80,       # AI-powered
        "cost": "$$",
        "rate_limit": "Varies",
        "features": ["semantic_search", "reader_api"],
    },
    "langsearch": {
        "quality": 82,       # Specialized
        "cost": "$$",
        "rate_limit": "1000/min",
        "features": ["research_mode", "filters"],
    },
}
```

#### Implementation

```python
class SearchManager:
    """Manages multiple search providers with fallback"""

    FALLBACK_CHAIN = ["tavily", "brave", "duckduckgo", "serper"]

    def __init__(self):
        self.providers = {
            "tavily": TavilySearch(),
            "brave": BraveSearch(),
            "duckduckgo": DuckDuckGoSearch(),
            "serper": SerperSearch(),
            "bing": BingSearch(),
            "jina": JinaSearch(),
            "langsearch": LangSearch(),
        }

        self.stats = {
            provider: {"calls": 0, "failures": 0, "avg_latency": 0}
            for provider in self.providers
        }

    async def search(
        self,
        query: str,
        max_results: int = 10,
        provider: str = None,
    ) -> List[SearchResult]:
        """Search with automatic fallback"""

        providers_to_try = (
            [provider] if provider
            else self.FALLBACK_CHAIN
        )

        for provider_name in providers_to_try:
            try:
                start_time = time.time()

                # Attempt search
                results = await self._search_with_provider(
                    provider_name,
                    query,
                    max_results,
                )

                # Track stats
                latency = time.time() - start_time
                self._track_success(provider_name, latency)

                return results

            except RateLimitError:
                self._track_failure(provider_name, "rate_limit")
                continue  # Try next provider

            except ProviderError as e:
                self._track_failure(provider_name, str(e))
                continue

        # All providers failed
        raise SearchError("All search providers failed")

    async def _search_with_provider(
        self,
        provider: str,
        query: str,
        max_results: int,
    ) -> List[SearchResult]:
        """Execute search with specific provider"""

        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}")

        search_tool = self.providers[provider]

        # Check rate limits
        if self._is_rate_limited(provider):
            raise RateLimitError(f"{provider} rate limit exceeded")

        # Execute search
        results = await search_tool.search(query, max_results)

        # Quality scoring
        scored_results = [
            self._score_result(r, provider) for r in results
        ]

        return scored_results

    def _score_result(
        self,
        result: SearchResult,
        provider: str,
    ) -> SearchResult:
        """Add quality score to result"""

        provider_quality = SEARCH_PROVIDERS[provider]["quality"]

        # Combine provider quality with result-specific factors
        result.quality_score = (
            provider_quality * 0.5 +
            self._domain_authority(result.url) * 0.3 +
            self._relevance_score(result) * 0.2
        )

        result.provider = provider
        return result

    def get_stats(self) -> dict:
        """Get provider statistics"""

        return {
            provider: {
                **stats,
                "success_rate": (
                    (stats["calls"] - stats["failures"]) / stats["calls"] * 100
                    if stats["calls"] > 0 else 0
                ),
            }
            for provider, stats in self.stats.items()
        }
```

#### Usage Example

```python
class ResearchAgent:
    """Agent using multi-provider search"""

    def __init__(self):
        self.search = SearchManager()

    async def gather_info(self, company: str) -> List[SearchResult]:
        """Search with automatic fallback"""

        # Primary search
        results = await self.search.search(
            query=f"{company} financial performance 2024",
            max_results=10,
        )

        return results

# Stats after 100 searches:
# {
#   "tavily": {"calls": 85, "failures": 2, "success_rate": 97.6%},
#   "brave": {"calls": 13, "failures": 0, "success_rate": 100%},
#   "duckduckgo": {"calls": 2, "failures": 0, "success_rate": 100%},
# }
```

#### Expected Impact

- **Uptime:** 99.9%+ (multi-provider fallback)
- **Quality:** 90%+ average (smart provider selection)
- **Cost:** Optimized (cheapest provider first when quality allows)
- **Speed:** Sub-second for most queries

#### Dependencies

- API keys for commercial providers (Tavily, Brave, Serper, Bing)
- Rate limit tracking system
- Provider health monitoring

#### Next Steps

1. Implement all 7 providers
2. Build fallback logic
3. Add rate limit tracking
4. Create quality scoring system
5. Add to Phase 1 (CRITICAL priority)

---

### 35. Browser Automation ⭐⭐⭐⭐⭐

**Priority:** HIGH
**Phase:** 3
**Effort:** Medium (10-12 hours)
**Source:** Company-researcher/src/tools/browser/

#### What It Does

Headless browser automation with JavaScript rendering, anti-bot handling, content extraction, and screenshot capability.

#### Architecture

```python
# Components:
browser/
├── navigator.py    # Page navigation, anti-bot
├── extractor.py    # Content extraction, cleaning
├── manager.py      # Browser pool, session management
└── tool.py         # LangChain tool wrapper
```

#### Implementation

```python
from playwright.async_api import async_playwright
import random

class BrowserNavigator:
    """Handles navigation and anti-bot measures"""

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
        # ... more user agents
    ]

    async def navigate(
        self,
        url: str,
        wait_for: str = "networkidle",
    ) -> Page:
        """Navigate with anti-bot measures"""

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            # Random user agent
            user_agent = random.choice(self.USER_AGENTS)

            context = await browser.new_context(
                user_agent=user_agent,
                viewport={"width": 1920, "height": 1080},
            )

            page = await context.new_page()

            # Anti-detection measures
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            # Navigate
            await page.goto(url, wait_until=wait_for)

            # Random delay (human-like)
            await page.wait_for_timeout(random.randint(1000, 3000))

            return page


class ContentExtractor:
    """Extracts and cleans page content"""

    async def extract(self, page: Page) -> dict:
        """Extract structured content"""

        # Main content
        main_content = await page.evaluate("""
            () => {
                // Try common content selectors
                const selectors = [
                    'article',
                    'main',
                    '[role="main"]',
                    '.content',
                    '#content',
                ];

                for (const selector of selectors) {
                    const el = document.querySelector(selector);
                    if (el) return el.innerText;
                }

                // Fallback to body
                return document.body.innerText;
            }
        """)

        # Metadata
        title = await page.title()
        meta_description = await page.get_attribute(
            'meta[name="description"]',
            'content',
        )

        # Links
        links = await page.evaluate("""
            () => Array.from(document.querySelectorAll('a'))
                      .map(a => ({ text: a.innerText, href: a.href }))
        """)

        return {
            "url": page.url,
            "title": title,
            "description": meta_description,
            "content": self._clean_content(main_content),
            "links": links[:20],  # Top 20 links
        }

    def _clean_content(self, content: str) -> str:
        """Clean extracted content"""

        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)

        # Remove common navigation text
        noise_patterns = [
            r'Cookie Policy.*?Accept',
            r'Subscribe to.*?Newsletter',
            r'Follow us on.*?Twitter',
        ]

        for pattern in noise_patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL)

        return content.strip()


class BrowserManager:
    """Manages browser pool and sessions"""

    def __init__(self, max_browsers: int = 5):
        self.max_browsers = max_browsers
        self.active_browsers = []
        self.navigator = BrowserNavigator()
        self.extractor = ContentExtractor()

    async def fetch_page(self, url: str) -> dict:
        """Fetch and extract page content"""

        # Navigate
        page = await self.navigator.navigate(url)

        # Extract content
        content = await self.extractor.extract(page)

        # Screenshot (optional)
        # await page.screenshot(path=f"screenshots/{url_hash}.png")

        # Cleanup
        await page.close()

        return content


# LangChain Tool Wrapper
class BrowserTool(BaseTool):
    """LangChain tool for browser automation"""

    name = "browser"
    description = "Browse web pages and extract content"

    def __init__(self):
        super().__init__()
        self.manager = BrowserManager()

    async def _arun(self, url: str) -> str:
        """Execute tool"""

        result = await self.manager.fetch_page(url)

        return f"""
        Title: {result['title']}
        URL: {result['url']}

        Content:
        {result['content'][:2000]}

        Links: {len(result['links'])} found
        """
```

#### Expected Impact

- **JavaScript Sites:** 100% coverage
- **Anti-Bot:** 95%+ success rate
- **Content Quality:** Clean, structured
- **Speed:** 2-5 seconds per page

#### Dependencies

- Playwright (`playwright install chromium`)
- User-Agent rotation list

#### Next Steps

1. Install Playwright
2. Implement navigator component
3. Build content extractor
4. Add browser pooling
5. Add to Phase 3 planning

---

## 📊 Financial Data APIs (Ideas #36-40)

### 36. Alpha Vantage API ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 8 hours

Stock fundamentals, time series, technical indicators.

**Features:** Real-time quotes, historical data, company overview, earnings, cash flow

---

### 37. SEC EDGAR API ⭐⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 10 hours

Official filings (10-K, 10-Q, 8-K, S-1), insider transactions.

**Implementation:** Parse XBRL, extract financials, track filing dates

---

### 38. Yahoo Finance ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 6 hours

Stock data, news, analyst ratings, options data.

**Note:** Unofficial API, use `yfinance` library

---

### 39. Financial Modeling Prep ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 8 hours

Company valuation, DCF models, financial ratios, historical data.

---

### 40. Bond Yield API ⭐⭐⭐

**Phase:** 3 | **Effort:** 4 hours

Treasury yields, corporate bonds, interest rates.

---

## 🏢 Company Data APIs (Ideas #41-45)

### 41. Crunchbase API ⭐⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 10 hours

Funding data, investors, acquisitions, leadership, company profiles.

```python
class CrunchbaseTool:
    async def get_company_profile(self, company: str) -> dict:
        data = await self.api.get(f"/entities/organizations/{company}")
        return {
            "funding_total": data["funding_total"],
            "last_funding_type": data["last_funding_type"],
            "investors": data["investor_names"],
            "founded": data["founded_on"],
        }
```

---

### 42. GitHub API ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 8 hours

Repository stats, commit activity, contributors, languages, stars.

---

### 43. OpenCorporates ⭐⭐⭐

**Phase:** 3 | **Effort:** 6 hours

Company registration data, officers, addresses, corporate filings.

---

### 44. WHOIS Lookup ⭐⭐⭐

**Phase:** 3 | **Effort:** 4 hours

Domain registration, ownership, DNS information.

---

### 45. LinkedIn Scraping ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 12 hours (complex)

Company pages, employee counts, job postings.

**Note:** Requires careful implementation (ToS compliance)

---

## 📱 Social Media APIs (Ideas #46-49)

### 46. Reddit API ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 8 hours

Subreddit monitoring, sentiment analysis, trending topics.

---

### 47. Twitter/X API ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 10 hours

Tweets, mentions, hashtags, sentiment, influencer analysis.

---

### 48. YouTube API ⭐⭐⭐

**Phase:** 3 | **Effort:** 8 hours

Video data, channel stats, comments, transcripts.

---

### 49. App Store Scraper ⭐⭐⭐

**Phase:** 3 | **Effort:** 6 hours

App reviews, ratings, download estimates, version history.

---

## 🔧 Tech Intelligence (Ideas #50-53)

### 50. BuiltWith API ⭐⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 8 hours

Tech stack detection, frameworks, analytics, hosting.

```python
class BuiltWithTool:
    async def get_tech_stack(self, domain: str) -> dict:
        data = await self.api.get(f"/v17/api.json?KEY={key}&LOOKUP={domain}")
        return {
            "analytics": data["analytics"],
            "frameworks": data["frameworks"],
            "hosting": data["hosting"],
            "widgets": data["widgets"],
        }
```

---

### 51. Wappalyzer ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 6 hours

Technology detection, CMS identification, JS libraries.

---

### 52. GitHub Statistics ⭐⭐⭐

**Phase:** 3 | **Effort:** 6 hours

Detailed repo analytics, contributor stats, code frequency.

---

### 53. Patent Databases ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 10 hours

USPTO, EPO, WIPO patent search and analysis.

---

## 📄 Content & Specialized (Ideas #54-60)

### 54. News Aggregator ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 8 hours

Multi-source news aggregation (NewsAPI, Google News, Bing News).

---

### 55. PDF Parser ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 6 hours

Extract text from PDFs (pypdf2, pdfplumber), table extraction.

---

### 56. Structured Data Extractor ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 8 hours

JSON-LD, Schema.org, OpenGraph extraction.

---

### 57. Web Crawler ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 10 hours

Sitemap parsing, recursive crawling, content indexing.

---

### 58. File Manager ⭐⭐⭐

**Phase:** 3 | **Effort:** 4 hours

Local file operations, CSV/Excel reading, file upload/download.

---

### 59. Local Search (Indexed Docs) ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 8 hours

Local document indexing, full-text search, metadata extraction.

---

### 60. Patent Search Specialized ⭐⭐⭐⭐

**Phase:** 3 | **Effort:** 8 hours

Advanced patent search, citation analysis, portfolio tracking.

---

## 📊 Summary Statistics

### Total Ideas: 27
### Total Effort: 180-200 hours

### By Priority:
- ⭐⭐⭐⭐⭐ Critical: 2 ideas (#34-35) - 18-24 hours
- ⭐⭐⭐⭐ High: 20 ideas (#36-53, selected) - 140-160 hours
- ⭐⭐⭐ Medium: 5 ideas - 20-30 hours

### By Category:
- **Core Search:** 2 ideas (18-24h)
- **Financial APIs:** 5 ideas (36-46h)
- **Company Data:** 5 ideas (40-50h)
- **Social Media:** 4 ideas (32-40h)
- **Tech Intel:** 4 ideas (30-38h)
- **Content/Specialized:** 7 ideas (34-42h)

### Implementation Order:
1. **Week 1 (Phase 1):** Multi-Provider Search (#34) - CRITICAL
2. **Week 7 (Phase 3):** Browser Automation (#35)
3. **Weeks 8-10:** Financial APIs (#36-40)
4. **Weeks 11-12:** Company Data APIs (#41-45)
5. **Weeks 13-14:** Social & Tech APIs (#46-53)
6. **Week 15:** Content tools (#54-60)

---

## 🎯 Integration Roadmap

### Phase 1 - Week 1 (CRITICAL)
1. Implement Multi-Provider Search Manager
2. Set up API keys for all providers
3. Build fallback chain
4. Test with research workflows

### Phase 3 - Week 7
1. Implement Browser Automation
2. Test with JavaScript-heavy sites
3. Build content extraction

### Phase 3 - Weeks 8-15
1. Implement Financial APIs (5 tools)
2. Implement Company Data APIs (5 tools)
3. Implement Social Media APIs (4 tools)
4. Implement Tech Intelligence (4 tools)
5. Implement Content tools (7 tools)
6. Integration testing for all 27 tools

---

## 🔗 Related Documents

- [01-architecture-patterns.md](01-architecture-patterns.md) - Tool singleton pattern
- [02-agent-specialization.md](02-agent-specialization.md) - Agents using these tools
- [05-quality-assurance.md](05-quality-assurance.md) - Source quality tracking
- [README.md](README.md) - Navigation hub

---

**Status:** ✅ Complete
**Total Tools:** 27
**Ready for:** Phase 1 & 3 implementation
