"""
Firecrawl Integration - LLM-ready web scraping and crawling.

Firecrawl converts websites to clean, LLM-ready markdown with support for:
- Single page scraping
- Full website crawling
- URL mapping/discovery
- Structured data extraction
- Web search
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from ..utils import get_config, get_logger

logger = get_logger(__name__)


@dataclass
class ScrapedPage:
    """Result from scraping a single page."""
    url: str
    markdown: str = ""
    html: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    links: List[str] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None

    @property
    def title(self) -> str:
        return self.metadata.get("title", "")

    @property
    def description(self) -> str:
        return self.metadata.get("description", "")


@dataclass
class CrawlResult:
    """Result from crawling a website."""
    base_url: str
    pages: List[ScrapedPage] = field(default_factory=list)
    total_pages: int = 0
    success: bool = True
    error: Optional[str] = None

    def get_all_markdown(self, separator: str = "\n\n---\n\n") -> str:
        """Combine all pages' markdown into one string."""
        return separator.join(
            f"# {p.title or p.url}\n\n{p.markdown}"
            for p in self.pages if p.success and p.markdown
        )


@dataclass
class MapResult:
    """Result from mapping a website's URLs."""
    base_url: str
    urls: List[str] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None


@dataclass
class SearchResult:
    """Result from web search."""
    query: str
    results: List[ScrapedPage] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None


@dataclass
class ExtractedData:
    """Result from structured extraction."""
    url: str
    data: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None


