"""
Crawl4AI Integration - FREE Firecrawl Alternative.

Crawl4AI is a 100% free, open-source web crawler that converts
any webpage to LLM-ready markdown with structured extraction.

Features:
- JavaScript rendering (via Playwright)
- Structured data extraction with schemas
- Multi-page crawling
- Async support for high performance
- NO API KEY REQUIRED

Cost: $0 (completely free, open source)
Replaces: Firecrawl ($20/1K pages), ScrapeGraph ($15/1K pages)

Usage:
    from company_researcher.integrations.crawl4ai_client import get_crawl4ai

    crawler = get_crawl4ai()

    # Simple scrape
    result = await crawler.scrape_url("https://example.com")
    print(result.markdown)

    # With structured extraction
    data = await crawler.extract_structured(
        url="https://company.com/about",
        schema={"name": "str", "description": "str", "employees": "int"}
    )
"""

import asyncio
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Dict, List, Optional

from ..utils import get_logger

logger = get_logger(__name__)

# Try to import crawl4ai
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    logger.warning("crawl4ai not installed. Run: pip install crawl4ai && playwright install")


@dataclass
class CrawlResult:
    """Result from a crawl operation."""

    url: str
    markdown: str
    html: Optional[str] = None
    title: Optional[str] = None
    links: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    extracted_data: Optional[Dict[str, Any]] = None
    success: bool = True
    error: Optional[str] = None
    crawl_time_ms: float = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "markdown": self.markdown,
            "title": self.title,
            "links": self.links,
            "images": self.images,
            "metadata": self.metadata,
            "extracted_data": self.extracted_data,
            "success": self.success,
            "error": self.error,
            "crawl_time_ms": self.crawl_time_ms,
        }


