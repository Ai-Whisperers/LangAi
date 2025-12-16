"""
Unified Web Scraper - Combines multiple scraping backends.

This module provides a unified interface for web scraping that automatically
selects the best backend (Firecrawl, ScrapeGraph, or basic HTTP) based on
availability and configuration.

Usage:
    from company_researcher.crawling import WebScraper

    scraper = WebScraper()

    # Simple scrape
    result = scraper.scrape("https://company.com/about")
    print(result.markdown)

    # Smart extraction
    data = scraper.smart_extract(
        "https://company.com/about",
        "Extract company name, CEO name, and founding year"
    )

    # Crawl entire site
    pages = scraper.crawl("https://company.com", max_pages=10)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel

from ..utils import get_config, get_logger

logger = get_logger(__name__)


class ScrapingBackend(str, Enum):
    """Available scraping backends."""

    FIRECRAWL = "firecrawl"
    SCRAPEGRAPH = "scrapegraph"
    BASIC = "basic"  # Falls back to DomainExplorer/httpx


@dataclass
class UnifiedScrapeResult:
    """Unified result from any scraping backend."""

    url: str
    markdown: str = ""
    html: str = ""
    extracted_data: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    backend_used: str = ""
    success: bool = True
    error: Optional[str] = None

    @property
    def title(self) -> str:
        return self.metadata.get("title", "")

    @property
    def description(self) -> str:
        return self.metadata.get("description", "")

    def to_research_format(self) -> Dict[str, Any]:
        """Convert to research pipeline format."""
        content = self.markdown or str(self.extracted_data) or ""
        return {
            "title": self.title or self.url,
            "url": self.url,
            "content": content[:4000],
            "score": 0.85 if self.success else 0.0,
            "source": f"web_scraper:{self.backend_used}",
            "metadata": self.metadata,
        }


@dataclass
class UnifiedCrawlResult:
    """Unified result from crawling."""

    base_url: str
    pages: List[UnifiedScrapeResult] = field(default_factory=list)
    total_pages: int = 0
    backend_used: str = ""
    success: bool = True
    error: Optional[str] = None

    def get_all_markdown(self, separator: str = "\n\n---\n\n") -> str:
        """Combine all pages' markdown."""
        return separator.join(
            f"# {p.title or p.url}\n\n{p.markdown}" for p in self.pages if p.success and p.markdown
        )

    def to_research_format(self) -> List[Dict[str, Any]]:
        """Convert all pages to research format."""
        return [p.to_research_format() for p in self.pages if p.success]


