"""
News Router - Smart routing between free and paid news providers.

This module contains the NewsRouter class which handles:
- Automatic provider selection and fallback
- Quota tracking
- Caching
- Cost tracking integration
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock
from typing import Optional

from .models import (
    NewsProvider,
    NewsQuality,
    NewsArticle,
    NewsSearchResult,
    ProviderQuota,
)

logger = logging.getLogger(__name__)


class NewsRouter:
    """
    Smart router for news providers.

    Routes requests using COST-FIRST strategy:
    - Always try FREE providers first (Google RSS)
    - Only escalate to paid providers if free fails or returns insufficient results
    - Persistent disk cache to avoid re-fetching data
    """

    # Provider priority (COST-FIRST: cheapest first)
    PROVIDER_PRIORITY = [
        NewsProvider.GOOGLE_RSS,  # FREE - unlimited
        NewsProvider.GNEWS,       # FREE tier: 100/day
        NewsProvider.NEWSAPI,     # FREE tier: 100/day (dev only)
        NewsProvider.MEDIASTACK,  # FREE tier: 500/month
    ]

    # Provider costs per query
    PROVIDER_COSTS = {
        NewsProvider.GOOGLE_RSS: 0.0,     # FREE
        NewsProvider.GNEWS: 0.003,        # ~$0.003/query after free tier
        NewsProvider.NEWSAPI: 0.003,      # ~$0.003/query after free tier
        NewsProvider.MEDIASTACK: 0.002,   # ~$0.002/query after free tier
    }

    # Minimum results before escalating to next provider
    MIN_RESULTS_THRESHOLD = 2

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        cache_ttl_days: int = 7,  # Changed to days (news is more time-sensitive than search)
        default_quality: NewsQuality = NewsQuality.STANDARD
    ):
        """
        Initialize news router.

        Args:
            cache_dir: Directory for caching news results
            cache_ttl_days: Cache time-to-live in days (news is time-sensitive)
            default_quality: Default quality tier
        """
        self.cache_dir = cache_dir or Path(".cache/news")
        self.cache_ttl = timedelta(days=cache_ttl_days)
        self.default_quality = default_quality

        self._lock = Lock()
        self._providers_initialized = False
        self._google_rss = None
        self._gnews = None
        self._newsapi = None
        self._mediastack = None

        # Quota tracking
        self._quotas: dict[NewsProvider, ProviderQuota] = {
            NewsProvider.GOOGLE_RSS: ProviderQuota(
                provider=NewsProvider.GOOGLE_RSS,
                daily_limit=0,  # Unlimited
                monthly_limit=0
            ),
            NewsProvider.GNEWS: ProviderQuota(
                provider=NewsProvider.GNEWS,
                daily_limit=100,
                monthly_limit=0
            ),
            NewsProvider.NEWSAPI: ProviderQuota(
                provider=NewsProvider.NEWSAPI,
                daily_limit=100,
                monthly_limit=0
            ),
            NewsProvider.MEDIASTACK: ProviderQuota(
                provider=NewsProvider.MEDIASTACK,
                daily_limit=0,
                monthly_limit=500
            ),
        }

        # Initialize cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"NewsRouter initialized with cache_ttl={cache_ttl_days} days")

    def _init_providers(self):
        """Lazy initialize providers."""
        if self._providers_initialized:
            return

        try:
            from ..google_news_rss import get_google_news
            self._google_rss = get_google_news()
        except Exception as e:
            logger.warning(f"Google News RSS not available: {e}")

        try:
            from ..gnews import GNewsClient
            self._gnews = GNewsClient()
        except Exception as e:
            logger.warning(f"GNews not available: {e}")

        try:
            from ..news_api import NewsAPIClient
            self._newsapi = NewsAPIClient()
        except Exception as e:
            logger.warning(f"NewsAPI not available: {e}")

        try:
            from ..mediastack import MediastackClient
            self._mediastack = MediastackClient()
        except Exception as e:
            logger.warning(f"Mediastack not available: {e}")

        self._providers_initialized = True

    def _get_cache_key(self, query: str, max_results: int) -> str:
        """Generate cache key for query."""
        key = f"{query}:{max_results}"
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cached(self, query: str, max_results: int) -> Optional[NewsSearchResult]:
        """Get cached result if exists and not expired."""
        cache_key = self._get_cache_key(query, max_results)
        cache_file = self.cache_dir / f"news_{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Check expiration
            timestamp = datetime.fromisoformat(data["timestamp"])
            if datetime.now() - timestamp > self.cache_ttl:
                cache_file.unlink()
                return None

            # Reconstruct articles
            articles = []
            for a in data["articles"]:
                articles.append(NewsArticle(
                    title=a["title"],
                    description=a.get("description"),
                    url=a["url"],
                    source=a["source"],
                    published_at=datetime.fromisoformat(a["published_at"]) if a.get("published_at") else None,
                    provider=NewsProvider(a["provider"]),
                    image_url=a.get("image_url"),
                    author=a.get("author"),
                    content=a.get("content"),
                    sentiment=a.get("sentiment")
                ))

            return NewsSearchResult(
                query=query,
                articles=articles,
                total_results=len(articles),
                provider=NewsProvider(data["provider"]),
                success=True,
                cached=True,
                cost=0.0
            )
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
            return None

    def _save_cache(self, query: str, max_results: int, result: NewsSearchResult) -> None:
        """Save result to cache."""
        if not result.success:
            return

        cache_key = self._get_cache_key(query, max_results)
        cache_file = self.cache_dir / f"news_{cache_key}.json"

        try:
            data = {
                "query": query,
                "provider": result.provider.value,
                "timestamp": datetime.now().isoformat(),
                "articles": [a.to_dict() for a in result.articles]
            }

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

    def _select_providers(self, quality: NewsQuality) -> list[NewsProvider]:
        """
        Select providers to try based on quality tier.

        COST-FIRST strategy: Always try free providers first, only escalate
        to paid providers if free ones fail or return insufficient results.

        Returns ordered list of providers to try (cheapest first).
        """
        if quality == NewsQuality.FREE:
            # FREE tier: Only free Google RSS
            return [NewsProvider.GOOGLE_RSS]
        elif quality == NewsQuality.STANDARD:
            # STANDARD tier: Free first, then limited paid options
            return [
                NewsProvider.GOOGLE_RSS,  # FREE - unlimited
                NewsProvider.GNEWS,       # FREE tier: 100/day
            ]
        else:  # PREMIUM - Cost-First: still try free first!
            # PREMIUM tier: All providers, but STILL free first
            return self.PROVIDER_PRIORITY.copy()

    async def _search_google_rss(
        self,
        query: str,
        max_results: int,
        language: str
    ) -> NewsSearchResult:
        """Search using Google News RSS."""
        if self._google_rss is None:
            return NewsSearchResult(
                query=query,
                articles=[],
                total_results=0,
                provider=NewsProvider.GOOGLE_RSS,
                success=False,
                error="Google News RSS not available"
            )

        try:
            result = await self._google_rss.search(query, language=language, max_results=max_results)

            articles = [
                NewsArticle(
                    title=a.title,
                    description=a.description,
                    url=a.url,
                    source=a.source,
                    published_at=a.published_at,
                    provider=NewsProvider.GOOGLE_RSS,
                    image_url=getattr(a, 'image_url', None)
                )
                for a in result.articles
            ]

            return NewsSearchResult(
                query=query,
                articles=articles,
                total_results=len(articles),
                provider=NewsProvider.GOOGLE_RSS,
                success=True,
                cost=0.0
            )
        except Exception as e:
            logger.warning(f"Google News RSS failed for '{query}': {e}")
            return NewsSearchResult(
                query=query,
                articles=[],
                total_results=0,
                provider=NewsProvider.GOOGLE_RSS,
                success=False,
                error=str(e)
            )

    async def _search_gnews(
        self,
        query: str,
        max_results: int,
        language: str
    ) -> NewsSearchResult:
        """Search using GNews."""
        if self._gnews is None:
            return NewsSearchResult(
                query=query,
                articles=[],
                total_results=0,
                provider=NewsProvider.GNEWS,
                success=False,
                error="GNews not available"
            )

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: self._gnews.search(query, max_results=max_results, language=language)
            )

            articles = [
                NewsArticle(
                    title=a.get("title", ""),
                    description=a.get("description"),
                    url=a.get("url", ""),
                    source=a.get("source", {}).get("name", "Unknown"),
                    published_at=datetime.fromisoformat(a["publishedAt"].replace("Z", "+00:00")) if a.get("publishedAt") else None,
                    provider=NewsProvider.GNEWS,
                    image_url=a.get("image")
                )
                for a in result.get("articles", [])
            ]

            return NewsSearchResult(
                query=query,
                articles=articles,
                total_results=len(articles),
                provider=NewsProvider.GNEWS,
                success=True,
                cost=0.003  # ~$0.003/request after free tier
            )
        except Exception as e:
            logger.warning(f"GNews failed for '{query}': {e}")
            return NewsSearchResult(
                query=query,
                articles=[],
                total_results=0,
                provider=NewsProvider.GNEWS,
                success=False,
                error=str(e)
            )

    async def _search_newsapi(
        self,
        query: str,
        max_results: int,
        language: str
    ) -> NewsSearchResult:
        """Search using NewsAPI."""
        if self._newsapi is None:
            return NewsSearchResult(
                query=query,
                articles=[],
                total_results=0,
                provider=NewsProvider.NEWSAPI,
                success=False,
                error="NewsAPI not available"
            )

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: self._newsapi.search(query, page_size=max_results, language=language)
            )

            articles = [
                NewsArticle(
                    title=a.get("title", ""),
                    description=a.get("description"),
                    url=a.get("url", ""),
                    source=a.get("source", {}).get("name", "Unknown"),
                    published_at=datetime.fromisoformat(a["publishedAt"].replace("Z", "+00:00")) if a.get("publishedAt") else None,
                    provider=NewsProvider.NEWSAPI,
                    image_url=a.get("urlToImage"),
                    author=a.get("author"),
                    content=a.get("content")
                )
                for a in result.get("articles", [])
            ]

            return NewsSearchResult(
                query=query,
                articles=articles,
                total_results=result.get("totalResults", len(articles)),
                provider=NewsProvider.NEWSAPI,
                success=True,
                cost=0.003
            )
        except Exception as e:
            logger.warning(f"NewsAPI failed for '{query}': {e}")
            return NewsSearchResult(
                query=query,
                articles=[],
                total_results=0,
                provider=NewsProvider.NEWSAPI,
                success=False,
                error=str(e)
            )

    async def _search_mediastack(
        self,
        query: str,
        max_results: int,
        language: str
    ) -> NewsSearchResult:
        """Search using Mediastack."""
        if self._mediastack is None:
            return NewsSearchResult(
                query=query,
                articles=[],
                total_results=0,
                provider=NewsProvider.MEDIASTACK,
                success=False,
                error="Mediastack not available"
            )

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: self._mediastack.search(query, limit=max_results, languages=language)
            )

            articles = [
                NewsArticle(
                    title=a.get("title", ""),
                    description=a.get("description"),
                    url=a.get("url", ""),
                    source=a.get("source", "Unknown"),
                    published_at=datetime.fromisoformat(a["published_at"]) if a.get("published_at") else None,
                    provider=NewsProvider.MEDIASTACK,
                    image_url=a.get("image"),
                    author=a.get("author")
                )
                for a in result.get("data", [])
            ]

            return NewsSearchResult(
                query=query,
                articles=articles,
                total_results=result.get("pagination", {}).get("total", len(articles)),
                provider=NewsProvider.MEDIASTACK,
                success=True,
                cost=0.002
            )
        except Exception as e:
            logger.warning(f"Mediastack failed for '{query}': {e}")
            return NewsSearchResult(
                query=query,
                articles=[],
                total_results=0,
                provider=NewsProvider.MEDIASTACK,
                success=False,
                error=str(e)
            )

    async def search(
        self,
        query: str,
        max_results: int = 10,
        language: str = "en",
        quality: Optional[NewsQuality] = None,
        use_cache: bool = True,
        force_provider: Optional[NewsProvider] = None
    ) -> NewsSearchResult:
        """
        Search news with automatic provider fallback.

        Args:
            query: Search query
            max_results: Maximum number of results
            language: Language code (en, es, de, etc.)
            quality: Quality tier (FREE, STANDARD, PREMIUM)
            use_cache: Whether to use cached results
            force_provider: Force specific provider (skips routing)

        Returns:
            NewsSearchResult with articles
        """
        quality = quality or self.default_quality
        self._init_providers()

        # Check cache first
        if use_cache:
            cached = self._get_cached(query, max_results)
            if cached:
                logger.info(f"Cache hit for news query: '{query}'")
                return cached

        # Determine providers to try
        if force_provider:
            providers = [force_provider]
        else:
            providers = self._select_providers(quality)

        # Filter by quota availability
        available_providers = [
            p for p in providers if self._quotas[p].is_available()
        ]

        if not available_providers:
            logger.warning("All news providers are at quota limits")
            available_providers = providers  # Try anyway

        # Try each provider
        last_error = None
        for provider in available_providers:
            logger.info(f"Trying {provider.value} for news query: '{query}'")

            # Record usage
            self._quotas[provider].use()

            if provider == NewsProvider.GOOGLE_RSS:
                result = await self._search_google_rss(query, max_results, language)
            elif provider == NewsProvider.GNEWS:
                result = await self._search_gnews(query, max_results, language)
            elif provider == NewsProvider.NEWSAPI:
                result = await self._search_newsapi(query, max_results, language)
            elif provider == NewsProvider.MEDIASTACK:
                result = await self._search_mediastack(query, max_results, language)
            else:
                continue

            if result.success and result.articles:
                # Check if we have enough results (Cost-First: only escalate if insufficient)
                if len(result.articles) >= self.MIN_RESULTS_THRESHOLD:
                    # Track cost
                    try:
                        from ..cost_tracker import track_cost
                        track_cost(provider.value.replace("_", "-"), 1)
                    except Exception:
                        pass

                    # Cache successful result
                    if use_cache:
                        self._save_cache(query, max_results, result)

                    logger.info(f"[OK] Found {len(result.articles)} articles via {provider.value} (cost: ${self.PROVIDER_COSTS.get(provider, 0):.4f})")
                    return result
                else:
                    # Insufficient results - try next provider
                    logger.info(f"[INSUFFICIENT] {provider.value} returned only {len(result.articles)} articles (need {self.MIN_RESULTS_THRESHOLD}), trying next...")

            last_error = result.error

        # All providers failed
        return NewsSearchResult(
            query=query,
            articles=[],
            total_results=0,
            provider=providers[0] if providers else NewsProvider.GOOGLE_RSS,
            success=False,
            error=f"All providers failed. Last error: {last_error}"
        )

    async def search_company(
        self,
        company_name: str,
        max_results: int = 10,
        quality: Optional[NewsQuality] = None
    ) -> NewsSearchResult:
        """
        Search news for a specific company.

        Args:
            company_name: Company name
            max_results: Maximum results
            quality: Quality tier

        Returns:
            NewsSearchResult with company news
        """
        # Build optimized company query
        query = f'"{company_name}"'
        return await self.search(query, max_results, quality=quality)

    async def search_batch(
        self,
        queries: list[str],
        max_results_each: int = 5,
        quality: Optional[NewsQuality] = None
    ) -> list[NewsSearchResult]:
        """
        Search multiple queries concurrently.

        Args:
            queries: List of search queries
            max_results_each: Max results per query
            quality: Quality tier

        Returns:
            List of NewsSearchResults
        """
        tasks = [
            self.search(q, max_results_each, quality=quality)
            for q in queries
        ]
        return await asyncio.gather(*tasks)

    def search_sync(
        self,
        query: str,
        max_results: int = 10,
        quality: Optional[NewsQuality] = None
    ) -> NewsSearchResult:
        """
        Synchronous wrapper for search().

        Args:
            query: Search query
            max_results: Maximum results
            quality: Quality tier

        Returns:
            NewsSearchResult
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.search(query, max_results, quality=quality))

    def get_quota_status(self) -> dict[str, dict]:
        """Get quota status for all providers."""
        status = {}
        for provider, quota in self._quotas.items():
            quota._check_reset()
            status[provider.value] = {
                "daily_limit": quota.daily_limit,
                "daily_used": quota.daily_used,
                "daily_remaining": max(0, quota.daily_limit - quota.daily_used) if quota.daily_limit > 0 else "unlimited",
                "monthly_limit": quota.monthly_limit,
                "monthly_used": quota.monthly_used,
                "monthly_remaining": max(0, quota.monthly_limit - quota.monthly_used) if quota.monthly_limit > 0 else "unlimited",
                "available": quota.is_available()
            }
        return status

    def clear_cache(self, older_than_minutes: Optional[int] = None) -> int:
        """
        Clear news cache.

        Args:
            older_than_minutes: Only clear entries older than this many minutes.

        Returns:
            Number of cache entries cleared
        """
        cleared = 0

        for cache_file in self.cache_dir.glob("news_*.json"):
            try:
                if older_than_minutes:
                    with open(cache_file, "r") as f:
                        data = json.load(f)
                    timestamp = datetime.fromisoformat(data["timestamp"])
                    if datetime.now() - timestamp < timedelta(minutes=older_than_minutes):
                        continue

                cache_file.unlink()
                cleared += 1
            except Exception as e:
                logger.warning(f"Error clearing cache file {cache_file}: {e}")

        logger.info(f"Cleared {cleared} news cache entries")
        return cleared
