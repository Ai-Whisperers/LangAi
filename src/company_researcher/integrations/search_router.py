"""
Smart Search Router - Multi-Provider Search with Cost Optimization.

Routes search queries to the optimal provider based on COST-FIRST strategy,
with automatic fallback to paid providers only when free ones fail.

Strategy (COST-FIRST):
- Always try FREE providers first (DuckDuckGo)
- Only use paid providers if free ones fail or return insufficient results
- Persistent disk cache to avoid re-fetching data

Tier System:
- FREE tier: DuckDuckGo only (unlimited)
- STANDARD tier: DuckDuckGo → Serper (only if DDG fails)
- PREMIUM tier: DuckDuckGo → Brave → Serper → Tavily (escalate only on failure)

Features:
- COST-FIRST routing (free before paid)
- Automatic fallback on errors/rate limits
- PERSISTENT DISK CACHE (saves money on repeat queries)
- Cost tracking per provider
- Result normalization
- Minimum results threshold before escalation

Usage:
    from company_researcher.integrations.search_router import get_search_router

    router = get_search_router()

    # Auto-route based on cost tier
    results = router.search("Tesla earnings Q4", quality="standard")

    # Force specific provider
    results = router.search("Apple stock", provider="tavily")

    # Get cost breakdown
    stats = router.get_stats()
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List, Literal
from dataclasses import dataclass, field
from threading import Lock
from datetime import datetime, timedelta
from ..utils import get_config, get_logger, utc_now

logger = get_logger(__name__)


# Quality tiers - now represent COST tiers
QualityTier = Literal["free", "standard", "premium"]


@dataclass
class SearchResult:
    """Normalized search result."""
    title: str
    url: str
    snippet: str
    source: str  # Provider name
    score: float = 0.0
    published_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "score": self.score,
            "published_date": self.published_date
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResult":
        return cls(
            title=data.get("title", ""),
            url=data.get("url", ""),
            snippet=data.get("snippet", ""),
            source=data.get("source", ""),
            score=data.get("score", 0.0),
            published_date=data.get("published_date")
        )


@dataclass
class SearchResponse:
    """Response from search operation."""
    query: str
    results: List[SearchResult] = field(default_factory=list)
    provider: str = ""
    quality_tier: str = ""
    cost: float = 0.0
    cached: bool = False
    success: bool = True
    error: Optional[str] = None
    cache_timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "results": [r.to_dict() for r in self.results],
            "provider": self.provider,
            "quality_tier": self.quality_tier,
            "cost": self.cost,
            "cached": self.cached,
            "success": self.success,
            "error": self.error,
            "cache_timestamp": self.cache_timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResponse":
        results = [SearchResult.from_dict(r) for r in data.get("results", [])]
        return cls(
            query=data.get("query", ""),
            results=results,
            provider=data.get("provider", ""),
            quality_tier=data.get("quality_tier", ""),
            cost=data.get("cost", 0.0),
            cached=data.get("cached", False),
            success=data.get("success", True),
            error=data.get("error"),
            cache_timestamp=data.get("cache_timestamp")
        )


class PersistentCache:
    """
    Persistent disk-based cache for search results.

    Saves API responses to disk so we never have to re-fetch the same data.
    """

    def __init__(self, cache_dir: str = ".cache/search", ttl_days: int = 30):
        """
        Initialize persistent cache.

        Args:
            cache_dir: Directory to store cache files
            ttl_days: Time-to-live in days (default 30 days)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_days = ttl_days
        self._lock = Lock()

    def _get_cache_key(self, query: str, max_results: int) -> str:
        """Generate a unique cache key for a query."""
        raw = f"{query.lower().strip()}:{max_results}"
        return hashlib.md5(raw.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / f"{cache_key}.json"

    def get(self, query: str, max_results: int) -> Optional[SearchResponse]:
        """
        Get cached response if available and not expired.

        Args:
            query: Search query
            max_results: Max results requested

        Returns:
            Cached SearchResponse or None
        """
        cache_key = self._get_cache_key(query, max_results)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        try:
            with self._lock:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

            # Check expiry
            timestamp = data.get("cache_timestamp")
            if timestamp:
                cache_time = datetime.fromisoformat(timestamp)
                if utc_now() - cache_time > timedelta(days=self.ttl_days):
                    # Expired - delete and return None
                    cache_path.unlink(missing_ok=True)
                    return None

            response = SearchResponse.from_dict(data)
            response.cached = True
            logger.info(f"[CACHE HIT] Query: '{query[:40]}...' (saved ${data.get('cost', 0):.4f})")
            return response

        except Exception as e:
            logger.warning(f"Cache read error: {e}")
            return None

    def set(self, query: str, max_results: int, response: SearchResponse) -> None:
        """
        Save response to cache.

        Args:
            query: Search query
            max_results: Max results requested
            response: SearchResponse to cache
        """
        if not response.success:
            return  # Don't cache failures

        cache_key = self._get_cache_key(query, max_results)
        cache_path = self._get_cache_path(cache_key)

        try:
            data = response.to_dict()
            data["cache_timestamp"] = utc_now().isoformat()

            with self._lock:
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"[CACHE SAVE] Query: '{query[:40]}...'")

        except Exception as e:
            logger.warning(f"Cache write error: {e}")

    def clear(self) -> int:
        """Clear all cache files. Returns count of files deleted."""
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except Exception as e:
                logger.debug(f"Failed to delete cache file {cache_file}: {e}")
        return count

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files if f.exists())

        return {
            "cache_entries": len(cache_files),
            "cache_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_dir": str(self.cache_dir),
            "ttl_days": self.ttl_days
        }


