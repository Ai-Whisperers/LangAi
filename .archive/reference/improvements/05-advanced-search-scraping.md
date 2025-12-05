# Advanced Search & Web Scraping

**Source:** `langchain-reference/01-research-agents/company-researcher/` + Playwright patterns

---

## Overview

High-quality research requires:
- ✅ Smart web search (find the right sources)
- ✅ Anti-bot scraping (get past defenses)
- ✅ Content extraction (clean HTML → text)
- ✅ PDF/document parsing (SEC filings, reports)
- ✅ Rate limiting (don't get blocked)

---

## Component 1: Web Search

### Tavily API (Primary)

**Why Tavily:**
- Built for AI agents
- Returns clean, relevant results
- Handles filtering automatically
- Affordable ($1 per 1,000 searches)

**Basic Usage:**
```python
from tavily import TavilyClient

client = TavilyClient(api_key="your_api_key")

# Simple search
results = client.search(
    query="Tesla revenue 2024",
    max_results=5
)

# Results format:
{
    "results": [
        {
            "title": "Tesla Q4 2023 Earnings",
            "url": "https://ir.tesla.com/...",
            "content": "Tesla reported revenue of $96.7B...",
            "score": 0.95,  # Relevance score
            "published_date": "2024-01-24"
        }
    ]
}
```

**Advanced Usage:**
```python
# Parallel searches
async def parallel_search(queries: list[str]):
    """Search multiple queries in parallel"""

    async def search_single(query: str):
        return await asyncio.to_thread(
            client.search,
            query=query,
            max_results=3,
            search_depth="advanced"  # More thorough
        )

    tasks = [search_single(q) for q in queries]
    results = await asyncio.gather(*tasks)

    return results

# Usage
results = await parallel_search([
    "Tesla revenue 2024",
    "Tesla Cybertruck production",
    "Tesla FSD adoption rate"
])
```

**Search Parameters:**
```python
client.search(
    query="Tesla",
    max_results=5,
    search_depth="basic" | "advanced",  # advanced = more thorough
    include_domains=["tesla.com", "sec.gov"],  # Only these domains
    exclude_domains=["reddit.com"],  # Never these domains
    time_range="1w" | "1m" | "3m" | "1y",  # How recent
    topic="general" | "news" | "finance"  # Content type
)
```

---

### Anthropic Native Search (Backup)

```python
from anthropic import Anthropic

client = Anthropic(api_key="your_api_key")

# Claude can search the web natively
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=[
        {
            "type": "web_search_20241022",
            "name": "web_search",
            "max_results": 5
        }
    ],
    messages=[
        {
            "role": "user",
            "content": "Search for Tesla's latest revenue numbers"
        }
    ]
)

# Claude automatically searches and synthesizes results
```

---

## Component 2: Web Scraping

### Playwright (Anti-Bot)

**Why Playwright:**
- Headless browser (acts like real user)
- Bypasses anti-bot detection
- Executes JavaScript (modern sites)
- Handles popups, cookies, etc.

**Basic Scraping:**
```python
from playwright.async_api import async_playwright

async def scrape_url(url: str) -> dict:
    """Scrape a single URL"""

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )

        # New page
        page = await browser.new_page()

        # Set user agent (look like real browser)
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/91.0.4472.124 Safari/537.36'
        })

        try:
            # Navigate
            await page.goto(url, timeout=10000)

            # Wait for content to load
            await page.wait_for_load_state('networkidle')

            # Extract content
            content = await page.evaluate('''() => {
                // Remove unwanted elements
                const unwanted = document.querySelectorAll(
                    'script, style, nav, footer, header, aside, .ad, .advertisement'
                );
                unwanted.forEach(el => el.remove());

                // Get main content
                const main = document.querySelector('main') ||
                            document.querySelector('article') ||
                            document.body;

                return {
                    text: main.innerText,
                    html: main.innerHTML,
                    title: document.title,
                    meta: {
                        description: document.querySelector('meta[name="description"]')?.content,
                        author: document.querySelector('meta[name="author"]')?.content
                    }
                };
            }''')

            return {
                "url": url,
                "title": content["title"],
                "text": content["text"][:10000],  # Limit length
                "meta": content["meta"],
                "success": True
            }

        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "success": False
            }

        finally:
            await browser.close()
```

**Batch Scraping:**
```python
async def scrape_multiple(urls: list[str], max_concurrent=3):
    """Scrape multiple URLs with rate limiting"""

    semaphore = asyncio.Semaphore(max_concurrent)

    async def scrape_with_limit(url: str):
        async with semaphore:
            result = await scrape_url(url)
            await asyncio.sleep(1)  # Rate limit
            return result

    tasks = [scrape_with_limit(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return results
```

**Handle Dynamic Content:**
```python
async def scrape_dynamic_content(url: str, wait_for: str):
    """Scrape sites with dynamic content"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(url)

        # Wait for specific element to appear
        await page.wait_for_selector(wait_for, timeout=10000)

        # Or wait for network activity to stop
        await page.wait_for_load_state('networkidle')

        # Scroll to load lazy content
        await page.evaluate('''() => {
            window.scrollTo(0, document.body.scrollHeight);
        }''')

        await asyncio.sleep(2)  # Wait for lazy load

        content = await page.content()

        await browser.close()

        return content
```

---

## Component 3: Content Extraction

### Clean HTML to Text

```python
from bs4 import BeautifulSoup
import re

class ContentExtractor:
    """Extract clean text from HTML"""

    def extract_clean_text(self, html: str) -> str:
        """Convert HTML to clean text"""

        soup = BeautifulSoup(html, 'html.parser')

        # Remove unwanted tags
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()

        # Get text
        text = soup.get_text()

        # Clean whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text

    def extract_structured_data(self, html: str) -> dict:
        """Extract structured data (tables, lists, etc.)"""

        soup = BeautifulSoup(html, 'html.parser')

        # Extract tables
        tables = []
        for table in soup.find_all('table'):
            rows = []
            for tr in table.find_all('tr'):
                cells = [td.get_text().strip() for td in tr.find_all(['td', 'th'])]
                rows.append(cells)
            tables.append(rows)

        # Extract lists
        lists = []
        for ul in soup.find_all(['ul', 'ol']):
            items = [li.get_text().strip() for li in ul.find_all('li')]
            lists.append(items)

        # Extract headings
        headings = {}
        for level in range(1, 7):
            headings[f'h{level}'] = [
                h.get_text().strip()
                for h in soup.find_all(f'h{level}')
            ]

        return {
            "tables": tables,
            "lists": lists,
            "headings": headings
        }

    def extract_links(self, html: str, base_url: str) -> list[dict]:
        """Extract all links"""

        from urllib.parse import urljoin

        soup = BeautifulSoup(html, 'html.parser')

        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            absolute_url = urljoin(base_url, href)
            links.append({
                "text": a.get_text().strip(),
                "url": absolute_url
            })

        return links
```

---

## Component 4: PDF Parsing

### SEC Filings & Reports

```python
import PyPDF2
import pdfplumber

class PDFParser:
    """Parse PDF documents"""

    def extract_text_basic(self, pdf_path: str) -> str:
        """Basic text extraction"""

        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            text = ""
            for page in reader.pages:
                text += page.extract_text()

            return text

    def extract_text_advanced(self, pdf_path: str) -> dict:
        """Advanced extraction with tables"""

        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            tables = []

            for page in pdf.pages:
                # Extract text
                text += page.extract_text()

                # Extract tables
                page_tables = page.extract_tables()
                tables.extend(page_tables)

            return {
                "text": text,
                "tables": tables,
                "pages": len(pdf.pages)
            }

    def extract_financial_tables(self, pdf_path: str) -> list[dict]:
        """Extract financial tables from SEC filings"""

        with pdfplumber.open(pdf_path) as pdf:
            financial_tables = []

            for page in pdf.pages:
                tables = page.extract_tables()

                for table in tables:
                    # Check if it's a financial table
                    if self._is_financial_table(table):
                        financial_tables.append({
                            "page": page.page_number,
                            "data": table
                        })

            return financial_tables

    def _is_financial_table(self, table: list[list]) -> bool:
        """Check if table contains financial data"""

        if not table or len(table) < 2:
            return False

        # Look for financial keywords
        financial_keywords = [
            'revenue', 'income', 'assets', 'liabilities',
            'cash flow', 'earnings', 'profit', 'loss'
        ]

        table_text = ' '.join([
            ' '.join(row) for row in table
        ]).lower()

        return any(keyword in table_text for keyword in financial_keywords)
```

---

## Component 5: Rate Limiting

### Prevent API Throttling

```python
from asyncio import Semaphore
import time

class RateLimiter:
    """Rate limiting for API calls"""

    def __init__(self, requests_per_second: int = 4):
        self.semaphore = Semaphore(requests_per_second)
        self.min_interval = 1.0 / requests_per_second
        self.last_call_time = 0

    async def __aenter__(self):
        await self.semaphore.acquire()
        # Ensure minimum interval between calls
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.last_call_time = time.time()
        self.semaphore.release()

# Usage
rate_limiter = RateLimiter(requests_per_second=4)

async def make_api_call(query: str):
    async with rate_limiter:
        result = await api_client.search(query)
        return result
```

---

## Complete Deep Research Agent

### Putting It All Together

```python
class DeepResearchAgent:
    """Advanced research with scraping"""

    def __init__(self, config: dict):
        self.tavily = TavilyClient(api_key=config["tavily_api_key"])
        self.rate_limiter = RateLimiter(requests_per_second=4)
        self.content_extractor = ContentExtractor()

    async def research(self, company_name: str, task: str) -> dict:
        """Conduct deep research"""

        # 1. Generate queries
        queries = self._generate_queries(company_name, task)

        # 2. Search web
        search_results = await self._search_all(queries)

        # 3. Extract top URLs
        urls = self._extract_top_urls(search_results, max_urls=10)

        # 4. Scrape URLs
        scraped_content = await self._scrape_urls(urls)

        # 5. Extract and clean content
        clean_content = self._extract_content(scraped_content)

        # 6. Synthesize findings
        findings = await self._synthesize(clean_content, task)

        return {
            "findings": findings,
            "sources": urls,
            "confidence": self._calculate_confidence(clean_content)
        }

    async def _search_all(self, queries: list[str]) -> list[dict]:
        """Search all queries with rate limiting"""

        results = []
        for query in queries:
            async with self.rate_limiter:
                result = await asyncio.to_thread(
                    self.tavily.search,
                    query=query,
                    max_results=5
                )
                results.append(result)

        return results

    async def _scrape_urls(self, urls: list[str]) -> list[dict]:
        """Scrape multiple URLs"""

        tasks = [scrape_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [r for r in results if isinstance(r, dict) and r.get("success")]

    def _extract_content(self, scraped_content: list[dict]) -> list[dict]:
        """Extract and clean content"""

        clean_content = []
        for content in scraped_content:
            clean_text = self.content_extractor.extract_clean_text(
                content.get("text", "")
            )

            clean_content.append({
                "url": content["url"],
                "title": content["title"],
                "text": clean_text[:5000],  # Limit
                "meta": content.get("meta", {})
            })

        return clean_content
```

---

## Implementation Roadmap

### Week 1-2 (MVP)
- Basic Tavily search
- Simple content extraction
- No scraping yet

### Week 3-4 (Enhancement)
- Add Playwright scraping
- Implement rate limiting
- PDF parsing for SEC filings

### Week 5+ (Advanced)
- Anti-bot techniques
- Dynamic content handling
- Screenshot capture for visual content

---

## References

- Company Researcher: `langchain-reference/01-research-agents/company-researcher/`
- Playwright docs: https://playwright.dev
- Tavily API: https://tavily.com