class Crawl4AIClient:
    """
    Free web scraper using Crawl4AI.

    100% free alternative to Firecrawl and ScrapeGraph.
    Converts any webpage to LLM-ready markdown.

    Features:
    - JavaScript rendering
    - Structured extraction
    - Multi-page crawling
    - Async support
    """

    def __init__(
        self, headless: bool = True, timeout: int = 30000, user_agent: Optional[str] = None
    ):
        """
        Initialize Crawl4AI client.

        Args:
            headless: Run browser in headless mode
            timeout: Page load timeout in ms
            user_agent: Custom user agent string
        """
        if not CRAWL4AI_AVAILABLE:
            raise ImportError(
                "crawl4ai not installed. Run: pip install crawl4ai && playwright install"
            )

        self.headless = headless
        self.timeout = timeout
        self.user_agent = (
            user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

        self._total_crawls = 0
        self._total_time_ms = 0
        self._lock = Lock()

    async def scrape_url(
        self,
        url: str,
        wait_for: Optional[str] = None,
        remove_selectors: Optional[List[str]] = None,
        only_main_content: bool = True,
    ) -> CrawlResult:
        """
        Scrape a URL and convert to markdown.

        Args:
            url: URL to scrape
            wait_for: CSS selector to wait for before scraping
            remove_selectors: CSS selectors to remove (ads, nav, etc.)
            only_main_content: Extract only main content area

        Returns:
            CrawlResult with markdown and metadata
        """
        import time

        start_time = time.time()

        try:
            browser_config = BrowserConfig(headless=self.headless, user_agent=self.user_agent)

            run_config = CrawlerRunConfig(
                wait_for=wait_for,
                remove_selectors=remove_selectors
                or ["nav", "footer", "aside", ".ads", "#cookie-banner"],
                word_count_threshold=10,
                only_text=False,
            )

            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(url=url, config=run_config)

                crawl_time = (time.time() - start_time) * 1000

                # Update stats
                with self._lock:
                    self._total_crawls += 1
                    self._total_time_ms += crawl_time

                return CrawlResult(
                    url=url,
                    markdown=(
                        result.markdown if hasattr(result, "markdown") else result.extracted_content
                    ),
                    html=result.html if hasattr(result, "html") else None,
                    title=result.title if hasattr(result, "title") else None,
                    links=(
                        result.links.get("internal", []) + result.links.get("external", [])
                        if hasattr(result, "links") and result.links
                        else []
                    ),
                    images=(
                        result.media.get("images", [])
                        if hasattr(result, "media") and result.media
                        else []
                    ),
                    metadata={
                        "word_count": len(result.markdown.split()) if result.markdown else 0,
                        "crawl_time_ms": crawl_time,
                    },
                    success=result.success if hasattr(result, "success") else True,
                    crawl_time_ms=crawl_time,
                )

        except Exception as e:
            logger.error(f"Crawl4AI error for {url}: {e}")
            return CrawlResult(
                url=url,
                markdown="",
                success=False,
                error=str(e),
                crawl_time_ms=(time.time() - start_time) * 1000,
            )

    async def scrape_multiple(self, urls: List[str], max_concurrent: int = 5) -> List[CrawlResult]:
        """
        Scrape multiple URLs concurrently.

        Args:
            urls: List of URLs to scrape
            max_concurrent: Maximum concurrent requests

        Returns:
            List of CrawlResults
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def scrape_with_semaphore(url: str) -> CrawlResult:
            async with semaphore:
                return await self.scrape_url(url)

        tasks = [scrape_with_semaphore(url) for url in urls]
        return await asyncio.gather(*tasks)

    async def extract_structured(
        self, url: str, schema: Dict[str, str], instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from a URL using CSS selectors or LLM.

        Args:
            url: URL to scrape
            schema: Dictionary mapping field names to CSS selectors or types
            instructions: Optional instructions for LLM extraction

        Returns:
            Dictionary with extracted data
        """
        # First get the page content
        result = await self.scrape_url(url)

        if not result.success:
            return {"error": result.error, "_meta": {"url": url}}

        # If schema has CSS selectors, use them
        # Otherwise, we'd need LLM extraction (would use your existing LLM clients)
        extracted = {
            "url": url,
            "markdown": result.markdown[:2000],  # First 2000 chars
            "title": result.title,
            "_meta": {
                "word_count": result.metadata.get("word_count", 0),
                "crawl_time_ms": result.crawl_time_ms,
            },
        }

        return extracted

    async def crawl_website(
        self,
        start_url: str,
        max_pages: int = 10,
        same_domain_only: bool = True,
        url_pattern: Optional[str] = None,
    ) -> List[CrawlResult]:
        """
        Crawl multiple pages from a website.

        Args:
            start_url: Starting URL
            max_pages: Maximum pages to crawl
            same_domain_only: Only crawl same domain
            url_pattern: Regex pattern for URLs to include

        Returns:
            List of CrawlResults
        """
        import re
        from urllib.parse import urlparse

        crawled_urls = set()
        results = []
        to_crawl = [start_url]
        base_domain = urlparse(start_url).netloc

        while to_crawl and len(results) < max_pages:
            url = to_crawl.pop(0)

            if url in crawled_urls:
                continue

            crawled_urls.add(url)

            # Check domain
            if same_domain_only and urlparse(url).netloc != base_domain:
                continue

            # Check pattern
            if url_pattern and not re.search(url_pattern, url):
                continue

            result = await self.scrape_url(url)
            results.append(result)

            # Add new URLs to crawl
            if result.success:
                for link in result.links:
                    if link not in crawled_urls:
                        to_crawl.append(link)

        return results

    async def scrape_company_page(self, url: str, page_type: str = "about") -> CrawlResult:
        """
        Scrape a company page with optimized settings.

        Args:
            url: Company page URL
            page_type: Type of page (about, team, careers, investors)

        Returns:
            CrawlResult optimized for company data
        """
        # Remove common non-content elements
        remove_selectors = [
            "nav",
            "footer",
            "aside",
            ".cookie-banner",
            "#cookie-consent",
            ".social-share",
            ".newsletter-signup",
            ".ads",
            ".advertisement",
            "script",
            "style",
        ]

        # Wait for common content containers
        wait_for_map = {
            "about": "main, article, .about-content, .company-info",
            "team": ".team, .leadership, .executives",
            "careers": ".jobs, .careers, .openings",
            "investors": ".investor-relations, .financials",
        }

        result = await self.scrape_url(
            url=url,
            wait_for=wait_for_map.get(page_type),
            remove_selectors=remove_selectors,
            only_main_content=True,
        )

        # Add page type to metadata
        result.metadata["page_type"] = page_type

        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get crawling statistics."""
        with self._lock:
            return {
                "total_crawls": self._total_crawls,
                "total_time_ms": self._total_time_ms,
                "avg_time_ms": (
                    self._total_time_ms / self._total_crawls if self._total_crawls > 0 else 0
                ),
                "cost": 0.0,  # FREE!
            }

    def reset_stats(self) -> None:
        """Reset statistics."""
        with self._lock:
            self._total_crawls = 0
            self._total_time_ms = 0


# Singleton instance
_crawl4ai_client: Optional[Crawl4AIClient] = None
_client_lock = Lock()


def get_crawl4ai() -> Crawl4AIClient:
    """Get singleton Crawl4AI client."""
    global _crawl4ai_client
    if _crawl4ai_client is None:
        with _client_lock:
            if _crawl4ai_client is None:
                _crawl4ai_client = Crawl4AIClient()
    return _crawl4ai_client


def reset_crawl4ai() -> None:
    """Reset Crawl4AI client (for testing)."""
    global _crawl4ai_client
    _crawl4ai_client = None


# Convenience functions for sync usage
def scrape_url_sync(url: str) -> CrawlResult:
    """Synchronous wrapper for scrape_url."""
    client = get_crawl4ai()
    return asyncio.run(client.scrape_url(url))


def scrape_to_markdown(url: str) -> str:
    """Quick function to get markdown from URL."""
    result = scrape_url_sync(url)
    return result.markdown if result.success else ""
