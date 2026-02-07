"""
Wikipedia API Integration - FREE Company Overview Data.

Access Wikipedia content for company overviews, history, and basic facts.
Completely free, no API key required.

Features:
- Company summary extraction
- Infobox data parsing (founding date, HQ, employees, etc.)
- Related articles and categories
- Multi-language support
- NO API KEY REQUIRED
- UNLIMITED QUERIES

Cost: $0 (completely free)
Provides: Company overviews, history, basic facts, founding dates

Usage:
    from company_researcher.integrations.wikipedia_client import get_wikipedia_client

    wiki = get_wikipedia_client()

    # Get company summary
    info = wiki.get_company_info("Apple Inc.")

    # Search for articles
    results = wiki.search("Tesla Motors")

    # Get full article content
    content = wiki.get_article("Microsoft")
"""

import re
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Dict, List, Optional

import requests

from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class WikipediaInfobox:
    """Parsed Wikipedia infobox data."""

    name: Optional[str] = None
    type: Optional[str] = None  # Public, Private, Subsidiary
    industry: Optional[str] = None
    founded: Optional[str] = None
    founder: Optional[str] = None
    headquarters: Optional[str] = None
    key_people: List[str] = field(default_factory=list)
    products: List[str] = field(default_factory=list)
    revenue: Optional[str] = None
    net_income: Optional[str] = None
    num_employees: Optional[str] = None
    website: Optional[str] = None
    parent: Optional[str] = None
    subsidiaries: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "industry": self.industry,
            "founded": self.founded,
            "founder": self.founder,
            "headquarters": self.headquarters,
            "key_people": self.key_people,
            "products": self.products,
            "revenue": self.revenue,
            "net_income": self.net_income,
            "num_employees": self.num_employees,
            "website": self.website,
            "parent": self.parent,
            "subsidiaries": self.subsidiaries,
        }


@dataclass
class WikipediaArticle:
    """Wikipedia article data."""

    title: str
    page_id: int
    summary: str = ""
    content: str = ""
    url: str = ""
    categories: List[str] = field(default_factory=list)
    infobox: Optional[WikipediaInfobox] = None
    related_articles: List[str] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "page_id": self.page_id,
            "summary": self.summary,
            "content": self.content,
            "url": self.url,
            "categories": self.categories,
            "infobox": self.infobox.to_dict() if self.infobox else None,
            "related_articles": self.related_articles,
            "success": self.success,
            "error": self.error,
        }


@dataclass
class WikipediaSearchResult:
    """Result from Wikipedia search."""

    query: str
    results: List[Dict[str, str]] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "results": self.results,
            "success": self.success,
            "error": self.error,
        }