class WebScraper:
    """
    Unified web scraper with multiple backends.

    Automatically selects the best available backend based on:
    1. API key availability
    2. Task requirements (simple scrape vs. smart extraction)
    3. Fallback chain on errors

    Priority order:
    - Firecrawl: Best for LLM-ready markdown
    - ScrapeGraph: Best for smart extraction
    - Basic: httpx + BeautifulSoup fallback
    """

    def __init__(
        self,
        firecrawl_api_key: Optional[str] = None,
        scrapegraph_api_key: Optional[str] = None,
        preferred_backend: Optional[ScrapingBackend] = None,
    ):
        """
        Initialize unified web scraper.

        Args:
            firecrawl_api_key: Firecrawl API key
            scrapegraph_api_key: ScrapeGraph API key
            preferred_backend: Preferred backend to use (if available)
        """
        self.firecrawl_key = firecrawl_api_key or get_config("FIRECRAWL_API_KEY")
        self.scrapegraph_key = scrapegraph_api_key or get_config("SCRAPEGRAPH_API_KEY")
        self.preferred_backend = preferred_backend

        # Lazy-loaded clients
        self._firecrawl_client = None
        self._scrapegraph_client = None
        self._domain_explorer = None

    @property
    def firecrawl(self):
        """Get Firecrawl client (lazy-loaded)."""
        if self._firecrawl_client is None and self.firecrawl_key:
            from ..integrations.firecrawl_client import FirecrawlClient

            self._firecrawl_client = FirecrawlClient(api_key=self.firecrawl_key)
        return self._firecrawl_client

    @property
    def scrapegraph(self):
        """Get ScrapeGraph client (lazy-loaded)."""
        if self._scrapegraph_client is None and self.scrapegraph_key:
            from ..integrations.scrapegraph_client import ScrapeGraphClient

            self._scrapegraph_client = ScrapeGraphClient(api_key=self.scrapegraph_key)
        return self._scrapegraph_client

    @property
    def domain_explorer(self):
        """Get basic DomainExplorer (lazy-loaded)."""
        if self._domain_explorer is None:
            from .domain_explorer import DomainExplorer

            self._domain_explorer = DomainExplorer()
        return self._domain_explorer

    def get_available_backends(self) -> List[ScrapingBackend]:
        """Get list of available backends based on API keys."""
        available = []
        if self.firecrawl_key:
            available.append(ScrapingBackend.FIRECRAWL)
        if self.scrapegraph_key:
            available.append(ScrapingBackend.SCRAPEGRAPH)
        available.append(ScrapingBackend.BASIC)  # Always available
        return available

    def _select_backend(
        self,
        for_extraction: bool = False,
        for_crawl: bool = False,
    ) -> ScrapingBackend:
        """Select best backend for the task."""
        available = self.get_available_backends()

        # Use preferred if available
        if self.preferred_backend and self.preferred_backend in available:
            return self.preferred_backend

        # For smart extraction, prefer ScrapeGraph
        if for_extraction and ScrapingBackend.SCRAPEGRAPH in available:
            return ScrapingBackend.SCRAPEGRAPH

        # For crawling and general scraping, prefer Firecrawl
        if ScrapingBackend.FIRECRAWL in available:
            return ScrapingBackend.FIRECRAWL

        # Fallback to ScrapeGraph
        if ScrapingBackend.SCRAPEGRAPH in available:
            return ScrapingBackend.SCRAPEGRAPH

        # Last resort: basic scraping
        return ScrapingBackend.BASIC

    def scrape(
        self,
        url: str,
        render_js: bool = False,
        backend: Optional[ScrapingBackend] = None,
    ) -> UnifiedScrapeResult:
        """
        Scrape a single URL.

        Args:
            url: URL to scrape
            render_js: Whether to render JavaScript
            backend: Specific backend to use (auto-select if None)

        Returns:
            UnifiedScrapeResult with markdown content
        """
        selected_backend = backend or self._select_backend()
        logger.debug(f"Scraping {url} with backend: {selected_backend}")

        try:
            if selected_backend == ScrapingBackend.FIRECRAWL:
                return self._scrape_firecrawl(url)
            elif selected_backend == ScrapingBackend.SCRAPEGRAPH:
                return self._scrape_scrapegraph(url, render_js)
            else:
                return self._scrape_basic(url)
        except Exception as e:
            logger.warning(f"Backend {selected_backend} failed, trying fallback: {e}")
            # Try fallback
            if selected_backend != ScrapingBackend.BASIC:
                return self._scrape_basic(url)
            return UnifiedScrapeResult(url=url, success=False, error=str(e))

    def _scrape_firecrawl(self, url: str) -> UnifiedScrapeResult:
        """Scrape using Firecrawl."""
        result = self.firecrawl.scrape(url)
        return UnifiedScrapeResult(
            url=url,
            markdown=result.markdown,
            html=result.html,
            metadata=result.metadata,
            backend_used="firecrawl",
            success=result.success,
            error=result.error,
        )

    def _scrape_scrapegraph(self, url: str, render_js: bool = False) -> UnifiedScrapeResult:
        """Scrape using ScrapeGraph markdownify."""
        result = self.scrapegraph.markdownify(url, render_js=render_js)
        return UnifiedScrapeResult(
            url=url,
            markdown=result.markdown,
            backend_used="scrapegraph",
            success=result.success,
            error=result.error,
        )

    def _scrape_basic(self, url: str) -> UnifiedScrapeResult:
        """Scrape using basic DomainExplorer."""
        import asyncio

        result = asyncio.run(self.domain_explorer._fetch_page(url, self._get_basic_client()))
        return UnifiedScrapeResult(
            url=url,
            markdown=result.text,  # Basic extraction is plain text
            metadata={"title": result.title, "description": result.meta_description},
            backend_used="basic",
            success=result.fetch_success,
            error=result.error,
        )

    def _get_basic_client(self):
        """Get httpx client for basic scraping."""
        import httpx

        return httpx.AsyncClient(
            headers={"User-Agent": "CompanyResearcher/1.0"},
            follow_redirects=True,
            timeout=30.0,
        )

    def smart_extract(
        self,
        url: str,
        prompt: str,
        output_schema: Optional[Type[BaseModel]] = None,
        render_js: bool = False,
    ) -> UnifiedScrapeResult:
        """
        Smart extraction using AI.

        Uses natural language prompt to extract specific information.

        Args:
            url: URL to extract from
            prompt: What to extract (natural language)
            output_schema: Optional Pydantic model for structured output
            render_js: Whether to render JavaScript

        Returns:
            UnifiedScrapeResult with extracted_data field populated
        """
        backend = self._select_backend(for_extraction=True)

        if backend == ScrapingBackend.SCRAPEGRAPH and self.scrapegraph:
            result = self.scrapegraph.smart_scrape(
                url=url,
                prompt=prompt,
                output_schema=output_schema,
                render_js=render_js,
            )
            return UnifiedScrapeResult(
                url=url,
                extracted_data=result.extracted_data,
                backend_used="scrapegraph",
                success=result.success,
                error=result.error,
            )
        elif backend == ScrapingBackend.FIRECRAWL and self.firecrawl:
            # Firecrawl extract with prompt
            results = self.firecrawl.extract(
                urls=[url],
                prompt=prompt,
                schema=output_schema,
            )
            result = results[0] if results else None
            return UnifiedScrapeResult(
                url=url,
                extracted_data=result.data if result else None,
                backend_used="firecrawl",
                success=result.success if result else False,
                error=result.error if result else "No result",
            )
        else:
            # Fallback: scrape and return markdown
            scrape_result = self.scrape(url)
            scrape_result.extracted_data = {"raw_text": scrape_result.markdown}
            return scrape_result

    def crawl(
        self,
        url: str,
        max_pages: int = 10,
        max_depth: int = 2,
        include_paths: List[str] = None,
        exclude_paths: List[str] = None,
        extraction_prompt: str = None,
    ) -> UnifiedCrawlResult:
        """
        Crawl a website.

        Args:
            url: Starting URL
            max_pages: Maximum pages to crawl
            max_depth: Maximum link depth
            include_paths: URL patterns to include
            exclude_paths: URL patterns to exclude
            extraction_prompt: Optional prompt for AI extraction on each page

        Returns:
            UnifiedCrawlResult with all scraped pages
        """
        backend = self._select_backend(for_crawl=True)
        logger.info(f"Crawling {url} with backend: {backend}")

        try:
            if backend == ScrapingBackend.FIRECRAWL and self.firecrawl:
                return self._crawl_firecrawl(
                    url, max_pages, max_depth, include_paths, exclude_paths
                )
            elif backend == ScrapingBackend.SCRAPEGRAPH and self.scrapegraph and extraction_prompt:
                return self._crawl_scrapegraph(url, max_pages, max_depth, extraction_prompt)
            else:
                return self._crawl_basic(url, max_pages)
        except Exception as e:
            logger.error(f"Crawl failed: {e}")
            return UnifiedCrawlResult(base_url=url, success=False, error=str(e))

    def _crawl_firecrawl(
        self,
        url: str,
        max_pages: int,
        max_depth: int,
        include_paths: List[str] = None,
        exclude_paths: List[str] = None,
    ) -> UnifiedCrawlResult:
        """Crawl using Firecrawl."""
        result = self.firecrawl.crawl(
            url=url,
            max_pages=max_pages,
            max_depth=max_depth,
            include_paths=include_paths,
            exclude_paths=exclude_paths,
        )

        pages = [
            UnifiedScrapeResult(
                url=p.url,
                markdown=p.markdown,
                html=p.html,
                metadata=p.metadata,
                backend_used="firecrawl",
                success=p.success,
                error=p.error,
            )
            for p in result.pages
        ]

        return UnifiedCrawlResult(
            base_url=url,
            pages=pages,
            total_pages=result.total_pages,
            backend_used="firecrawl",
            success=result.success,
            error=result.error,
        )

    def _crawl_scrapegraph(
        self,
        url: str,
        max_pages: int,
        max_depth: int,
        prompt: str,
    ) -> UnifiedCrawlResult:
        """Crawl using ScrapeGraph with extraction."""
        result = self.scrapegraph.crawl_extract(
            url=url,
            prompt=prompt,
            max_pages=max_pages,
            max_depth=max_depth,
        )

        pages = [
            UnifiedScrapeResult(
                url=url,  # ScrapeGraph doesn't return individual URLs
                extracted_data=page_data,
                backend_used="scrapegraph",
                success=True,
            )
            for page_data in result.pages
        ]

        return UnifiedCrawlResult(
            base_url=url,
            pages=pages,
            total_pages=result.total_pages,
            backend_used="scrapegraph",
            success=result.success,
            error=result.error,
        )

    def _crawl_basic(self, url: str, max_pages: int) -> UnifiedCrawlResult:
        """Crawl using basic DomainExplorer."""
        self.domain_explorer.max_pages = max_pages
        result = self.domain_explorer.explore_sync(url)

        pages = [
            UnifiedScrapeResult(
                url=page.url,
                markdown=page.text,
                metadata={"title": page.title, "description": page.meta_description},
                backend_used="basic",
                success=page.fetch_success,
                error=page.error,
            )
            for page in result.pages_explored
        ]

        return UnifiedCrawlResult(
            base_url=url,
            pages=pages,
            total_pages=result.pages_fetched,
            backend_used="basic",
            success=True,
        )

    def map_urls(self, url: str, limit: int = 100) -> List[str]:
        """
        Discover all URLs on a website.

        Args:
            url: Website URL
            limit: Maximum URLs to return

        Returns:
            List of discovered URLs
        """
        if self.firecrawl:
            result = self.firecrawl.map_url(url, limit=limit)
            return result.urls if result.success else []
        else:
            # Basic URL extraction from homepage
            scrape_result = self.scrape(url)
            return scrape_result.metadata.get("links", [])[:limit]

    def search_and_scrape(
        self,
        query: str,
        num_results: int = 5,
    ) -> List[UnifiedScrapeResult]:
        """
        Search the web and scrape results.

        Args:
            query: Search query
            num_results: Number of results

        Returns:
            List of scraped search results
        """
        if self.firecrawl:
            result = self.firecrawl.search(query, num_results=num_results)
            return [
                UnifiedScrapeResult(
                    url=p.url,
                    markdown=p.markdown,
                    metadata=p.metadata,
                    backend_used="firecrawl",
                    success=p.success,
                )
                for p in result.results
            ]
        elif self.scrapegraph:
            result = self.scrapegraph.search_scrape(query, num_results=num_results)
            return [
                UnifiedScrapeResult(
                    url=url,
                    extracted_data=result.results,
                    backend_used="scrapegraph",
                    success=result.success,
                )
                for url in result.reference_urls
            ]
        else:
            logger.warning("No search-capable backend available")
            return []


# Convenience functions
def create_web_scraper(
    firecrawl_key: str = None,
    scrapegraph_key: str = None,
) -> WebScraper:
    """Create a WebScraper instance."""
    return WebScraper(
        firecrawl_api_key=firecrawl_key,
        scrapegraph_api_key=scrapegraph_key,
    )


def quick_scrape(url: str) -> str:
    """Quick scrape URL to markdown."""
    scraper = create_web_scraper()
    result = scraper.scrape(url)
    return result.markdown if result.success else ""


def quick_extract(url: str, prompt: str) -> Any:
    """Quick AI extraction from URL."""
    scraper = create_web_scraper()
    result = scraper.smart_extract(url, prompt)
    return result.extracted_data if result.success else None
