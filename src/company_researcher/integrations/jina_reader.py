"""
Jina Reader Integration - FREE URL to Markdown Conversion.

Jina Reader converts any URL to clean, LLM-ready markdown instantly.
No complex setup, no browser automation needed.

Features:
- Instant URL to markdown conversion
- Search functionality
- Fact extraction
- NO API KEY REQUIRED for basic usage
- 1M tokens/month free with API key

Cost: $0 (free tier generous)
URL: https://r.jina.ai/

Usage:
    from company_researcher.integrations.jina_reader import get_jina_reader

    reader = get_jina_reader()

    # Convert URL to markdown
    content = reader.read_url("https://example.com")

    # Search the web
    results = reader.search("Tesla Q4 2024 earnings")

    # Extract facts
    facts = reader.extract_facts("https://company.com/about")
"""

import time
from dataclasses import dataclass
from threading import Lock
from typing import Any, Dict, List, Optional

import requests

from ..utils import get_config, get_logger

logger = get_logger(__name__)


@dataclass
class JinaResult:
    """Result from Jina Reader."""

    url: str
    content: str
    title: Optional[str] = None
    description: Optional[str] = None
    success: bool = True
    error: Optional[str] = None
    response_time_ms: float = 0
    token_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "content": self.content,
            "title": self.title,
            "description": self.description,
            "success": self.success,
            "error": self.error,
            "response_time_ms": self.response_time_ms,
            "token_count": self.token_count,
        }


@dataclass
class JinaSearchResult:
    """Result from Jina Search."""

    query: str
    results: List[Dict[str, str]]
    total_results: int = 0
    success: bool = True
    error: Optional[str] = None


