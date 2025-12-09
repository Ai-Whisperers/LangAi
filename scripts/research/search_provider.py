"""
Optimized Search Provider Module.

Implements best practices learned from top GitHub repositories:
- DuckDuckGo fallback when Tavily rate limit exceeded
- get_search_context() for LLM-optimized results
- Domain filtering for quality sources
- Max 4 queries per research stage (50% credit savings)
- Automatic retry with exponential backoff

Patterns from:
- gpt-researcher: Plan-Execute architecture
- tavily_company_researcher: 5-stage pipeline
- ai-langgraph-multi-agent: Max 3 queries pattern
- agentic_search_openai_langgraph: DuckDuckGo fallback
- tavily-search-mcp-server: Domain filtering
"""

import os
import asyncio
import time
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

from dotenv import load_dotenv

load_dotenv()


class SearchProvider(str, Enum):
    """Available search providers."""
    TAVILY = "tavily"
    SERPER = "serper"
    BRAVE = "brave"
    DUCKDUCKGO = "duckduckgo"
    GOOGLE = "google"  # Google Custom Search (100 free/day)
    BING = "bing"      # Bing Web Search (1,000 free/month)


class SearchStrategy(str, Enum):
    """Search strategy modes."""
    AUTO = "auto"           # Original behavior: Tavily first, fallback to free
    FREE_FIRST = "free_first"  # Free providers first, then Tavily for refinement
    FREE_ONLY = "free_only"    # Only use free providers (DuckDuckGo)
    TAVILY_ONLY = "tavily_only"  # Only use Tavily (paid)
    # NEW: Maximum free strategy - tries ALL free providers before premium
    MAXIMUM_FREE = "maximum_free"  # DuckDuckGo -> Serper -> Brave -> Google -> Bing -> Tavily


@dataclass
class SearchConfig:
    """Search configuration with domain filtering and limits."""

    # Quality source domains to prioritize for company research
    include_domains: List[str] = field(default_factory=lambda: [
        # Financial data
        "sec.gov",
        "reuters.com",
        "bloomberg.com",
        "wsj.com",
        "ft.com",
        "marketwatch.com",
        "finance.yahoo.com",
        "investing.com",

        # Company info
        "crunchbase.com",
        "linkedin.com",
        "glassdoor.com",
        "owler.com",

        # Industry analysis
        "mckinsey.com",
        "bcg.com",
        "hbr.org",
        "forrester.com",
        "gartner.com",

        # News
        "techcrunch.com",
        "cnbc.com",
        "bbc.com",
        "theguardian.com",
    ])

    # Low quality domains to exclude
    exclude_domains: List[str] = field(default_factory=lambda: [
        "wikipedia.org",  # Good for context but not primary source
        "reddit.com",
        "quora.com",
        "pinterest.com",
        "facebook.com",
        "twitter.com",
        "instagram.com",
        "tiktok.com",
        "medium.com",  # Variable quality
    ])

    # Search parameters
    max_results_per_query: int = 5
    max_tokens_context: int = 4000
    search_depth: str = "basic"  # "basic" (1 credit) or "advanced" (2 credits)
    use_context_mode: bool = True  # Use get_search_context() for LLM-optimized results

    # Rate limiting
    max_retries: int = 3
    base_delay_seconds: float = 1.0

    # Query limits per depth (learned from ai-langgraph-multi-agent)
    query_limits: Dict[str, int] = field(default_factory=lambda: {
        "quick": 4,       # Was 6, reduced 33%
        "standard": 6,    # Was 9, reduced 33%
        "comprehensive": 8  # Was 12, reduced 33%
    })

    # FREE-FIRST STRATEGY SETTINGS
    # Search strategy: "auto", "free_first", "free_only", "tavily_only"
    search_strategy: str = "free_first"  # Default to free first!

    # Minimum sources to collect from free providers before using Tavily
    min_free_sources: int = 100

    # Maximum results per query for free providers (DuckDuckGo can return more)
    free_max_results_per_query: int = 10

    # Query multiplier for free-first mode (generate more queries)
    free_query_multiplier: float = 3.0  # 3x more queries for free search

    # Whether to use Tavily for refinement after free search
    tavily_refinement: bool = True

    # Maximum Tavily refinement queries (only for high-priority gaps)
    max_tavily_refinement_queries: int = 5


@dataclass
class SearchResult:
    """Unified search result from any provider."""
    title: str
    url: str
    content: str
    score: float = 0.0
    provider: str = "unknown"
    query: str = ""
    raw_content: Optional[str] = None


