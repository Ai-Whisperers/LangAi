"""
Domain Explorer - HTML link extraction and domain crawling.

This module provides intelligent domain exploration by:
1. Fetching HTML from URLs
2. Parsing and extracting internal links
3. Prioritizing valuable pages (about, leadership, investors, etc.)
4. Fetching content from prioritized pages
"""

import asyncio
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from ..utils import get_logger

logger = get_logger(__name__)


# High-value page patterns for company research
PRIORITY_PATTERNS = {
    # Leadership & Team (highest priority for B2B sales)
    "leadership": {
        "patterns": [
            r"/about[/-]?us",
            r"/team",
            r"/leadership",
            r"/management",
            r"/executives",
            r"/directors",
            r"/board",
            r"/quien[es]?[-_]?somos",  # Spanish
            r"/nosotros",
            r"/equipo",
        ],
        "keywords": [
            "team",
            "leadership",
            "management",
            "executives",
            "about us",
            "equipo",
            "nosotros",
        ],
        "priority": 10,
    },
    # Products & Services
    "products": {
        "patterns": [
            r"/products?",
            r"/services?",
            r"/solutions?",
            r"/offerings?",
            r"/productos?",
            r"/servicios?",
        ],
        "keywords": ["products", "services", "solutions", "productos", "servicios"],
        "priority": 9,
    },
    # Investors & Financials
    "investors": {
        "patterns": [
            r"/investor[s]?",
            r"/ir\b",
            r"/financial[s]?",
            r"/annual[-_]?report",
            r"/shareholders?",
            r"/inversionistas?",
        ],
        "keywords": ["investors", "investor relations", "financial", "shareholders"],
        "priority": 8,
    },
    # News & Press
    "news": {
        "patterns": [
            r"/news",
            r"/press",
            r"/media",
            r"/blog",
            r"/noticias",
            r"/prensa",
        ],
        "keywords": ["news", "press", "media", "blog", "noticias"],
        "priority": 7,
    },
    # Contact & Locations
    "contact": {
        "patterns": [
            r"/contact",
            r"/locations?",
            r"/offices?",
            r"/contacto",
            r"/ubicacion",
        ],
        "keywords": ["contact", "locations", "offices", "contacto"],
        "priority": 6,
    },
    # Careers (indicates company size/growth)
    "careers": {
        "patterns": [
            r"/careers?",
            r"/jobs?",
            r"/work[-_]?with[-_]?us",
            r"/employment",
            r"/trabaja[-_]?con[-_]?nosotros",
            r"/empleo",
        ],
        "keywords": ["careers", "jobs", "employment", "trabaja"],
        "priority": 5,
    },
    # Technology & Innovation
    "technology": {
        "patterns": [
            r"/technology",
            r"/innovation",
            r"/r[-_]?and[-_]?d",
            r"/research",
            r"/tecnologia",
            r"/innovacion",
        ],
        "keywords": ["technology", "innovation", "research", "tecnologia"],
        "priority": 4,
    },
}

# Patterns to exclude (low-value pages)
EXCLUDE_PATTERNS = [
    r"/login",
    r"/signin",
    r"/signup",
    r"/register",
    r"/cart",
    r"/checkout",
    r"/privacy",
    r"/terms",
    r"/legal",
    r"/cookie",
    r"/faq",
    r"/help",
    r"/support",
    r"\.pdf$",
    r"\.jpg$",
    r"\.png$",
    r"\.gif$",
    r"\.svg$",
    r"\.css$",
    r"\.js$",
    r"/wp-content/",
    r"/wp-admin/",
    r"/wp-includes/",
]


@dataclass
class LinkInfo:
    """Information about an extracted link."""

    url: str
    text: str
    category: str = "other"
    priority: int = 0
    is_internal: bool = True


@dataclass
class PageContent:
    """Content extracted from a page."""

    url: str
    title: str
    text: str
    links: List[LinkInfo] = field(default_factory=list)
    meta_description: str = ""
    category: str = "other"
    fetch_success: bool = True
    error: Optional[str] = None


@dataclass
class DomainExplorationResult:
    """Result of domain exploration."""

    base_url: str
    domain: str
    pages_explored: List[PageContent] = field(default_factory=list)
    all_links: List[LinkInfo] = field(default_factory=list)
    total_pages_found: int = 0
    pages_fetched: int = 0
    errors: List[str] = field(default_factory=list)


