"""
ScrapeGraph Integration - AI-powered web scraping with natural language.

ScrapeGraph uses LLMs to intelligently extract data from websites:
- Natural language prompts for extraction
- Structured output with schemas
- Multi-page crawling with extraction
- Search and scrape capabilities
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel

from ..utils import get_config, get_logger

logger = get_logger(__name__)


@dataclass
class SmartScrapedData:
    """Result from AI-powered smart scraping."""

    url: str
    prompt: str
    extracted_data: Any = None
    raw_markdown: str = ""
    success: bool = True
    error: Optional[str] = None
    request_id: Optional[str] = None


@dataclass
class MarkdownResult:
    """Result from converting URL to markdown."""

    url: str
    markdown: str = ""
    success: bool = True
    error: Optional[str] = None


@dataclass
class CrawlExtractResult:
    """Result from crawling with extraction."""

    base_url: str
    pages: List[Dict[str, Any]] = field(default_factory=list)
    total_pages: int = 0
    success: bool = True
    error: Optional[str] = None


@dataclass
class SearchScrapedResult:
    """Result from search and scrape."""

    query: str
    results: List[Dict[str, Any]] = field(default_factory=list)
    reference_urls: List[str] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None


class ScrapeGraphClient:
    """
    Client for ScrapeGraph API - AI-powered web scraping.

    ScrapeGraph specializes in:
    - Natural language extraction prompts
    - Structured data extraction with schemas
    - Smart scraping that understands content
    - Heavy JavaScript rendering

    Usage:
        client = ScrapeGraphClient(api_key="your_key")

        # Smart scrape with natural language
        result = client.smart_scrape(
            url="https://company.com/about",
            prompt="Extract the company name, founding year, and key executives"
        )
        print(result.extracted_data)

        # Smart scrape with schema
        class CompanyInfo(BaseModel):
            name: str
            founded: int
            executives: List[str]

        result = client.smart_scrape(
            url="https://company.com/about",
            prompt="Extract company information",
            output_schema=CompanyInfo
        )

        # Search and extract
        result = client.search_scrape(
            prompt="Find the latest revenue figures for Microsoft"
        )
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize ScrapeGraph client.

        Args:
            api_key: ScrapeGraph API key. If not provided, reads from SCRAPEGRAPH_API_KEY env var.
        """
        self.api_key = api_key or get_config("SCRAPEGRAPH_API_KEY")
        self._client = None

    def _get_client(self):
        """Lazy initialization of ScrapeGraph client."""
        if self._client is None:
            if not self.api_key:
                raise ValueError(
                    "ScrapeGraph API key required. Set SCRAPEGRAPH_API_KEY env var or pass api_key parameter."
                )
            from scrapegraph_py import Client

            self._client = Client(api_key=self.api_key)
        return self._client

    def smart_scrape(
        self,
        url: str,
        prompt: str,
        output_schema: Optional[Type[BaseModel]] = None,
        render_js: bool = False,
        stealth: bool = False,
        num_scrolls: int = None,
    ) -> SmartScrapedData:
        """
        Smart scrape a URL using natural language prompt.

        The AI understands your prompt and extracts relevant information.

        Args:
            url: URL to scrape
            prompt: Natural language description of what to extract
            output_schema: Optional Pydantic model for structured output
            render_js: Render heavy JavaScript (slower but more complete)
            stealth: Use stealth mode to avoid detection
            num_scrolls: Number of page scrolls for infinite scroll pages

        Returns:
            SmartScrapedData with extracted information
        """
        try:
            client = self._get_client()

            kwargs = {
                "user_prompt": prompt,
                "website_url": url,
                "render_heavy_js": render_js,
                "stealth": stealth,
            }

            if output_schema:
                kwargs["output_schema"] = output_schema
            if num_scrolls:
                kwargs["number_of_scrolls"] = num_scrolls

            result = client.smartscraper(**kwargs)

            return SmartScrapedData(
                url=url,
                prompt=prompt,
                extracted_data=result.get("result", result),
                request_id=result.get("request_id"),
                success=True,
            )

        except Exception as e:
            logger.error(f"ScrapeGraph smart scrape error for {url}: {e}")
            return SmartScrapedData(
                url=url,
                prompt=prompt,
                success=False,
                error=str(e),
            )

    def markdownify(
        self,
        url: str,
        render_js: bool = False,
        stealth: bool = False,
    ) -> MarkdownResult:
        """
        Convert a URL to clean markdown.

        Args:
            url: URL to convert
            render_js: Render heavy JavaScript
            stealth: Use stealth mode

        Returns:
            MarkdownResult with clean markdown
        """
        try:
            client = self._get_client()

            result = client.markdownify(
                website_url=url,
                render_heavy_js=render_js,
                stealth=stealth,
            )

            return MarkdownResult(
                url=url,
                markdown=result.get("result", ""),
                success=True,
            )

        except Exception as e:
            logger.error(f"ScrapeGraph markdownify error for {url}: {e}")
            return MarkdownResult(
                url=url,
                success=False,
                error=str(e),
            )

    def crawl_extract(
        self,
        url: str,
        prompt: str = None,
        data_schema: Dict[str, Any] = None,
        max_pages: int = 5,
        max_depth: int = 2,
        same_domain_only: bool = True,
        use_sitemap: bool = False,
    ) -> CrawlExtractResult:
        """
        Crawl a website and extract data from pages.

        Args:
            url: Starting URL
            prompt: Extraction prompt for each page
            data_schema: JSON schema for extracted data
            max_pages: Maximum pages to crawl
            max_depth: Maximum link depth
            same_domain_only: Only crawl same domain
            use_sitemap: Use sitemap for URL discovery

        Returns:
            CrawlExtractResult with extracted data from all pages
        """
        try:
            client = self._get_client()

            result = client.crawl(
                url=url,
                prompt=prompt,
                data_schema=data_schema,
                extraction_mode=True,
                depth=max_depth,
                max_pages=max_pages,
                same_domain_only=same_domain_only,
                sitemap=use_sitemap,
            )

            pages = result.get("result", [])
            if isinstance(pages, dict):
                pages = [pages]

            return CrawlExtractResult(
                base_url=url,
                pages=pages,
                total_pages=len(pages),
                success=True,
            )

        except Exception as e:
            logger.error(f"ScrapeGraph crawl error for {url}: {e}")
            return CrawlExtractResult(
                base_url=url,
                success=False,
                error=str(e),
            )

    def search_scrape(
        self,
        prompt: str,
        num_results: int = 3,
        output_schema: Optional[Type[BaseModel]] = None,
        stealth: bool = False,
    ) -> SearchScrapedResult:
        """
        Search the web and extract information using AI.

        Performs a web search based on the prompt, then extracts
        relevant information from the results.

        Args:
            prompt: Natural language query/extraction prompt
            num_results: Number of search results to process
            output_schema: Optional Pydantic model for structured output
            stealth: Use stealth mode

        Returns:
            SearchScrapedResult with extracted information
        """
        try:
            client = self._get_client()

            kwargs = {
                "user_prompt": prompt,
                "num_results": num_results,
                "extraction_mode": True,
                "stealth": stealth,
            }

            if output_schema:
                kwargs["output_schema"] = output_schema

            result = client.searchscraper(**kwargs)

            return SearchScrapedResult(
                query=prompt,
                results=[result.get("result", result)] if result else [],
                reference_urls=result.get("reference_urls", []),
                success=True,
            )

        except Exception as e:
            logger.error(f"ScrapeGraph search scrape error for '{prompt}': {e}")
            return SearchScrapedResult(
                query=prompt,
                success=False,
                error=str(e),
            )

    def get_credits(self) -> Optional[int]:
        """Get remaining API credits."""
        try:
            client = self._get_client()
            result = client.get_credits()
            return result.get("remaining_credits")
        except Exception as e:
            logger.error(f"ScrapeGraph get credits error: {e}")
            return None


# Convenience functions
def create_scrapegraph_client(api_key: str = None) -> ScrapeGraphClient:
    """Create a ScrapeGraphClient instance."""
    return ScrapeGraphClient(api_key=api_key)


def smart_extract(
    url: str,
    prompt: str,
    api_key: str = None,
) -> Any:
    """Quick function to smart extract from URL."""
    client = create_scrapegraph_client(api_key)
    result = client.smart_scrape(url, prompt)
    return result.extracted_data if result.success else None


def url_to_markdown(url: str, api_key: str = None) -> str:
    """Quick function to convert URL to markdown."""
    client = create_scrapegraph_client(api_key)
    result = client.markdownify(url)
    return result.markdown if result.success else ""


# Pydantic models for common extraction schemas
class CompanyBasicInfo(BaseModel):
    """Basic company information schema."""

    name: str = ""
    description: str = ""
    industry: str = ""
    founded_year: Optional[int] = None
    headquarters: str = ""
    website: str = ""


class ExecutiveInfo(BaseModel):
    """Executive information schema."""

    name: str
    title: str = ""
    linkedin_url: str = ""


class CompanyLeadership(BaseModel):
    """Company leadership schema."""

    company_name: str = ""
    executives: List[ExecutiveInfo] = []
    board_members: List[ExecutiveInfo] = []


class ProductInfo(BaseModel):
    """Product information schema."""

    name: str
    description: str = ""
    category: str = ""
    pricing: str = ""


class CompanyProducts(BaseModel):
    """Company products schema."""

    company_name: str = ""
    products: List[ProductInfo] = []
    services: List[str] = []


class FinancialHighlights(BaseModel):
    """Financial highlights schema."""

    revenue: str = ""
    revenue_growth: str = ""
    profit: str = ""
    employees: Optional[int] = None
    market_cap: str = ""
    fiscal_year: str = ""


# Format for research pipeline
def format_scrapegraph_for_research(results: List[SmartScrapedData]) -> List[Dict[str, Any]]:
    """
    Format ScrapeGraph results for the research pipeline.

    Converts SmartScrapedData objects to the standard research result format.
    """
    formatted = []
    for result in results:
        if not result.success:
            continue

        # Convert extracted data to string if needed
        content = result.extracted_data
        if isinstance(content, dict):
            content = "\n".join(f"{k}: {v}" for k, v in content.items())
        elif isinstance(content, list):
            content = "\n".join(str(item) for item in content)
        else:
            content = str(content)

        formatted.append(
            {
                "title": f"AI Extraction: {result.prompt[:50]}...",
                "url": result.url,
                "content": content[:4000],  # Truncate for API limits
                "score": 0.90,  # High score for AI extraction
                "source": "scrapegraph",
                "extracted_data": result.extracted_data,
            }
        )

    return formatted