class WikipediaClient:
    """
    Free Wikipedia API client for company data.

    100% free, no API key required.
    """

    BASE_URL = "https://en.wikipedia.org/w/api.php"

    def __init__(self, language: str = "en", timeout: int = 10):
        """
        Initialize Wikipedia client.

        Args:
            language: Wikipedia language code (en, es, de, fr, etc.)
            timeout: Request timeout in seconds
        """
        self.language = language
        self.timeout = timeout

        # Update base URL for language
        self.base_url = f"https://{language}.wikipedia.org/w/api.php"

        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "CompanyResearcher/1.0 (research@example.com)"})

        self._total_queries = 0
        self._lock = Lock()

    def search(self, query: str, max_results: int = 10) -> WikipediaSearchResult:
        """
        Search Wikipedia for articles.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            WikipediaSearchResult with matching articles
        """
        try:
            params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": max_results,
                "format": "json",
            }

            response = self._session.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            results = []
            for item in data.get("query", {}).get("search", []):
                results.append(
                    {
                        "title": item.get("title", ""),
                        "page_id": str(item.get("pageid", "")),
                        "snippet": re.sub(r"<[^>]+>", "", item.get("snippet", "")),
                    }
                )

            with self._lock:
                self._total_queries += 1

            return WikipediaSearchResult(query=query, results=results, success=True)

        except Exception as e:
            logger.error(f"Wikipedia search error for '{query}': {e}")
            return WikipediaSearchResult(query=query, success=False, error=str(e))

    def get_summary(self, title: str) -> Optional[str]:
        """
        Get article summary (first paragraph).

        Args:
            title: Article title

        Returns:
            Summary text or None
        """
        try:
            params = {
                "action": "query",
                "titles": title,
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "format": "json",
            }

            response = self._session.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            pages = data.get("query", {}).get("pages", {})

            for page_id, page_data in pages.items():
                if page_id != "-1":
                    with self._lock:
                        self._total_queries += 1
                    return page_data.get("extract", "")

            return None

        except Exception as e:
            logger.error(f"Wikipedia summary error for '{title}': {e}")
            return None

    def get_article(self, title: str, include_content: bool = False) -> WikipediaArticle:
        """
        Get full article data.

        Args:
            title: Article title
            include_content: Include full article content

        Returns:
            WikipediaArticle with data
        """
        try:
            # Get basic info and summary
            params = {
                "action": "query",
                "titles": title,
                "prop": "extracts|info|categories|links",
                "exintro": not include_content,
                "explaintext": True,
                "inprop": "url",
                "cllimit": 20,
                "pllimit": 20,
                "format": "json",
            }

            response = self._session.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            pages = data.get("query", {}).get("pages", {})

            for page_id, page_data in pages.items():
                if page_id == "-1":
                    return WikipediaArticle(
                        title=title, page_id=0, success=False, error="Article not found"
                    )

                # Extract categories
                categories = []
                for cat in page_data.get("categories", []):
                    cat_name = cat.get("title", "").replace("Category:", "")
                    if cat_name:
                        categories.append(cat_name)

                # Extract related articles (links)
                related = []
                for link in page_data.get("links", []):
                    link_title = link.get("title", "")
                    if link_title and not link_title.startswith(
                        ("Wikipedia:", "Template:", "Help:")
                    ):
                        related.append(link_title)

                with self._lock:
                    self._total_queries += 1

                return WikipediaArticle(
                    title=page_data.get("title", title),
                    page_id=int(page_id),
                    summary=page_data.get("extract", ""),
                    url=page_data.get("fullurl", ""),
                    categories=categories[:10],
                    related_articles=related[:10],
                    success=True,
                )

            return WikipediaArticle(
                title=title, page_id=0, success=False, error="Article not found"
            )

        except Exception as e:
            logger.error(f"Wikipedia article error for '{title}': {e}")
            return WikipediaArticle(title=title, page_id=0, success=False, error=str(e))

    def get_company_info(self, company_name: str) -> WikipediaArticle:
        """
        Get company information from Wikipedia (with caching).

        Searches for the company and retrieves structured data.

        Args:
            company_name: Company name to search for

        Returns:
            WikipediaArticle with company data
        """
        # Check cache first (30-day TTL)
        try:
            from ..cache.result_cache import cache_wikipedia, get_cached_wikipedia

            cached = get_cached_wikipedia(company_name)
            if cached:
                logger.debug(f"[CACHE HIT] Wikipedia: '{company_name}'")
                # Reconstruct WikipediaArticle from cached dict
                article_dict = cached.copy()
                # Reconstruct infobox if present
                if article_dict.get("infobox"):
                    infobox_data = article_dict["infobox"]
                    article_dict["infobox"] = WikipediaInfobox(**infobox_data)
                return WikipediaArticle(**article_dict)
        except ImportError:
            pass

        # First search for the company
        search_result = self.search(company_name, max_results=5)

        if not search_result.success or not search_result.results:
            return WikipediaArticle(
                title=company_name, page_id=0, success=False, error="Company not found on Wikipedia"
            )

        # Find best match (prioritize exact matches and company-related articles)
        best_match = search_result.results[0]["title"]

        for result in search_result.results:
            title_lower = result["title"].lower()
            company_lower = company_name.lower()

            # Prefer exact match
            if title_lower == company_lower:
                best_match = result["title"]
                break

            # Prefer titles containing "company", "corporation", "Inc"
            if any(term in title_lower for term in ["company", "corporation", "inc", "ltd"]):
                best_match = result["title"]
                break

        # Get full article
        article = self.get_article(best_match)

        # Try to parse infobox data from the extract
        if article.success and article.summary:
            article.infobox = self._parse_company_info(article.summary)

        # Cache results (30 days)
        if article.success:
            try:
                from ..cache.result_cache import cache_wikipedia

                cache_wikipedia(company_name, article.to_dict())
                logger.debug(f"[CACHED] Wikipedia: '{company_name}'")
            except ImportError:
                pass

        return article

    def _parse_company_info(self, text: str) -> WikipediaInfobox:
        """
        Parse company information from article text.

        Args:
            text: Article text to parse

        Returns:
            WikipediaInfobox with extracted data
        """
        infobox = WikipediaInfobox()

        # Try to extract common patterns from the summary
        text_lower = text.lower()

        # Founded year pattern
        founded_patterns = [
            r"founded (?:in |on )?(\d{4})",
            r"established (?:in |on )?(\d{4})",
            r"incorporated (?:in |on )?(\d{4})",
        ]
        for pattern in founded_patterns:
            match = re.search(pattern, text_lower)
            if match:
                infobox.founded = match.group(1)
                break

        # Headquarters pattern
        hq_patterns = [
            r"headquartered in ([^,\.]+)",
            r"based in ([^,\.]+)",
            r"headquarters (?:is |are )?(?:in |at )?([^,\.]+)",
        ]
        for pattern in hq_patterns:
            match = re.search(pattern, text_lower)
            if match:
                infobox.headquarters = match.group(1).strip().title()
                break

        # Employee count pattern
        emp_patterns = [
            r"(\d[\d,]+)\s*employees",
            r"employs?\s*(\d[\d,]+)",
            r"workforce of\s*(\d[\d,]+)",
        ]
        for pattern in emp_patterns:
            match = re.search(pattern, text_lower)
            if match:
                infobox.num_employees = match.group(1).replace(",", "")
                break

        # Industry pattern (usually first sentence)
        industry_keywords = [
            "technology",
            "software",
            "hardware",
            "automotive",
            "retail",
            "financial",
            "bank",
            "insurance",
            "pharmaceutical",
            "healthcare",
            "energy",
            "oil",
            "gas",
            "manufacturing",
            "aerospace",
            "defense",
            "telecommunications",
            "media",
            "entertainment",
            "food",
            "beverage",
        ]
        for keyword in industry_keywords:
            if keyword in text_lower:
                infobox.industry = keyword.title()
                break

        # Company type patterns
        if "public company" in text_lower or "publicly traded" in text_lower:
            infobox.type = "Public"
        elif "private company" in text_lower or "privately held" in text_lower:
            infobox.type = "Private"
        elif "subsidiary" in text_lower:
            infobox.type = "Subsidiary"

        return infobox

    def get_categories(self, title: str) -> List[str]:
        """
        Get article categories.

        Args:
            title: Article title

        Returns:
            List of category names
        """
        try:
            params = {
                "action": "query",
                "titles": title,
                "prop": "categories",
                "cllimit": 50,
                "format": "json",
            }

            response = self._session.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            pages = data.get("query", {}).get("pages", {})

            categories = []
            for page_id, page_data in pages.items():
                if page_id != "-1":
                    for cat in page_data.get("categories", []):
                        cat_name = cat.get("title", "").replace("Category:", "")
                        if cat_name:
                            categories.append(cat_name)

            with self._lock:
                self._total_queries += 1

            return categories

        except Exception as e:
            logger.error(f"Wikipedia categories error for '{title}': {e}")
            return []

    def set_language(self, language: str) -> None:
        """
        Change Wikipedia language.

        Args:
            language: Language code (en, es, de, fr, etc.)
        """
        self.language = language
        self.base_url = f"https://{language}.wikipedia.org/w/api.php"

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        with self._lock:
            return {
                "total_queries": self._total_queries,
                "language": self.language,
                "cost": 0.0,  # FREE!
            }

    def reset_stats(self) -> None:
        """Reset statistics."""
        with self._lock:
            self._total_queries = 0


# Singleton instance
_wikipedia_client: Optional[WikipediaClient] = None
_wiki_lock = Lock()


def get_wikipedia_client(language: str = "en") -> WikipediaClient:
    """Get singleton Wikipedia client instance."""
    global _wikipedia_client
    if _wikipedia_client is None:
        with _wiki_lock:
            if _wikipedia_client is None:
                _wikipedia_client = WikipediaClient(language=language)
    return _wikipedia_client


def reset_wikipedia_client() -> None:
    """Reset Wikipedia client instance."""
    global _wikipedia_client
    _wikipedia_client = None


# Convenience functions
def get_company_summary(company: str) -> Optional[str]:
    """Quick function to get company summary."""
    wiki = get_wikipedia_client()
    result = wiki.get_company_info(company)
    return result.summary if result.success else None


def search_wikipedia(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Quick function to search Wikipedia."""
    wiki = get_wikipedia_client()
    result = wiki.search(query, max_results)
    return result.results if result.success else []