class SearchRouter:
    """
    Smart search router with multi-provider support.

    Routes queries using COST-FIRST strategy:
    - Always try FREE providers first
    - Only escalate to paid if free fails or returns insufficient results
    """

    # Provider costs per query (sorted cheapest to most expensive)
    PROVIDER_COSTS = {
        "duckduckgo": 0.0,      # FREE (unlimited)
        "brave": 0.0,          # FREE (2000/month free tier)
        "serper": 0.001,       # $0.001/query ($50/50K)
        "tavily": 0.005,       # $0.005/query (best quality)
    }

    # Provider quality scores (for reference)
    PROVIDER_QUALITY = {
        "tavily": 0.95,     # Best for research
        "serper": 0.90,     # Google results
        "brave": 0.85,      # Good with AI summaries
        "duckduckgo": 0.75, # Good for most queries
    }

    # COST-FIRST tier ordering (cheapest first, paid only as fallback)
    TIER_PROVIDERS = {
        # FREE tier: Only free providers
        "free": ["duckduckgo"],

        # STANDARD tier: Free first, then cheap paid as fallback
        "standard": ["duckduckgo", "brave", "serper"],

        # PREMIUM tier: Free first, then escalate through all paid options
        "premium": ["duckduckgo", "brave", "serper", "tavily"],
    }

    # Minimum results to consider search successful (before trying next provider)
    MIN_RESULTS_THRESHOLD = 3

    def __init__(
        self,
        tavily_api_key: Optional[str] = None,
        serper_api_key: Optional[str] = None,
        brave_api_key: Optional[str] = None,
        default_tier: QualityTier = "standard",
        cache_dir: str = ".cache/search",
        cache_ttl_days: int = 30
    ):
        """
        Initialize search router.

        Args:
            tavily_api_key: Tavily API key (optional)
            serper_api_key: Serper.dev API key (optional)
            brave_api_key: Brave Search API key (optional)
            default_tier: Default quality tier
            cache_dir: Directory for persistent cache
            cache_ttl_days: Cache TTL in days
        """
        self.tavily_api_key = tavily_api_key or get_config("TAVILY_API_KEY")
        self.serper_api_key = serper_api_key or get_config("SERPER_API_KEY")
        self.brave_api_key = brave_api_key or get_config("BRAVE_API_KEY")
        self.default_tier = default_tier

        # Track usage and costs
        self._usage: Dict[str, int] = {
            "duckduckgo": 0,
            "brave": 0,
            "serper": 0,
            "tavily": 0
        }
        self._costs: Dict[str, float] = {
            "duckduckgo": 0.0,
            "brave": 0.0,
            "serper": 0.0,
            "tavily": 0.0
        }
        self._errors: Dict[str, int] = {}
        self._cache_hits: int = 0
        self._lock = Lock()

        # Persistent disk cache
        self._persistent_cache = PersistentCache(cache_dir, cache_ttl_days)

        # In-memory cache for session (faster lookups)
        self._memory_cache: Dict[str, SearchResponse] = {}

    def _get_available_providers(self) -> List[str]:
        """Get list of available providers based on API keys."""
        available = ["duckduckgo"]  # Always available (no API key needed)

        # Brave - check for API key (has free tier)
        if self.brave_api_key:
            available.append("brave")

        # Serper - requires API key
        if self.serper_api_key:
            available.append("serper")

        # Tavily - requires API key
        if self.tavily_api_key:
            available.append("tavily")

        return available

    def search(
        self,
        query: str,
        quality: Optional[QualityTier] = None,
        provider: Optional[str] = None,
        max_results: int = 10,
        use_cache: bool = True,
        min_results: Optional[int] = None
    ) -> SearchResponse:
        """
        Search using COST-FIRST provider selection.

        Strategy:
        1. Check persistent cache first (saves money!)
        2. Try FREE providers first (DuckDuckGo)
        3. Only escalate to paid if free fails or returns < min_results

        Args:
            query: Search query
            quality: Quality tier (free, standard, premium)
            provider: Force specific provider (bypasses cost-first logic)
            max_results: Maximum results
            use_cache: Use cached results if available
            min_results: Minimum results before escalating (default: MIN_RESULTS_THRESHOLD)

        Returns:
            SearchResponse with results
        """
        quality = quality or self.default_tier
        min_results = min_results if min_results is not None else self.MIN_RESULTS_THRESHOLD

        # 1. Check persistent disk cache first (FREE!)
        if use_cache:
            cached = self._persistent_cache.get(query, max_results)
            if cached and len(cached.results) >= min_results:
                with self._lock:
                    self._cache_hits += 1
                return cached

        # 2. Determine provider order (COST-FIRST)
        if provider:
            providers = [provider]
        else:
            providers = self._get_provider_order(quality)

        logger.info(f"[SEARCH] Query: '{query[:50]}...' | Tier: {quality} | Providers: {providers}")

        # 3. Try providers in COST-FIRST order
        last_error = None
        best_result = None

        for prov in providers:
            try:
                result = self._search_provider(prov, query, max_results)

                if result.success and result.results:
                    result.quality_tier = quality

                    # If we got enough results, stop here (save money!)
                    if len(result.results) >= min_results:
                        logger.info(f"[OK] {prov}: {len(result.results)} results (sufficient, not escalating)")

                        # Save to persistent cache
                        if use_cache:
                            self._persistent_cache.set(query, max_results, result)

                        return result

                    # Got some results but not enough - save as best so far
                    if best_result is None or len(result.results) > len(best_result.results):
                        best_result = result
                        logger.info(f"[PARTIAL] {prov}: {len(result.results)} results (below threshold, trying next)")
                else:
                    last_error = result.error
                    logger.warning(f"[FAIL] {prov}: {result.error}")

            except Exception as e:
                last_error = str(e)
                logger.warning(f"[ERROR] {prov}: {e}")
                with self._lock:
                    self._errors[prov] = self._errors.get(prov, 0) + 1

        # 4. Return best result we got (even if below threshold)
        if best_result:
            logger.info(f"[DONE] Returning best result: {len(best_result.results)} from {best_result.provider}")
            if use_cache:
                self._persistent_cache.set(query, max_results, best_result)
            return best_result

        # 5. All providers failed
        return SearchResponse(
            query=query,
            provider="none",
            quality_tier=quality,
            success=False,
            error=f"All providers failed. Last error: {last_error}"
        )

    def _get_provider_order(self, quality: QualityTier) -> List[str]:
        """Get provider order based on quality tier and availability (COST-FIRST)."""
        tier_providers = self.TIER_PROVIDERS.get(quality, ["duckduckgo"])
        available = self._get_available_providers()

        # Filter to available providers, maintaining COST-FIRST order
        return [p for p in tier_providers if p in available]

    def _search_provider(
        self,
        provider: str,
        query: str,
        max_results: int
    ) -> SearchResponse:
        """Execute search on specific provider."""
        if provider == "duckduckgo":
            return self._search_duckduckgo(query, max_results)
        elif provider == "brave":
            return self._search_brave(query, max_results)
        elif provider == "serper":
            return self._search_serper(query, max_results)
        elif provider == "tavily":
            return self._search_tavily(query, max_results)
        else:
            return SearchResponse(
                query=query,
                provider=provider,
                success=False,
                error=f"Unknown provider: {provider}"
            )

    def _search_duckduckgo(self, query: str, max_results: int) -> SearchResponse:
        """Search using DuckDuckGo (FREE - unlimited)."""
        try:
            from duckduckgo_search import DDGS

            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append(SearchResult(
                        title=r.get("title", ""),
                        url=r.get("href", ""),
                        snippet=r.get("body", ""),
                        source="duckduckgo"
                    ))

            cost = self.PROVIDER_COSTS["duckduckgo"]
            with self._lock:
                self._usage["duckduckgo"] += 1
                self._costs["duckduckgo"] += cost

            return SearchResponse(
                query=query,
                results=results,
                provider="duckduckgo",
                cost=cost,
                success=True
            )

        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return SearchResponse(
                query=query,
                provider="duckduckgo",
                success=False,
                error=str(e)
            )

    def _search_brave(self, query: str, max_results: int) -> SearchResponse:
        """Search using Brave Search API (FREE tier: 2000/month)."""
        if not self.brave_api_key:
            return SearchResponse(
                query=query,
                provider="brave",
                success=False,
                error="Brave API key not configured"
            )

        try:
            import requests

            response = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={
                    "X-Subscription-Token": self.brave_api_key,
                    "Accept": "application/json"
                },
                params={
                    "q": query,
                    "count": max_results,
                    "safesearch": "moderate"
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for r in data.get("web", {}).get("results", [])[:max_results]:
                results.append(SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("description", ""),
                    source="brave",
                    score=r.get("relevance_score", 0.0)
                ))

            cost = self.PROVIDER_COSTS["brave"]
            with self._lock:
                self._usage["brave"] += 1
                self._costs["brave"] += cost

            return SearchResponse(
                query=query,
                results=results,
                provider="brave",
                cost=cost,
                success=True
            )

        except Exception as e:
            logger.error(f"Brave search error: {e}")
            return SearchResponse(
                query=query,
                provider="brave",
                success=False,
                error=str(e)
            )

    def _search_serper(self, query: str, max_results: int) -> SearchResponse:
        """Search using Serper.dev (Google results, $0.001/query)."""
        if not self.serper_api_key:
            return SearchResponse(
                query=query,
                provider="serper",
                success=False,
                error="Serper API key not configured"
            )

        try:
            import requests

            response = requests.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": self.serper_api_key},
                json={"q": query, "num": max_results},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for r in data.get("organic", [])[:max_results]:
                results.append(SearchResult(
                    title=r.get("title", ""),
                    url=r.get("link", ""),
                    snippet=r.get("snippet", ""),
                    source="serper",
                    score=r.get("position", 0)
                ))

            cost = self.PROVIDER_COSTS["serper"]
            with self._lock:
                self._usage["serper"] += 1
                self._costs["serper"] += cost

            return SearchResponse(
                query=query,
                results=results,
                provider="serper",
                cost=cost,
                success=True
            )

        except Exception as e:
            logger.error(f"Serper search error: {e}")
            return SearchResponse(
                query=query,
                provider="serper",
                success=False,
                error=str(e)
            )

    def _search_tavily(self, query: str, max_results: int) -> SearchResponse:
        """Search using Tavily (premium, best quality, $0.005/query)."""
        if not self.tavily_api_key:
            return SearchResponse(
                query=query,
                provider="tavily",
                success=False,
                error="Tavily API key not configured"
            )

        try:
            from tavily import TavilyClient

            client = TavilyClient(api_key=self.tavily_api_key)
            response = client.search(query, max_results=max_results)

            results = []
            for r in response.get("results", []):
                results.append(SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("content", ""),
                    source="tavily",
                    score=r.get("score", 0.0),
                    published_date=r.get("published_date")
                ))

            cost = self.PROVIDER_COSTS["tavily"]
            with self._lock:
                self._usage["tavily"] += 1
                self._costs["tavily"] += cost

            return SearchResponse(
                query=query,
                results=results,
                provider="tavily",
                cost=cost,
                success=True
            )

        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return SearchResponse(
                query=query,
                provider="tavily",
                success=False,
                error=str(e)
            )

    def search_news(
        self,
        query: str,
        quality: Optional[QualityTier] = None,
        max_results: int = 10
    ) -> SearchResponse:
        """Search for news articles."""
        news_query = f"{query} news latest"
        return self.search(news_query, quality=quality, max_results=max_results)

    def search_company(
        self,
        company_name: str,
        search_type: str = "general",
        quality: Optional[QualityTier] = None,
        max_results: int = 10
    ) -> SearchResponse:
        """Search for company information."""
        query_templates = {
            "general": f'"{company_name}" company overview',
            "financials": f'"{company_name}" financials revenue earnings',
            "news": f'"{company_name}" news latest',
            "competitors": f'"{company_name}" competitors market share',
            "products": f'"{company_name}" products services offerings',
            "leadership": f'"{company_name}" CEO executives leadership',
        }

        query = query_templates.get(search_type, f'"{company_name}"')
        return self.search(query, quality=quality, max_results=max_results)

    def get_stats(self) -> Dict[str, Any]:
        """Get usage, cost, and cache statistics."""
        with self._lock:
            total_queries = sum(self._usage.values())
            total_cost = sum(self._costs.values())

            # Calculate money saved from cache
            estimated_cache_savings = self._cache_hits * 0.003  # Avg cost per query

            return {
                "total_queries": total_queries,
                "total_cost": round(total_cost, 4),
                "cache_hits": self._cache_hits,
                "estimated_cache_savings": round(estimated_cache_savings, 4),
                "by_provider": {
                    provider: {
                        "queries": self._usage[provider],
                        "cost": round(self._costs[provider], 4),
                        "errors": self._errors.get(provider, 0)
                    }
                    for provider in self._usage.keys()
                },
                "available_providers": self._get_available_providers(),
                "default_tier": self.default_tier,
                "persistent_cache": self._persistent_cache.get_stats()
            }

    def reset_stats(self) -> None:
        """Reset usage statistics (does not clear cache)."""
        with self._lock:
            for key in self._usage:
                self._usage[key] = 0
                self._costs[key] = 0.0
            self._errors.clear()
            self._cache_hits = 0

    def clear_cache(self) -> Dict[str, int]:
        """Clear all caches (memory and disk)."""
        self._memory_cache.clear()
        disk_cleared = self._persistent_cache.clear()
        return {
            "memory_cleared": True,
            "disk_entries_cleared": disk_cleared
        }

    def set_default_tier(self, tier: QualityTier) -> None:
        """Set default quality tier."""
        self.default_tier = tier