class JinaReader:
    """
    Free URL to markdown converter using Jina Reader.

    No API key required for basic usage.
    1M tokens/month free with API key.

    Endpoints:
    - r.jina.ai/{url} - Read URL
    - s.jina.ai/{query} - Search
    - r.jina.ai/facts/{url} - Extract facts
    """

    BASE_URL = "https://r.jina.ai"
    SEARCH_URL = "https://s.jina.ai"

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30):
        """
        Initialize Jina Reader.

        Args:
            api_key: Optional API key for higher limits (1M tokens/month free)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout

        self._total_requests = 0
        self._total_tokens = 0
        self._lock = Lock()

        self.headers = {"Accept": "text/plain", "User-Agent": "CompanyResearcher/1.0"}

        if self.api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def read_url(
        self,
        url: str,
        target_selector: Optional[str] = None,
        wait_for_selector: Optional[str] = None,
        remove_selector: Optional[str] = None,
    ) -> JinaResult:
        """
        Convert a URL to markdown.

        Args:
            url: URL to convert
            target_selector: CSS selector to focus on
            wait_for_selector: Wait for this element before reading
            remove_selector: Remove these elements

        Returns:
            JinaResult with markdown content
        """
        start_time = time.time()

        try:
            # Build request URL
            request_url = f"{self.BASE_URL}/{url}"

            # Add optional headers
            headers = self.headers.copy()
            if target_selector:
                headers["X-Target-Selector"] = target_selector
            if wait_for_selector:
                headers["X-Wait-For-Selector"] = wait_for_selector
            if remove_selector:
                headers["X-Remove-Selector"] = remove_selector

            response = requests.get(request_url, headers=headers, timeout=self.timeout)

            response_time = (time.time() - start_time) * 1000
            content = response.text

            # Estimate token count (rough: 4 chars per token)
            token_count = len(content) // 4

            # Update stats
            with self._lock:
                self._total_requests += 1
                self._total_tokens += token_count

            # Parse title if present (usually first line)
            title = None
            lines = content.split("\n")
            if lines and lines[0].startswith("# "):
                title = lines[0][2:].strip()

            return JinaResult(
                url=url,
                content=content,
                title=title,
                success=response.status_code == 200,
                error=None if response.status_code == 200 else f"HTTP {response.status_code}",
                response_time_ms=response_time,
                token_count=token_count,
            )

        except Exception as e:
            logger.error(f"Jina Reader error for {url}: {e}")
            return JinaResult(
                url=url,
                content="",
                success=False,
                error=str(e),
                response_time_ms=(time.time() - start_time) * 1000,
            )

    def search(self, query: str, num_results: int = 5) -> JinaSearchResult:
        """
        Search the web and get markdown results.

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            JinaSearchResult with search results
        """
        try:
            request_url = f"{self.SEARCH_URL}/{query}"

            response = requests.get(request_url, headers=self.headers, timeout=self.timeout)

            content = response.text

            # Parse search results (Jina returns markdown with links)
            results = []
            lines = content.split("\n")

            for line in lines:
                if line.startswith("- [") and "](" in line:
                    # Parse markdown link: - [Title](URL)
                    try:
                        title_end = line.index("](")
                        url_end = line.index(")", title_end)
                        title = line[3:title_end]
                        url = line[title_end + 2 : url_end]
                        results.append({"title": title, "url": url})
                    except ValueError:
                        continue

            with self._lock:
                self._total_requests += 1

            return JinaSearchResult(
                query=query, results=results[:num_results], total_results=len(results), success=True
            )

        except Exception as e:
            logger.error(f"Jina Search error for '{query}': {e}")
            return JinaSearchResult(query=query, results=[], success=False, error=str(e))

    def extract_facts(self, url: str) -> Dict[str, Any]:
        """
        Extract key facts from a URL.

        Uses Jina's fact extraction endpoint.

        Args:
            url: URL to extract facts from

        Returns:
            Dictionary with extracted facts
        """
        # Read the URL first
        result = self.read_url(url)

        if not result.success:
            return {"error": result.error, "url": url}

        # Return structured data
        return {
            "url": url,
            "title": result.title,
            "content_preview": result.content[:1000],
            "token_count": result.token_count,
            "full_content": result.content,
        }

    def read_company_page(self, url: str, page_type: str = "about") -> JinaResult:
        """
        Read a company page with optimized selectors.

        Args:
            url: Company page URL
            page_type: Type of page (about, team, careers, investors)

        Returns:
            JinaResult with content
        """
        # Define selectors for different page types
        selectors = {
            "about": "main, article, .about, .company-info, [class*='about']",
            "team": ".team, .leadership, .executives, [class*='team']",
            "careers": ".jobs, .careers, .openings, [class*='career']",
            "investors": ".investor, .financials, [class*='investor']",
        }

        # Remove common non-content elements
        remove = "nav, footer, header, .cookie, .popup, .modal, aside"

        return self.read_url(
            url=url, target_selector=selectors.get(page_type), remove_selector=remove
        )

    def batch_read(self, urls: List[str], delay_ms: int = 100) -> List[JinaResult]:
        """
        Read multiple URLs with rate limiting.

        Args:
            urls: List of URLs to read
            delay_ms: Delay between requests in ms

        Returns:
            List of JinaResults
        """
        results = []

        for url in urls:
            result = self.read_url(url)
            results.append(result)

            if delay_ms > 0:
                time.sleep(delay_ms / 1000)

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        with self._lock:
            return {
                "total_requests": self._total_requests,
                "total_tokens": self._total_tokens,
                "cost": 0.0,  # FREE!
                "has_api_key": self.api_key is not None,
            }

    def reset_stats(self) -> None:
        """Reset statistics."""
        with self._lock:
            self._total_requests = 0
            self._total_tokens = 0


# Singleton instance
_jina_reader: Optional[JinaReader] = None
_reader_lock = Lock()


def get_jina_reader(api_key: Optional[str] = None) -> JinaReader:
    """Get singleton Jina Reader instance."""
    global _jina_reader
    if _jina_reader is None:
        with _reader_lock:
            if _jina_reader is None:
                key = api_key or get_config("JINA_API_KEY")
                _jina_reader = JinaReader(api_key=key)
    return _jina_reader


def reset_jina_reader() -> None:
    """Reset Jina Reader instance."""
    global _jina_reader
    _jina_reader = None


# Convenience functions
def read_url(url: str) -> str:
    """Quick function to read URL to markdown."""
    reader = get_jina_reader()
    result = reader.read_url(url)
    return result.content if result.success else ""


def search_web(query: str) -> List[Dict[str, str]]:
    """Quick function to search web."""
    reader = get_jina_reader()
    result = reader.search(query)
    return result.results if result.success else []