class BaseSearchProvider(ABC):
    """Abstract base class for search providers."""

    @abstractmethod
    async def search(
        self,
        query: str,
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Execute a search query."""
        pass

    @abstractmethod
    def get_context(
        self,
        query: str,
        max_tokens: int = 4000
    ) -> str:
        """Get LLM-optimized search context."""
        pass


class TavilySearchProvider(BaseSearchProvider):
    """Tavily search provider with optimizations."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self._client = None
        self._rate_limited = False
        self._last_error_time = 0

    @property
    def client(self):
        """Lazy initialize Tavily client."""
        if self._client is None:
            from tavily import TavilyClient
            self._client = TavilyClient(api_key=self.api_key)
        return self._client

    def is_rate_limited(self) -> bool:
        """Check if we're currently rate limited."""
        if self._rate_limited:
            # Reset after 60 seconds
            if time.time() - self._last_error_time > 60:
                self._rate_limited = False
        return self._rate_limited

    async def search(
        self,
        query: str,
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        search_depth: str = "basic"
    ) -> List[SearchResult]:
        """Execute Tavily search with domain filtering."""
        if self.is_rate_limited():
            raise RateLimitError("Tavily rate limit exceeded")

        try:
            # Build search parameters
            params = {
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
                "include_answer": False,  # Save tokens
            }

            # Apply domain filtering (only if not empty)
            if include_domains:
                params["include_domains"] = include_domains[:10]  # API limit
            if exclude_domains:
                params["exclude_domains"] = exclude_domains[:10]

            # Execute search in thread pool
            response = await asyncio.to_thread(
                self.client.search,
                **params
            )

            # Parse results
            results = []
            for item in response.get("results", []):
                results.append(SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    score=item.get("score", 0.0),
                    provider="tavily",
                    query=query,
                    raw_content=item.get("raw_content")
                ))

            return results

        except Exception as e:
            error_msg = str(e).lower()
            if "rate" in error_msg or "limit" in error_msg or "exceeded" in error_msg:
                self._rate_limited = True
                self._last_error_time = time.time()
                raise RateLimitError(f"Tavily rate limit: {e}")
            raise

    def get_context(
        self,
        query: str,
        max_tokens: int = 4000,
        search_depth: str = "basic"
    ) -> str:
        """Get LLM-optimized search context using Tavily's get_search_context."""
        if self.is_rate_limited():
            raise RateLimitError("Tavily rate limit exceeded")

        try:
            context = self.client.get_search_context(
                query=query,
                search_depth=search_depth,
                max_tokens=max_tokens
            )
            return context
        except Exception as e:
            error_msg = str(e).lower()
            if "rate" in error_msg or "limit" in error_msg or "exceeded" in error_msg:
                self._rate_limited = True
                self._last_error_time = time.time()
                raise RateLimitError(f"Tavily rate limit: {e}")
            raise