class DomainExplorer:
    """
    Intelligent domain explorer for company research.

    Fetches pages, extracts links, and prioritizes valuable content.
    """

    def __init__(
        self,
        max_pages: int = 10,
        timeout: float = 10.0,
        max_content_length: int = 50000,
        user_agent: str = "CompanyResearcher/1.0 (Research Bot)",
    ):
        """
        Initialize the domain explorer.

        Args:
            max_pages: Maximum pages to fetch per domain
            timeout: HTTP request timeout in seconds
            max_content_length: Maximum content length to process
            user_agent: User agent string for requests
        """
        self.max_pages = max_pages
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.user_agent = user_agent
        self._visited: Set[str] = set()

    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication."""
        parsed = urlparse(url)
        # Remove trailing slash, fragment, and common query params
        path = parsed.path.rstrip("/") or "/"
        return f"{parsed.scheme}://{parsed.netloc}{path}".lower()

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc.lower()

    def _is_same_domain(self, url: str, base_domain: str) -> bool:
        """Check if URL belongs to the same domain."""
        url_domain = self._get_domain(url)
        # Handle www prefix differences
        base_clean = base_domain.replace("www.", "")
        url_clean = url_domain.replace("www.", "")
        return url_clean == base_clean or url_clean.endswith(f".{base_clean}")

    def _should_exclude(self, url: str) -> bool:
        """Check if URL should be excluded."""
        path = urlparse(url).path.lower()
        for pattern in EXCLUDE_PATTERNS:
            if re.search(pattern, path):
                return True
        return False

    def _categorize_link(self, url: str, link_text: str) -> Tuple[str, int]:
        """
        Categorize a link and assign priority.

        Returns:
            Tuple of (category, priority)
        """
        path = urlparse(url).path.lower()
        text_lower = link_text.lower()

        for category, config in PRIORITY_PATTERNS.items():
            # Check URL patterns
            for pattern in config["patterns"]:
                if re.search(pattern, path):
                    return category, config["priority"]
            # Check link text keywords
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    return category, config["priority"]

        return "other", 0

    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text from HTML."""
        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        # Get text
        text = soup.get_text(separator=" ", strip=True)

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)

        # Truncate if too long
        if len(text) > self.max_content_length:
            text = text[: self.max_content_length] + "..."

        return text

    def _extract_links(
        self, soup: BeautifulSoup, base_url: str, base_domain: str
    ) -> List[LinkInfo]:
        """Extract and categorize links from HTML."""
        links = []
        seen_urls = set()

        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]

            # Skip empty, javascript, and mailto links
            if not href or href.startswith(("javascript:", "mailto:", "tel:", "#")):
                continue

            # Resolve relative URLs
            full_url = urljoin(base_url, href)
            normalized = self._normalize_url(full_url)

            # Skip if already seen or visited
            if normalized in seen_urls or normalized in self._visited:
                continue
            seen_urls.add(normalized)

            # Check if internal
            is_internal = self._is_same_domain(full_url, base_domain)

            # Skip excluded URLs
            if is_internal and self._should_exclude(full_url):
                continue

            # Get link text
            link_text = anchor.get_text(strip=True) or ""

            # Categorize
            category, priority = self._categorize_link(full_url, link_text)

            links.append(
                LinkInfo(
                    url=full_url,
                    text=link_text[:100],  # Truncate long text
                    category=category,
                    priority=priority,
                    is_internal=is_internal,
                )
            )

        # Sort by priority (highest first)
        links.sort(key=lambda x: (-x.priority, x.url))

        return links

    async def _fetch_page(self, url: str, client: httpx.AsyncClient) -> PageContent:
        """Fetch and parse a single page."""
        try:
            response = await client.get(
                url,
                follow_redirects=True,
                timeout=self.timeout,
            )
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type:
                return PageContent(
                    url=url,
                    title="",
                    text="",
                    fetch_success=False,
                    error=f"Non-HTML content: {content_type}",
                )

            html = response.text
            soup = BeautifulSoup(html, "lxml")

            # Extract title
            title_tag = soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else ""

            # Extract meta description
            meta_desc = ""
            meta_tag = soup.find("meta", attrs={"name": "description"})
            if meta_tag and meta_tag.get("content"):
                meta_desc = meta_tag["content"]

            # Extract text content
            text = self._extract_text(soup)

            # Extract links
            base_domain = self._get_domain(url)
            links = self._extract_links(soup, url, base_domain)

            # Categorize the page itself
            category, _ = self._categorize_link(url, title)

            return PageContent(
                url=url,
                title=title,
                text=text,
                links=links,
                meta_description=meta_desc,
                category=category,
                fetch_success=True,
            )

        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching {url}")
            return PageContent(
                url=url,
                title="",
                text="",
                fetch_success=False,
                error="Request timeout",
            )
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error {e.response.status_code} for {url}")
            return PageContent(
                url=url,
                title="",
                text="",
                fetch_success=False,
                error=f"HTTP {e.response.status_code}",
            )
        except Exception as e:
            logger.warning(f"Error fetching {url}: {e}")
            return PageContent(
                url=url,
                title="",
                text="",
                fetch_success=False,
                error=str(e),
            )

    async def explore(self, start_url: str) -> DomainExplorationResult:
        """
        Explore a domain starting from a URL.

        Fetches the starting page, extracts links, and follows
        high-priority internal links up to max_pages.

        Args:
            start_url: Starting URL to explore

        Returns:
            DomainExplorationResult with explored pages and links
        """
        base_domain = self._get_domain(start_url)
        self._visited.clear()

        result = DomainExplorationResult(
            base_url=start_url,
            domain=base_domain,
        )

        # Queue of URLs to explore (priority, url)
        to_explore: List[Tuple[int, str]] = [(10, start_url)]
        all_internal_links: List[LinkInfo] = []

        async with httpx.AsyncClient(
            headers={"User-Agent": self.user_agent},
            follow_redirects=True,
        ) as client:
            while to_explore and len(result.pages_explored) < self.max_pages:
                # Get highest priority URL
                to_explore.sort(key=lambda x: -x[0])
                priority, url = to_explore.pop(0)

                normalized = self._normalize_url(url)
                if normalized in self._visited:
                    continue
                self._visited.add(normalized)

                logger.debug(f"Exploring: {url} (priority: {priority})")

                # Fetch and parse page
                page = await self._fetch_page(url, client)

                if page.fetch_success:
                    result.pages_explored.append(page)

                    # Add internal links to explore queue
                    for link in page.links:
                        if link.is_internal:
                            all_internal_links.append(link)
                            link_normalized = self._normalize_url(link.url)
                            if link_normalized not in self._visited:
                                to_explore.append((link.priority, link.url))
                else:
                    result.errors.append(f"{url}: {page.error}")

        # Deduplicate and sort all links
        seen = set()
        unique_links = []
        for link in all_internal_links:
            normalized = self._normalize_url(link.url)
            if normalized not in seen:
                seen.add(normalized)
                unique_links.append(link)

        result.all_links = sorted(unique_links, key=lambda x: (-x.priority, x.url))
        result.total_pages_found = len(seen) + len(self._visited)
        result.pages_fetched = len(result.pages_explored)

        logger.info(
            f"Domain exploration complete: {result.pages_fetched} pages fetched, "
            f"{result.total_pages_found} total links found"
        )

        return result

    def explore_sync(self, start_url: str) -> DomainExplorationResult:
        """Synchronous wrapper for explore()."""
        return asyncio.run(self.explore(start_url))