class FirecrawlClient:
    """
    Client for Firecrawl API - LLM-ready web scraping.

    Firecrawl handles:
    - JavaScript rendering
    - Anti-bot bypassing
    - Clean markdown conversion
    - Metadata extraction

    Usage:
        client = FirecrawlClient(api_key="your_key")

        # Scrape single page
        page = await client.scrape("https://example.com")
        print(page.markdown)

        # Crawl entire site
        result = await client.crawl("https://example.com", max_pages=10)
        for page in result.pages:
            print(page.title, page.markdown[:500])

        # Search and scrape
        results = await client.search("company AI strategy")
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Firecrawl client.

        Args:
            api_key: Firecrawl API key. If not provided, reads from FIRECRAWL_API_KEY env var.
        """
        self.api_key = api_key or get_config("FIRECRAWL_API_KEY")
        self._app = None

    def _get_app(self):
        """Lazy initialization of FirecrawlApp."""
        if self._app is None:
            if not self.api_key:
                raise ValueError(
                    "Firecrawl API key required. Set FIRECRAWL_API_KEY env var or pass api_key parameter."
                )
            from firecrawl import FirecrawlApp
            self._app = FirecrawlApp(api_key=self.api_key)
        return self._app

    def scrape(
        self,
        url: str,
        formats: List[str] = None,
        only_main_content: bool = True,
        include_tags: List[str] = None,
        exclude_tags: List[str] = None,
        wait_for: int = None,
        timeout: int = 30000,
    ) -> ScrapedPage:
        """
        Scrape a single URL and return LLM-ready content.

        Args:
            url: URL to scrape
            formats: Output formats ["markdown", "html", "links", "screenshot"]
            only_main_content: Extract only main content (recommended for LLM)
            include_tags: HTML tags to include
            exclude_tags: HTML tags to exclude
            wait_for: Wait for element (CSS selector) before scraping
            timeout: Request timeout in ms

        Returns:
            ScrapedPage with markdown content and metadata
        """
        try:
            app = self._get_app()

            params = {
                "formats": formats or ["markdown"],
                "onlyMainContent": only_main_content,
                "timeout": timeout,
            }

            if include_tags:
                params["includeTags"] = include_tags
            if exclude_tags:
                params["excludeTags"] = exclude_tags
            if wait_for:
                params["waitFor"] = wait_for

            result = app.scrape_url(url, params=params)

            return ScrapedPage(
                url=url,
                markdown=result.get("markdown", ""),
                html=result.get("html", ""),
                metadata=result.get("metadata", {}),
                links=result.get("links", []),
                success=True,
            )

        except Exception as e:
            logger.error(f"Firecrawl scrape error for {url}: {e}")
            return ScrapedPage(
                url=url,
                success=False,
                error=str(e),
            )

    def crawl(
        self,
        url: str,
        max_pages: int = 10,
        max_depth: int = 2,
        include_paths: List[str] = None,
        exclude_paths: List[str] = None,
        allow_external: bool = False,
        poll_interval: int = 5,
    ) -> CrawlResult:
        """
        Crawl a website and return all pages as LLM-ready content.

        Args:
            url: Starting URL
            max_pages: Maximum pages to crawl
            max_depth: Maximum link depth to follow
            include_paths: URL paths to include (regex patterns)
            exclude_paths: URL paths to exclude (regex patterns)
            allow_external: Allow crawling external domains
            poll_interval: Seconds between status checks

        Returns:
            CrawlResult with all scraped pages
        """
        try:
            app = self._get_app()

            params = {
                "limit": max_pages,
                "maxDepth": max_depth,
                "scrapeOptions": {
                    "formats": ["markdown"],
                    "onlyMainContent": True,
                },
            }

            if include_paths:
                params["includePaths"] = include_paths
            if exclude_paths:
                params["excludePaths"] = exclude_paths
            if allow_external:
                params["allowExternalLinks"] = True

            result = app.crawl_url(url, params=params, poll_interval=poll_interval)

            pages = []
            for item in result.get("data", []):
                pages.append(ScrapedPage(
                    url=item.get("url", url),
                    markdown=item.get("markdown", ""),
                    html=item.get("html", ""),
                    metadata=item.get("metadata", {}),
                    links=item.get("links", []),
                    success=True,
                ))

            return CrawlResult(
                base_url=url,
                pages=pages,
                total_pages=len(pages),
                success=True,
            )

        except Exception as e:
            logger.error(f"Firecrawl crawl error for {url}: {e}")
            return CrawlResult(
                base_url=url,
                success=False,
                error=str(e),
            )

    def map_url(
        self,
        url: str,
        search_query: str = None,
        include_subdomains: bool = False,
        limit: int = 100,
    ) -> MapResult:
        """
        Map all URLs on a website (fast URL discovery).

        Args:
            url: Website URL to map
            search_query: Filter URLs by search query
            include_subdomains: Include subdomain URLs
            limit: Maximum URLs to return

        Returns:
            MapResult with discovered URLs
        """
        try:
            app = self._get_app()

            params = {
                "limit": limit,
                "includeSubdomains": include_subdomains,
            }

            if search_query:
                params["search"] = search_query

            result = app.map_url(url, params=params)

            return MapResult(
                base_url=url,
                urls=result.get("links", []),
                success=True,
            )

        except Exception as e:
            logger.error(f"Firecrawl map error for {url}: {e}")
            return MapResult(
                base_url=url,
                success=False,
                error=str(e),
            )

    def search(
        self,
        query: str,
        num_results: int = 5,
        scrape_results: bool = True,
    ) -> SearchResult:
        """
        Search the web and optionally scrape results.

        Args:
            query: Search query
            num_results: Number of results to return
            scrape_results: Whether to scrape result pages

        Returns:
            SearchResult with scraped pages
        """
        try:
            app = self._get_app()

            params = {
                "limit": num_results,
                "scrapeOptions": {
                    "formats": ["markdown"],
                    "onlyMainContent": True,
                } if scrape_results else None,
            }

            result = app.search(query, params=params)

            pages = []
            for item in result.get("data", []):
                pages.append(ScrapedPage(
                    url=item.get("url", ""),
                    markdown=item.get("markdown", ""),
                    metadata=item.get("metadata", {}),
                    success=True,
                ))

            return SearchResult(
                query=query,
                results=pages,
                success=True,
            )

        except Exception as e:
            logger.error(f"Firecrawl search error for '{query}': {e}")
            return SearchResult(
                query=query,
                success=False,
                error=str(e),
            )

    def extract(
        self,
        urls: List[str],
        prompt: str = None,
        schema: Union[Dict[str, Any], BaseModel] = None,
    ) -> List[ExtractedData]:
        """
        Extract structured data from URLs using AI.

        Args:
            urls: URLs to extract from
            prompt: Natural language prompt describing what to extract
            schema: Pydantic model or JSON schema for output structure

        Returns:
            List of ExtractedData with structured information
        """
        try:
            app = self._get_app()

            params = {}
            if prompt:
                params["prompt"] = prompt
            if schema:
                if isinstance(schema, type) and issubclass(schema, BaseModel):
                    params["schema"] = schema.model_json_schema()
                else:
                    params["schema"] = schema

            result = app.extract(urls=urls, params=params)

            extracted = []
            for i, data in enumerate(result.get("data", [])):
                extracted.append(ExtractedData(
                    url=urls[i] if i < len(urls) else "",
                    data=data,
                    success=True,
                ))

            return extracted

        except Exception as e:
            logger.error(f"Firecrawl extract error: {e}")
            return [ExtractedData(url=url, success=False, error=str(e)) for url in urls]


# Convenience functions
def create_firecrawl_client(api_key: str = None) -> FirecrawlClient:
    """Create a FirecrawlClient instance."""
    return FirecrawlClient(api_key=api_key)


def scrape_to_markdown(url: str, api_key: str = None) -> str:
    """Quick function to scrape URL to markdown."""
    client = create_firecrawl_client(api_key)
    result = client.scrape(url)
    return result.markdown if result.success else ""


def crawl_website(url: str, max_pages: int = 10, api_key: str = None) -> CrawlResult:
    """Quick function to crawl a website."""
    client = create_firecrawl_client(api_key)
    return client.crawl(url, max_pages=max_pages)


# Format for research pipeline
def format_firecrawl_for_research(pages: List[ScrapedPage]) -> List[Dict[str, Any]]:
    """
    Format Firecrawl results for the research pipeline.

    Converts ScrapedPage objects to the standard research result format.
    """
    formatted = []
    for page in pages:
        if not page.success:
            continue

        formatted.append({
            "title": page.title or page.url,
            "url": page.url,
            "content": page.markdown[:4000],  # Truncate for API limits
            "score": 0.85,  # High score for direct scraping
            "source": "firecrawl",
            "metadata": page.metadata,
        })

    return formatted