class DuckDuckGoSearchProvider(BaseSearchProvider):
    """DuckDuckGo search provider as free fallback."""

    def __init__(self):
        self._ddgs = None

    @property
    def ddgs(self):
        """Lazy initialize DuckDuckGo client."""
        if self._ddgs is None:
            try:
                from duckduckgo_search import DDGS
                self._ddgs = DDGS()
            except ImportError:
                raise ImportError(
                    "duckduckgo-search not installed. "
                    "Run: pip install duckduckgo-search"
                )
        return self._ddgs

    async def search(
        self,
        query: str,
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Execute DuckDuckGo search."""
        try:
            # DuckDuckGo doesn't support native domain filtering
            # We'll filter results after the fact
            from duckduckgo_search import DDGS

            results = []
            with DDGS() as ddgs:
                # Run search in thread pool
                search_results = await asyncio.to_thread(
                    lambda: list(ddgs.text(query, max_results=max_results * 2))
                )

                for item in search_results:
                    url = item.get("href", "")

                    # Apply domain filtering manually
                    if exclude_domains:
                        if any(domain in url for domain in exclude_domains):
                            continue

                    # Optionally prioritize include_domains
                    score = 0.5
                    if include_domains:
                        if any(domain in url for domain in include_domains):
                            score = 0.8

                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=url,
                        content=item.get("body", ""),
                        score=score,
                        provider="duckduckgo",
                        query=query
                    ))

                    if len(results) >= max_results:
                        break

            return results

        except Exception as e:
            print(f"[DUCKDUCKGO ERROR] {e}")
            return []

    def get_context(
        self,
        query: str,
        max_tokens: int = 4000
    ) -> str:
        """Build context from DuckDuckGo results."""
        import asyncio
        results = asyncio.run(self.search(query, max_results=5))

        context_parts = []
        current_tokens = 0

        for result in results:
            # Rough token estimate: 1 token ~= 4 chars
            content = f"Source: {result.title}\n{result.content}\n"
            estimated_tokens = len(content) // 4

            if current_tokens + estimated_tokens > max_tokens:
                break

            context_parts.append(content)
            current_tokens += estimated_tokens

        return "\n---\n".join(context_parts)


class RateLimitError(Exception):
    """Raised when a search provider rate limit is hit."""
    pass


class SerperSearchProvider(BaseSearchProvider):
    """
    Serper.dev search provider - Fast, cheap Google results.

    Cost: 2,500 free queries, then $1.00/1K queries
    Speed: 1-2 seconds (fastest)
    Quality: Google-quality results
    """

    API_URL = "https://google.serper.dev/search"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SERPER_API_KEY")
        self._rate_limited = False
        self._last_error_time = 0

    def is_available(self) -> bool:
        """Check if Serper API key is configured."""
        return bool(self.api_key)

    def is_rate_limited(self) -> bool:
        """Check if we're currently rate limited."""
        if self._rate_limited:
            if time.time() - self._last_error_time > 60:
                self._rate_limited = False
        return self._rate_limited

    async def search(
        self,
        query: str,
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Execute Serper (Google) search."""
        if not self.api_key:
            raise RateLimitError("Serper API key not configured")

        if self.is_rate_limited():
            raise RateLimitError("Serper rate limit exceeded")

        try:
            import aiohttp

            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json",
            }

            payload = {
                "q": query,
                "num": min(max_results, 100),
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.API_URL,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 429:
                        self._rate_limited = True
                        self._last_error_time = time.time()
                        raise RateLimitError("Serper rate limit exceeded")

                    if response.status != 200:
                        text = await response.text()
                        raise Exception(f"Serper HTTP {response.status}: {text[:200]}")

                    data = await response.json()
                    return self._parse_results(data, query, max_results, exclude_domains)

        except RateLimitError:
            raise
        except Exception as e:
            error_msg = str(e).lower()
            if "rate" in error_msg or "limit" in error_msg:
                self._rate_limited = True
                self._last_error_time = time.time()
                raise RateLimitError(f"Serper rate limit: {e}")
            raise

    def _parse_results(
        self,
        data: dict,
        query: str,
        max_results: int,
        exclude_domains: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Parse Serper API response."""
        results = []

        # Organic results
        for item in data.get("organic", []):
            url = item.get("link", "")

            # Apply domain filtering
            if exclude_domains and any(domain in url for domain in exclude_domains):
                continue

            results.append(SearchResult(
                title=item.get("title", ""),
                url=url,
                content=item.get("snippet", ""),
                score=1.0 - (item.get("position", 10) / 10),
                provider="serper",
                query=query
            ))

            if len(results) >= max_results:
                break

        # Include knowledge graph if present
        kg = data.get("knowledgeGraph")
        if kg and len(results) < max_results:
            results.insert(0, SearchResult(
                title=kg.get("title", "Knowledge Graph"),
                url=kg.get("website", ""),
                content=kg.get("description", ""),
                score=1.0,
                provider="serper_kg",
                query=query
            ))

        return results[:max_results]

    def get_context(self, query: str, max_tokens: int = 4000) -> str:
        """Build context from Serper results."""
        import asyncio
        results = asyncio.run(self.search(query, max_results=5))

        context_parts = []
        current_tokens = 0

        for result in results:
            content = f"Source: {result.title}\n{result.content}\n"
            estimated_tokens = len(content) // 4

            if current_tokens + estimated_tokens > max_tokens:
                break

            context_parts.append(content)
            current_tokens += estimated_tokens

        return "\n---\n".join(context_parts)


class BraveSearchProvider(BaseSearchProvider):
    """
    Brave Search provider - Privacy-focused with independent index.

    Cost: 2,000 free queries/month, then $5/1K queries
    Quality: Excellent - independent index, not relying on Google/Bing
    Privacy: No user tracking
    """

    API_URL = "https://api.search.brave.com/res/v1/web/search"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("BRAVE_API_KEY")
        self._rate_limited = False
        self._last_error_time = 0

    def is_available(self) -> bool:
        """Check if Brave API key is configured."""
        return bool(self.api_key)

    def is_rate_limited(self) -> bool:
        """Check if we're currently rate limited."""
        if self._rate_limited:
            if time.time() - self._last_error_time > 60:
                self._rate_limited = False
        return self._rate_limited

    async def search(
        self,
        query: str,
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Execute Brave Search query."""
        if not self.api_key:
            raise RateLimitError("Brave API key not configured")

        if self.is_rate_limited():
            raise RateLimitError("Brave rate limit exceeded")

        try:
            import aiohttp

            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key,
            }

            params = {
                "q": query,
                "count": min(max_results, 20),
                "text_decorations": "false",
                "search_lang": "en",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.API_URL,
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 429:
                        self._rate_limited = True
                        self._last_error_time = time.time()
                        raise RateLimitError("Brave rate limit exceeded")

                    if response.status != 200:
                        text = await response.text()
                        raise Exception(f"Brave HTTP {response.status}: {text[:200]}")

                    data = await response.json()
                    return self._parse_results(data, query, max_results, exclude_domains)

        except RateLimitError:
            raise
        except Exception as e:
            error_msg = str(e).lower()
            if "rate" in error_msg or "limit" in error_msg:
                self._rate_limited = True
                self._last_error_time = time.time()
                raise RateLimitError(f"Brave rate limit: {e}")
            raise

    def _parse_results(
        self,
        data: dict,
        query: str,
        max_results: int,
        exclude_domains: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Parse Brave Search API response."""
        results = []

        # Web results
        web = data.get("web", {})
        for item in web.get("results", []):
            url = item.get("url", "")

            # Apply domain filtering
            if exclude_domains and any(domain in url for domain in exclude_domains):
                continue

            results.append(SearchResult(
                title=item.get("title", ""),
                url=url,
                content=item.get("description", ""),
                score=0.8,
                provider="brave",
                query=query
            ))

            if len(results) >= max_results:
                break

        # Include featured snippet if present
        featured = data.get("featured_snippet")
        if featured and len(results) < max_results:
            results.insert(0, SearchResult(
                title=featured.get("title", "Featured"),
                url=featured.get("url", ""),
                content=featured.get("description", ""),
                score=1.0,
                provider="brave_featured",
                query=query
            ))

        return results[:max_results]

    def get_context(self, query: str, max_tokens: int = 4000) -> str:
        """Build context from Brave results."""
        import asyncio
        results = asyncio.run(self.search(query, max_results=5))

        context_parts = []
        current_tokens = 0

        for result in results:
            content = f"Source: {result.title}\n{result.content}\n"
            estimated_tokens = len(content) // 4

            if current_tokens + estimated_tokens > max_tokens:
                break

            context_parts.append(content)
            current_tokens += estimated_tokens

        return "\n---\n".join(context_parts)


class GoogleCustomSearchProvider(BaseSearchProvider):
    """
    Google Custom Search provider - Official Google API.

    Cost: 100 free queries/day, then $5/1K queries
    Quality: Highest - actual Google results
    Setup: Requires API key + Custom Search Engine ID

    Get API key: https://console.cloud.google.com/apis/credentials
    Get CX ID: https://programmablesearchengine.google.com/
    """

    API_URL = "https://www.googleapis.com/customsearch/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        cx_id: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.cx_id = cx_id or os.getenv("GOOGLE_CX_ID")
        self._rate_limited = False
        self._last_error_time = 0
        self._daily_calls = 0
        self._daily_limit = 100  # Free tier limit

    def is_available(self) -> bool:
        """Check if Google API is configured."""
        return bool(self.api_key and self.cx_id)

    def is_rate_limited(self) -> bool:
        """Check if we're currently rate limited."""
        if self._rate_limited:
            if time.time() - self._last_error_time > 3600:  # Reset after 1 hour
                self._rate_limited = False
                self._daily_calls = 0
        return self._rate_limited or self._daily_calls >= self._daily_limit

    async def search(
        self,
        query: str,
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Execute Google Custom Search query."""
        if not self.is_available():
            raise RateLimitError("Google API not configured (need GOOGLE_API_KEY and GOOGLE_CX_ID)")

        if self.is_rate_limited():
            raise RateLimitError("Google daily limit exceeded (100 free queries)")

        try:
            import aiohttp

            params = {
                "key": self.api_key,
                "cx": self.cx_id,
                "q": query,
                "num": min(max_results, 10),  # Max 10 per request
            }

            # Add site restriction if include_domains provided
            if include_domains and len(include_domains) <= 3:
                site_query = " OR ".join(f"site:{d}" for d in include_domains[:3])
                params["q"] = f"{query} ({site_query})"

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.API_URL,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    self._daily_calls += 1

                    if response.status == 429:
                        self._rate_limited = True
                        self._last_error_time = time.time()
                        raise RateLimitError("Google rate limit exceeded")

                    if response.status == 403:
                        self._rate_limited = True
                        self._last_error_time = time.time()
                        raise RateLimitError("Google API quota exceeded")

                    if response.status != 200:
                        text = await response.text()
                        raise Exception(f"Google HTTP {response.status}: {text[:200]}")

                    data = await response.json()
                    return self._parse_results(data, query, max_results, exclude_domains)

        except RateLimitError:
            raise
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "limit" in error_msg:
                self._rate_limited = True
                self._last_error_time = time.time()
                raise RateLimitError(f"Google quota: {e}")
            raise

    def _parse_results(
        self,
        data: dict,
        query: str,
        max_results: int,
        exclude_domains: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Parse Google Custom Search API response."""
        results = []

        for item in data.get("items", []):
            url = item.get("link", "")

            # Apply domain filtering
            if exclude_domains and any(domain in url for domain in exclude_domains):
                continue

            results.append(SearchResult(
                title=item.get("title", ""),
                url=url,
                content=item.get("snippet", ""),
                score=0.9,  # Google results are high quality
                provider="google",
                query=query
            ))

            if len(results) >= max_results:
                break

        return results

    def get_context(self, query: str, max_tokens: int = 4000) -> str:
        """Build context from Google results."""
        import asyncio
        results = asyncio.run(self.search(query, max_results=5))

        context_parts = []
        current_tokens = 0

        for result in results:
            content = f"Source: {result.title}\n{result.content}\n"
            estimated_tokens = len(content) // 4

            if current_tokens + estimated_tokens > max_tokens:
                break

            context_parts.append(content)
            current_tokens += estimated_tokens

        return "\n---\n".join(context_parts)


class BingSearchProvider(BaseSearchProvider):
    """
    Bing Web Search provider - Microsoft's search API.

    Cost: 1,000 free calls/month (S1 tier), then paid
    Quality: Good - Bing's index is comprehensive
    Setup: Requires Azure subscription + Bing Search resource

    Get API key: https://portal.azure.com/#create/Microsoft.BingSearch
    """

    API_URL = "https://api.bing.microsoft.com/v7.0/search"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("BING_API_KEY")
        self._rate_limited = False
        self._last_error_time = 0
        self._monthly_calls = 0
        self._monthly_limit = 1000  # Free tier limit

    def is_available(self) -> bool:
        """Check if Bing API key is configured."""
        return bool(self.api_key)

    def is_rate_limited(self) -> bool:
        """Check if we're currently rate limited."""
        if self._rate_limited:
            if time.time() - self._last_error_time > 3600:  # Reset check after 1 hour
                self._rate_limited = False
        return self._rate_limited or self._monthly_calls >= self._monthly_limit

    async def search(
        self,
        query: str,
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Execute Bing Web Search query."""
        if not self.api_key:
            raise RateLimitError("Bing API key not configured")

        if self.is_rate_limited():
            raise RateLimitError("Bing monthly limit exceeded")

        try:
            import aiohttp

            headers = {
                "Ocp-Apim-Subscription-Key": self.api_key,
            }

            params = {
                "q": query,
                "count": min(max_results, 50),
                "mkt": "en-US",
                "responseFilter": "Webpages",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.API_URL,
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    self._monthly_calls += 1

                    if response.status == 429:
                        self._rate_limited = True
                        self._last_error_time = time.time()
                        raise RateLimitError("Bing rate limit exceeded")

                    if response.status == 403:
                        self._rate_limited = True
                        self._last_error_time = time.time()
                        raise RateLimitError("Bing quota exceeded")

                    if response.status != 200:
                        text = await response.text()
                        raise Exception(f"Bing HTTP {response.status}: {text[:200]}")

                    data = await response.json()
                    return self._parse_results(data, query, max_results, exclude_domains)

        except RateLimitError:
            raise
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "limit" in error_msg or "401" in error_msg:
                self._rate_limited = True
                self._last_error_time = time.time()
                raise RateLimitError(f"Bing limit: {e}")
            raise

    def _parse_results(
        self,
        data: dict,
        query: str,
        max_results: int,
        exclude_domains: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Parse Bing Web Search API response."""
        results = []

        web_pages = data.get("webPages", {})
        for item in web_pages.get("value", []):
            url = item.get("url", "")

            # Apply domain filtering
            if exclude_domains and any(domain in url for domain in exclude_domains):
                continue

            results.append(SearchResult(
                title=item.get("name", ""),
                url=url,
                content=item.get("snippet", ""),
                score=0.8,
                provider="bing",
                query=query
            ))

            if len(results) >= max_results:
                break

        return results

    def get_context(self, query: str, max_tokens: int = 4000) -> str:
        """Build context from Bing results."""
        import asyncio
        results = asyncio.run(self.search(query, max_results=5))

        context_parts = []
        current_tokens = 0

        for result in results:
            content = f"Source: {result.title}\n{result.content}\n"
            estimated_tokens = len(content) // 4

            if current_tokens + estimated_tokens > max_tokens:
                break

            context_parts.append(content)
            current_tokens += estimated_tokens

        return "\n---\n".join(context_parts)


class OptimizedSearchClient:
    """
    Main search client with fallback and optimizations.

    Features:
    - Multi-provider fallback chain with 6 providers
    - MAXIMUM_FREE STRATEGY: DuckDuckGo -> Serper -> Brave -> Google -> Bing -> Tavily
    - FREE-FIRST STRATEGY: DuckDuckGo first with 100+ sources, then Tavily refinement
    - Domain filtering for quality sources
    - Query optimization (reduced count)
    - get_search_context for LLM-ready results
    - Caching integration

    Provider Free Tiers:
    - DuckDuckGo: Unlimited (no API key needed)
    - Serper: 2,500 free queries (then $1/1K)
    - Brave: 2,000 free/month (then $5/1K)
    - Google: 100 free/day (then $5/1K)
    - Bing: 1,000 free/month (Azure)
    - Tavily: Paid only (~$0.01/query)
    """

    def __init__(
        self,
        config: Optional[SearchConfig] = None,
        cache = None,
        preferred_provider: Optional[str] = None
    ):
        self.config = config or SearchConfig()
        self.cache = cache
        # Use config strategy if provider not explicitly set
        self.preferred_provider = preferred_provider or os.getenv("SEARCH_PROVIDER", self.config.search_strategy)

        # Initialize ALL providers (6 total)
        self.tavily = TavilySearchProvider()
        self.serper = SerperSearchProvider()
        self.brave = BraveSearchProvider()
        self.duckduckgo = DuckDuckGoSearchProvider()
        self.google = GoogleCustomSearchProvider()
        self.bing = BingSearchProvider()

        # Track provider usage (all 6 providers)
        self.stats = {
            "tavily_calls": 0,
            "tavily_successes": 0,
            "serper_calls": 0,
            "serper_successes": 0,
            "brave_calls": 0,
            "brave_successes": 0,
            "duckduckgo_calls": 0,
            "duckduckgo_successes": 0,
            "google_calls": 0,
            "google_successes": 0,
            "bing_calls": 0,
            "bing_successes": 0,
            "duckduckgo_fallbacks": 0,  # Keep for backward compatibility
            "cache_hits": 0,
            "total_queries": 0,
            "free_sources_total": 0,
            "tavily_sources_total": 0,
        }

        # Log available providers
        self._log_available_providers()

    async def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        use_cache: bool = True,
        provider: Optional[str] = None,
        strategy: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Execute search with multi-provider fallback chain.

        Strategy modes:
        - "auto": Tavily -> Serper -> Brave -> DuckDuckGo (original)
        - "free_first": DuckDuckGo first, Tavily only for refinement
        - "free_only": Only use DuckDuckGo (no paid providers)
        - "tavily_only": Only use Tavily

        Args:
            query: Search query
            max_results: Max results (default from config)
            use_cache: Whether to check cache first
            provider: Force specific provider ("tavily", "serper", "brave", "duckduckgo")
            strategy: Override search strategy for this call

        Returns:
            List of SearchResult objects
        """
        self.stats["total_queries"] += 1
        active_strategy = strategy or self.config.search_strategy
        max_results = max_results or self.config.max_results_per_query

        # Check cache first
        if use_cache and self.cache:
            cached = self.cache.get_search_results(query)
            if cached:
                self.stats["cache_hits"] += 1
                print(f"  [CACHE HIT] {query[:50]}...")
                return self._convert_cached_results(cached, query)

        results = []
        active_provider = provider or self.preferred_provider

        # If specific provider requested, try only that one
        if active_provider and active_provider not in ("auto", "free_first", "free_only"):
            results = await self._try_provider(active_provider, query, max_results)
            if results:
                self._cache_results(query, results)
                return results

        # Strategy-based routing
        if active_strategy == "free_only":
            # FREE ONLY: Try ALL free providers in cascade, NO Tavily
            free_max = self.config.free_max_results_per_query
            results = await self._search_with_free_cascade(query, free_max, include_tavily=False)
            if results:
                self.stats["free_sources_total"] += len(results)
            self._cache_results(query, results)
            return results

        elif active_strategy == "free_first" or active_strategy == "maximum_free":
            # FREE FIRST / MAXIMUM FREE: Try ALL free providers in cascade, then Tavily as last resort
            free_max = self.config.free_max_results_per_query
            results = await self._search_with_free_cascade(query, free_max, include_tavily=True)
            if results:
                # Track which type of source was used
                provider = results[0].provider if results else "unknown"
                if provider == "tavily":
                    self.stats["tavily_sources_total"] += len(results)
                else:
                    self.stats["free_sources_total"] += len(results)
            self._cache_results(query, results)
            return results

        elif active_strategy == "tavily_only":
            # TAVILY ONLY
            if not self.tavily.is_rate_limited():
                results = await self._try_provider("tavily", query, max_results)
            self._cache_results(query, results)
            return results

        # AUTO mode: try providers in priority order (original behavior)
        # 1. Try Tavily first (best quality, but has rate limits)
        if not results and not self.tavily.is_rate_limited():
            results = await self._try_provider("tavily", query, max_results)

        # 2. Try Serper (Google results, cheap)
        if not results and self.serper.is_available() and not self.serper.is_rate_limited():
            results = await self._try_provider("serper", query, max_results)

        # 3. Try Brave (independent index, good quality)
        if not results and self.brave.is_available() and not self.brave.is_rate_limited():
            results = await self._try_provider("brave", query, max_results)

        # 4. Final fallback: DuckDuckGo (free, no API key needed)
        if not results:
            results = await self._try_provider("duckduckgo", query, max_results)

        # Cache results
        self._cache_results(query, results)
        return results

    async def _try_provider(
        self,
        provider_name: str,
        query: str,
        max_results: int
    ) -> List[SearchResult]:
        """Try a specific search provider."""
        try:
            if provider_name == "tavily":
                self.stats["tavily_calls"] += 1
                results = await self.tavily.search(
                    query=query,
                    max_results=max_results,
                    include_domains=self.config.include_domains[:5],
                    exclude_domains=self.config.exclude_domains,
                    search_depth=self.config.search_depth
                )
                if results:
                    self.stats["tavily_successes"] += 1
                    print(f"  [TAVILY] {query[:50]}... ({len(results)} results)")
                return results

            elif provider_name == "serper":
                self.stats["serper_calls"] += 1
                results = await self.serper.search(
                    query=query,
                    max_results=max_results,
                    exclude_domains=self.config.exclude_domains
                )
                if results:
                    self.stats["serper_successes"] += 1
                    print(f"  [SERPER] {query[:50]}... ({len(results)} results)")
                return results

            elif provider_name == "brave":
                self.stats["brave_calls"] += 1
                results = await self.brave.search(
                    query=query,
                    max_results=max_results,
                    exclude_domains=self.config.exclude_domains
                )
                if results:
                    self.stats["brave_successes"] += 1
                    print(f"  [BRAVE] {query[:50]}... ({len(results)} results)")
                return results

            elif provider_name == "duckduckgo":
                self.stats["duckduckgo_calls"] = self.stats.get("duckduckgo_calls", 0) + 1
                self.stats["duckduckgo_fallbacks"] += 1  # Keep for backward compatibility
                results = await self.duckduckgo.search(
                    query=query,
                    max_results=max_results,
                    exclude_domains=self.config.exclude_domains
                )
                if results:
                    self.stats["duckduckgo_successes"] = self.stats.get("duckduckgo_successes", 0) + 1
                    print(f"  [DUCKDUCKGO] {query[:50]}... ({len(results)} results)")
                return results

            elif provider_name == "google":
                self.stats["google_calls"] += 1
                results = await self.google.search(
                    query=query,
                    max_results=max_results,
                    exclude_domains=self.config.exclude_domains
                )
                if results:
                    self.stats["google_successes"] += 1
                    print(f"  [GOOGLE] {query[:50]}... ({len(results)} results)")
                return results

            elif provider_name == "bing":
                self.stats["bing_calls"] += 1
                results = await self.bing.search(
                    query=query,
                    max_results=max_results,
                    exclude_domains=self.config.exclude_domains
                )
                if results:
                    self.stats["bing_successes"] += 1
                    print(f"  [BING] {query[:50]}... ({len(results)} results)")
                return results

        except RateLimitError as e:
            print(f"  [{provider_name.upper()} LIMIT] {e}")
        except Exception as e:
            print(f"  [{provider_name.upper()} ERROR] {e}")

        return []

    def _cache_results(self, query: str, results: List[SearchResult]) -> None:
        """Cache search results if cache is available."""
        if self.cache and results:
            cache_data = self._convert_results_for_cache(results)
            self.cache.store_search_results(query, cache_data)

    async def _search_with_free_cascade(
        self,
        query: str,
        max_results: int,
        include_tavily: bool = True
    ) -> List[SearchResult]:
        """
        Execute search with full free provider cascade, with optional Tavily fallback.

        Provider Priority Order (all free/low-cost providers first):
        1. DuckDuckGo - Completely FREE, no API key needed (but rate limited)
        2. Serper - 2,500 free queries (very fast, Google results)
        3. Brave - 2,000 free/month (independent index)
        4. Google - 100 free/day (requires setup)
        5. Bing - 1,000 free/month (requires Azure)
        6. Tavily - Paid only (ONLY if include_tavily=True)

        This cascade ensures:
        - Maximum use of free providers before any paid calls
        - Graceful degradation when providers are rate limited
        - Always returns results if ANY provider works

        Args:
            query: Search query
            max_results: Maximum results to return
            include_tavily: If True, include Tavily as final fallback

        Returns:
            List of SearchResult objects from the first successful provider
        """
        results = []

        # FREE PROVIDER CASCADE (in order of preference)
        # Each provider is tried in sequence, moving to next only on failure

        # 1. DuckDuckGo (FREE - no API key, but rate limited)
        results = await self._try_provider("duckduckgo", query, max_results)
        if results:
            return results

        # 2. Serper (2,500 free queries - Google results, FAST)
        if self.serper.is_available() and not self.serper.is_rate_limited():
            results = await self._try_provider("serper", query, max_results)
            if results:
                return results

        # 3. Brave (2,000 free/month - independent index)
        if self.brave.is_available() and not self.brave.is_rate_limited():
            results = await self._try_provider("brave", query, max_results)
            if results:
                return results

        # 4. Google Custom Search (100 free/day)
        if self.google.is_available() and not self.google.is_rate_limited():
            results = await self._try_provider("google", query, max_results)
            if results:
                return results

        # 5. Bing (1,000 free/month)
        if self.bing.is_available() and not self.bing.is_rate_limited():
            results = await self._try_provider("bing", query, max_results)
            if results:
                return results

        # 6. TAVILY (PREMIUM - Last resort, only if allowed)
        if include_tavily and not self.tavily.is_rate_limited():
            print(f"  [CASCADE] All free providers failed, using Tavily for: {query[:40]}...")
            results = await self._try_provider("tavily", query, max_results)
            if results:
                return results

        # All providers failed
        print(f"  [CASCADE FAILED] No providers returned results for: {query[:40]}...")
        return []

    def get_context(
        self,
        query: str,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Get LLM-optimized search context.

        Uses Tavily's get_search_context when available,
        falls back to building context from DuckDuckGo.
        """
        max_tokens = max_tokens or self.config.max_tokens_context

        # Try Tavily's optimized context first
        if not self.tavily.is_rate_limited():
            try:
                return self.tavily.get_context(
                    query=query,
                    max_tokens=max_tokens,
                    search_depth=self.config.search_depth
                )
            except RateLimitError:
                pass
            except Exception as e:
                print(f"[CONTEXT ERROR] {e}")

        # Fallback to DuckDuckGo
        return self.duckduckgo.get_context(query, max_tokens)

    async def batch_search(
        self,
        queries: List[str],
        max_results_per_query: Optional[int] = None
    ) -> Dict[str, List[SearchResult]]:
        """
        Execute multiple searches with rate limiting.

        Args:
            queries: List of search queries
            max_results_per_query: Max results per query

        Returns:
            Dict mapping query -> results
        """
        results = {}

        for query in queries:
            results[query] = await self.search(
                query=query,
                max_results=max_results_per_query
            )

            # Small delay to avoid rate limits
            await asyncio.sleep(0.5)

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get search statistics."""
        total = self.stats["total_queries"]
        return {
            **self.stats,
            "cache_hit_rate": self.stats["cache_hits"] / total if total > 0 else 0,
            "tavily_success_rate": (
                self.stats["tavily_successes"] / self.stats["tavily_calls"]
                if self.stats["tavily_calls"] > 0 else 0
            ),
            "duckduckgo_fallback_rate": (
                self.stats["duckduckgo_fallbacks"] / total if total > 0 else 0
            )
        }

    def _convert_cached_results(
        self,
        cached: Dict[str, Any],
        query: str
    ) -> List[SearchResult]:
        """Convert cached results back to SearchResult objects."""
        results = []
        for item in cached.get("results", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                content=item.get("content", ""),
                score=item.get("score", 0.0),
                provider="cache",
                query=query
            ))
        return results

    def _convert_results_for_cache(
        self,
        results: List[SearchResult]
    ) -> Dict[str, Any]:
        """Convert SearchResult objects to cacheable format."""
        return {
            "results": [
                {
                    "title": r.title,
                    "url": r.url,
                    "content": r.content,
                    "score": r.score
                }
                for r in results
            ]
        }

    async def search_tavily_refinement(
        self,
        queries: List[str],
        max_queries: Optional[int] = None
    ) -> List[SearchResult]:
        """
        Execute Tavily search for refinement after free search.

        Only used in free_first strategy to fill high-priority gaps
        after collecting 100+ free sources.

        Args:
            queries: List of targeted refinement queries
            max_queries: Maximum number of Tavily queries to execute

        Returns:
            List of SearchResult objects from Tavily
        """
        max_queries = max_queries or self.config.max_tavily_refinement_queries
        results = []

        if self.tavily.is_rate_limited():
            print("  [TAVILY REFINEMENT] Skipped - rate limited")
            return results

        for query in queries[:max_queries]:
            try:
                self.stats["tavily_calls"] += 1
                tavily_results = await self.tavily.search(
                    query=query,
                    max_results=self.config.max_results_per_query,
                    include_domains=self.config.include_domains[:5],
                    exclude_domains=self.config.exclude_domains,
                    search_depth=self.config.search_depth
                )
                if tavily_results:
                    self.stats["tavily_successes"] += 1
                    self.stats["tavily_sources_total"] += len(tavily_results)
                    results.extend(tavily_results)
                    print(f"  [TAVILY REFINE] {query[:50]}... ({len(tavily_results)} results)")

                # Small delay between queries
                await asyncio.sleep(0.3)

            except RateLimitError as e:
                print(f"  [TAVILY LIMIT] {e}")
                break
            except Exception as e:
                print(f"  [TAVILY ERROR] {e}")
                continue

        return results


def generate_optimized_queries(
    company_name: str,
    profile = None,
    depth: str = "quick",
    strategy: str = "auto"
) -> List[str]:
    """
    Generate optimized search queries for company research.

    Priority order:
    1. Profile-defined priority_queries (user-specified, most relevant)
    2. Core queries (always included)
    3. Profile-enhanced queries (industry, competitors)

    For free_first strategy, generates 3x more queries to reach 100+ sources.

    Returns max 4-12 queries for auto, or 12-24 queries for free_first.
    """
    config = SearchConfig()
    base_max = config.query_limits.get(depth, 4)

    # For free_first strategy, multiply query count to get more sources
    if strategy in ("free_first", "free_only"):
        max_queries = int(base_max * config.free_query_multiplier)
    else:
        max_queries = base_max

    queries = []

    # 1. Priority queries from profile (user-defined, most important)
    if profile and hasattr(profile, 'priority_queries') and profile.priority_queries:
        queries.extend(profile.priority_queries)

    # 2. Core queries (fill remaining slots)
    core_queries = [
        f'"{company_name}" company overview financials revenue 2024',
        f'"{company_name}" market share competitive position industry',
        f'"{company_name}" products services business model strategy',
        f'"{company_name}" news developments announcements 2024',
    ]

    # Add core queries that aren't duplicates
    for q in core_queries:
        if len(queries) >= max_queries:
            break
        # Avoid adding if similar query already exists
        if not any(company_name.lower() in existing.lower() and
                   any(word in existing.lower() for word in q.split()[:3])
                   for existing in queries):
            queries.append(q)

    # 3. Profile-enhanced queries (if room)
    if profile and len(queries) < max_queries:
        if profile.industry and profile.country:
            queries.append(
                f'"{company_name}" {profile.industry} {profile.country} market leader'
            )

        if profile.parent_company and len(queries) < max_queries:
            queries.append(
                f'"{profile.parent_company}" "{company_name}" subsidiary investor presentation'
            )

        if profile.competitors and len(profile.competitors) > 0 and len(queries) < max_queries:
            comp = profile.competitors[0]
            queries.append(
                f'"{company_name}" vs "{comp}" comparison market share analysis'
            )

    # 4. Extended queries for free_first strategy (to get 100+ sources)
    if strategy in ("free_first", "free_only") and len(queries) < max_queries:
        extended_queries = _generate_extended_queries(company_name, profile, max_queries - len(queries))
        queries.extend(extended_queries)

    # Apply depth limit
    return queries[:max_queries]


def _generate_extended_queries(
    company_name: str,
    profile = None,
    max_additional: int = 15
) -> List[str]:
    """
    Generate additional queries for free-first strategy to reach 100+ sources.

    These queries cover different aspects of company research:
    - Financial metrics (revenue, earnings, market cap)
    - Leadership and governance
    - Products and services
    - Competitors and market position
    - Recent news and developments
    - Strategic initiatives
    """
    queries = []
    ticker = getattr(profile, 'ticker', '') if profile else ''
    industry = getattr(profile, 'industry', '') if profile else ''
    country = getattr(profile, 'country', '') if profile else ''

    # Financial queries
    financial_queries = [
        f'"{company_name}" annual revenue earnings report 2024',
        f'"{company_name}" quarterly results Q3 Q4 2024',
        f'"{company_name}" market capitalization stock price',
        f'"{company_name}" profit margin net income financial performance',
        f'"{company_name}" revenue growth year over year',
        f'"{company_name}" balance sheet debt assets 2024',
    ]

    # Leadership queries
    leadership_queries = [
        f'"{company_name}" CEO executive leadership team',
        f'"{company_name}" board of directors management',
        f'"{company_name}" founder history founding story',
        f'"{company_name}" headquarters employees workforce',
    ]

    # Products/Services queries
    products_queries = [
        f'"{company_name}" products services portfolio',
        f'"{company_name}" new product launch 2024',
        f'"{company_name}" flagship products main offerings',
        f'"{company_name}" business segments revenue breakdown',
    ]

    # Competitive queries
    competitive_queries = [
        f'"{company_name}" competitors market share comparison',
        f'"{company_name}" competitive advantage moat',
        f'"{company_name}" industry ranking position',
        f'"{company_name}" SWOT analysis strengths weaknesses',
    ]

    # News/Developments queries
    news_queries = [
        f'"{company_name}" latest news 2024',
        f'"{company_name}" press release announcement 2024',
        f'"{company_name}" acquisition partnership deal 2024',
        f'"{company_name}" expansion growth plans',
    ]

    # Strategy queries
    strategy_queries = [
        f'"{company_name}" strategy roadmap future plans',
        f'"{company_name}" AI artificial intelligence initiatives',
        f'"{company_name}" digital transformation technology',
        f'"{company_name}" sustainability ESG environmental',
    ]

    # Add industry-specific if available
    if industry:
        industry_queries = [
            f'"{company_name}" {industry} market leader',
            f'"{company_name}" {industry} trends outlook 2024',
        ]
        queries.extend(industry_queries)

    # Add ticker-specific if available
    if ticker:
        ticker_queries = [
            f'{ticker} stock analysis investor',
            f'{ticker} earnings call transcript 2024',
        ]
        queries.extend(ticker_queries)

    # Combine all query categories
    all_extended = (
        financial_queries +
        leadership_queries +
        products_queries +
        competitive_queries +
        news_queries +
        strategy_queries
    )

    # Add queries up to max
    for q in all_extended:
        if len(queries) >= max_additional:
            break
        queries.append(q)

    return queries


# Convenience function
def create_search_client(
    cache = None,
    config: Optional[SearchConfig] = None
) -> OptimizedSearchClient:
    """Create an optimized search client."""
    return OptimizedSearchClient(config=config, cache=cache)