def explore_domain(
    url: str,
    max_pages: int = 10,
    timeout: float = 10.0,
) -> DomainExplorationResult:
    """
    Convenience function to explore a domain.

    Args:
        url: Starting URL
        max_pages: Maximum pages to fetch
        timeout: Request timeout

    Returns:
        DomainExplorationResult
    """
    explorer = DomainExplorer(max_pages=max_pages, timeout=timeout)
    return explorer.explore_sync(url)


def format_exploration_for_research(result: DomainExplorationResult) -> List[Dict]:
    """
    Format exploration results for the research pipeline.

    Converts DomainExplorationResult to a list of search results
    compatible with the existing researcher agent format.

    Args:
        result: Domain exploration result

    Returns:
        List of result dicts with title, url, content, score
    """
    formatted = []

    for page in result.pages_explored:
        if not page.fetch_success:
            continue

        # Calculate score based on category priority
        category_scores = {
            "leadership": 0.95,
            "products": 0.90,
            "investors": 0.85,
            "news": 0.80,
            "contact": 0.75,
            "careers": 0.70,
            "technology": 0.75,
            "other": 0.60,
        }
        score = category_scores.get(page.category, 0.60)

        formatted.append(
            {
                "title": page.title or page.url,
                "url": page.url,
                "content": page.text[:2000],  # Truncate for API
                "score": score,
                "source": "domain_explorer",
                "category": page.category,
            }
        )

    return formatted