# Singleton instance
_search_router: Optional[SearchRouter] = None
_router_lock = Lock()


def get_search_router(
    tavily_api_key: Optional[str] = None,
    serper_api_key: Optional[str] = None,
    brave_api_key: Optional[str] = None
) -> SearchRouter:
    """Get singleton search router instance."""
    global _search_router
    if _search_router is None:
        with _router_lock:
            if _search_router is None:
                _search_router = SearchRouter(
                    tavily_api_key=tavily_api_key,
                    serper_api_key=serper_api_key,
                    brave_api_key=brave_api_key
                )
    return _search_router


def reset_search_router() -> None:
    """Reset search router instance."""
    global _search_router
    _search_router = None


# Convenience functions
def smart_search(
    query: str,
    quality: QualityTier = "standard",
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """Quick function to perform smart search."""
    router = get_search_router()
    result = router.search(query, quality=quality, max_results=max_results)
    return [r.to_dict() for r in result.results] if result.success else []


def free_search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Quick function for free search (DuckDuckGo only)."""
    router = get_search_router()
    result = router.search(query, quality="free", max_results=max_results)
    return [r.to_dict() for r in result.results] if result.success else []


def cached_search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Quick function that prioritizes cached results."""
    router = get_search_router()
    result = router.search(query, quality="standard", max_results=max_results, use_cache=True)
    return [r.to_dict() for r in result.results] if result.success else []
