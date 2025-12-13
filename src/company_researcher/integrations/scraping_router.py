"""
Scraping Router - Smart routing between free and paid scraping providers.

Fallback Chain (cheapest first):
1. Crawl4AI (FREE) - Best for most pages, async, handles JS
2. Jina Reader (FREE) - Quick markdown conversion, good for articles
3. Firecrawl (PAID) - Complex JS sites, anti-bot, best quality

Features:
- Automatic fallback on failure
- Quality-based routing (simple pages → free, complex → paid)
- Cost tracking integration
- Caching to avoid re-scraping
- Concurrent scraping support

Usage:
    from company_researcher.integrations import get_scraping_router

    router = get_scraping_router()
    result = await router.scrape("https://example.com")
    # Automatically uses best free option first
"""

import asyncio
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import Optional
import json
from ..utils import get_logger, utc_now

logger = get_logger(__name__)


class ScrapingProvider(str, Enum):
    """Available scraping providers."""
    CRAWL4AI = "crawl4ai"
    JINA_READER = "jina_reader"
    FIRECRAWL = "firecrawl"
    SCRAPEGRAPH = "scrapegraph"


class ScrapingQuality(str, Enum):
    """Quality tier for scraping."""
    FREE = "free"           # Only use free providers
    STANDARD = "standard"   # Free first, fall back to paid
    PREMIUM = "premium"     # Use best provider regardless of cost


@dataclass
class ScrapeResult:
    """Result from a scraping operation."""
    url: str
    content: str           # Main content (markdown or text)
    html: Optional[str]    # Raw HTML if available
    title: Optional[str]
    provider: ScrapingProvider
    success: bool
    error: Optional[str] = None
    metadata: dict = None
    timestamp: datetime = None
    cost: float = 0.0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = utc_now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ProviderStatus:
    """Status of a scraping provider."""
    provider: ScrapingProvider
    available: bool
    last_used: Optional[datetime]
    success_rate: float
    avg_response_time: float
    errors_today: int


class ScrapingRouter:
    """
    Smart router for scraping providers.

    Routes requests to cheapest available provider,
    with automatic fallback on failures.
    """

    # Provider priority (cheapest first)
    PROVIDER_PRIORITY = [
        ScrapingProvider.CRAWL4AI,
        ScrapingProvider.JINA_READER,
        ScrapingProvider.FIRECRAWL,
        ScrapingProvider.SCRAPEGRAPH,
    ]

    # Sites that work best with specific providers
    PROVIDER_PREFERENCES = {
        # JS-heavy sites that need Crawl4AI or Firecrawl
        "linkedin.com": ScrapingProvider.FIRECRAWL,
        "twitter.com": ScrapingProvider.FIRECRAWL,
        "x.com": ScrapingProvider.FIRECRAWL,
        "facebook.com": ScrapingProvider.FIRECRAWL,
        # Simple article sites - Jina is fast
        "medium.com": ScrapingProvider.JINA_READER,
        "substack.com": ScrapingProvider.JINA_READER,
        "wikipedia.org": ScrapingProvider.JINA_READER,
        "reuters.com": ScrapingProvider.JINA_READER,
        "bbc.com": ScrapingProvider.JINA_READER,
    }

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        cache_ttl_hours: int = 24,
        max_retries: int = 2,
        default_quality: ScrapingQuality = ScrapingQuality.STANDARD
    ):
        """
        Initialize scraping router.

        Args:
            cache_dir: Directory for caching scraped content
            cache_ttl_hours: Cache time-to-live in hours
            max_retries: Max retries per provider before moving to next
            default_quality: Default quality tier
        """
        self.cache_dir = cache_dir or Path(".scraping_cache")
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.max_retries = max_retries
        self.default_quality = default_quality

        self._lock = Lock()
        self._provider_stats: dict[ScrapingProvider, dict] = {}
        self._crawl4ai = None
        self._jina = None
        self._firecrawl = None
        self._scrapegraph = None

        # Initialize cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"ScrapingRouter initialized with cache_ttl={cache_ttl_hours}h")

    def _init_providers(self):
        """Lazy initialize providers."""
        # Import here to avoid circular imports
        try:
            from .crawl4ai_client import get_crawl4ai
            self._crawl4ai = get_crawl4ai()
        except Exception as e:
            logger.warning(f"Crawl4AI not available: {e}")

        try:
            from .jina_reader import get_jina_reader
            self._jina = get_jina_reader()
        except Exception as e:
            logger.warning(f"Jina Reader not available: {e}")

        try:
            from .firecrawl_client import FirecrawlClient
            self._firecrawl = FirecrawlClient()
        except Exception as e:
            logger.warning(f"Firecrawl not available: {e}")

        try:
            from .scrapegraph_client import ScrapeGraphClient
            self._scrapegraph = ScrapeGraphClient()
        except Exception as e:
            logger.warning(f"ScrapeGraph not available: {e}")

    def _get_cache_key(self, url: str) -> str:
        """Generate cache key for URL."""
        return hashlib.md5(url.encode()).hexdigest()

    def _get_cached(self, url: str) -> Optional[ScrapeResult]:
        """Get cached result if exists and not expired."""
        cache_key = self._get_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Check expiration
            timestamp = datetime.fromisoformat(data["timestamp"])
            if utc_now() - timestamp > self.cache_ttl:
                cache_file.unlink()  # Delete expired
                return None

            return ScrapeResult(
                url=data["url"],
                content=data["content"],
                html=data.get("html"),
                title=data.get("title"),
                provider=ScrapingProvider(data["provider"]),
                success=True,
                metadata=data.get("metadata", {}),
                timestamp=timestamp,
                cost=0.0  # Cached = free
            )
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
            return None

    def _save_cache(self, result: ScrapeResult) -> None:
        """Save result to cache."""
        if not result.success:
            return

        cache_key = self._get_cache_key(result.url)
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            data = {
                "url": result.url,
                "content": result.content,
                "html": result.html,
                "title": result.title,
                "provider": result.provider.value,
                "metadata": result.metadata,
                "timestamp": result.timestamp.isoformat()
            }

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

    def _select_provider(
        self,
        url: str,
        quality: ScrapingQuality
    ) -> list[ScrapingProvider]:
        """
        Select providers to try based on URL and quality.

        Returns ordered list of providers to try.
        """
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower()

        providers = []

        # Check for site-specific preference
        preferred = None
        for site_domain, pref in self.PROVIDER_PREFERENCES.items():
            if site_domain in domain:
                preferred = pref
                break

        if quality == ScrapingQuality.FREE:
            # Only free providers
            providers = [
                ScrapingProvider.CRAWL4AI,
                ScrapingProvider.JINA_READER
            ]
        elif quality == ScrapingQuality.PREMIUM:
            # Best quality first
            if preferred:
                providers = [preferred]
            providers.extend([
                ScrapingProvider.FIRECRAWL,
                ScrapingProvider.SCRAPEGRAPH,
                ScrapingProvider.CRAWL4AI,
                ScrapingProvider.JINA_READER
            ])
        else:  # STANDARD
            # Free first, then paid
            if preferred and preferred in [ScrapingProvider.CRAWL4AI, ScrapingProvider.JINA_READER]:
                providers = [preferred]
            providers.extend([
                ScrapingProvider.CRAWL4AI,
                ScrapingProvider.JINA_READER,
                ScrapingProvider.FIRECRAWL,
                ScrapingProvider.SCRAPEGRAPH
            ])

        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for p in providers:
            if p not in seen:
                seen.add(p)
                unique.append(p)

        return unique

    async def _scrape_with_crawl4ai(self, url: str) -> ScrapeResult:
        """Scrape using Crawl4AI."""
        if self._crawl4ai is None:
            self._init_providers()

        if self._crawl4ai is None:
            return ScrapeResult(
                url=url,
                content="",
                html=None,
                title=None,
                provider=ScrapingProvider.CRAWL4AI,
                success=False,
                error="Crawl4AI not available"
            )

        try:
            result = await self._crawl4ai.scrape(url)
            return ScrapeResult(
                url=url,
                content=result.markdown or result.text or "",
                html=result.html,
                title=result.title,
                provider=ScrapingProvider.CRAWL4AI,
                success=True,
                metadata={"links": result.links, "images": result.images}
            )
        except Exception as e:
            logger.warning(f"Crawl4AI failed for {url}: {e}")
            return ScrapeResult(
                url=url,
                content="",
                html=None,
                title=None,
                provider=ScrapingProvider.CRAWL4AI,
                success=False,
                error=str(e)
            )

    async def _scrape_with_jina(self, url: str) -> ScrapeResult:
        """Scrape using Jina Reader."""
        if self._jina is None:
            self._init_providers()

        if self._jina is None:
            return ScrapeResult(
                url=url,
                content="",
                html=None,
                title=None,
                provider=ScrapingProvider.JINA_READER,
                success=False,
                error="Jina Reader not available"
            )

        try:
            result = await self._jina.read(url)
            return ScrapeResult(
                url=url,
                content=result.content,
                html=None,  # Jina returns markdown only
                title=result.title,
                provider=ScrapingProvider.JINA_READER,
                success=True,
                metadata={"word_count": result.word_count}
            )
        except Exception as e:
            logger.warning(f"Jina Reader failed for {url}: {e}")
            return ScrapeResult(
                url=url,
                content="",
                html=None,
                title=None,
                provider=ScrapingProvider.JINA_READER,
                success=False,
                error=str(e)
            )

    async def _scrape_with_firecrawl(self, url: str) -> ScrapeResult:
        """Scrape using Firecrawl."""
        if self._firecrawl is None:
            self._init_providers()

        if self._firecrawl is None:
            return ScrapeResult(
                url=url,
                content="",
                html=None,
                title=None,
                provider=ScrapingProvider.FIRECRAWL,
                success=False,
                error="Firecrawl not available"
            )

        try:
            # Firecrawl has sync API, wrap in executor
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None, self._firecrawl.scrape_url, url
            )

            return ScrapeResult(
                url=url,
                content=result.get("markdown", "") or result.get("content", ""),
                html=result.get("html"),
                title=result.get("title"),
                provider=ScrapingProvider.FIRECRAWL,
                success=True,
                cost=0.01  # ~$0.01/page
            )
        except Exception as e:
            logger.warning(f"Firecrawl failed for {url}: {e}")
            return ScrapeResult(
                url=url,
                content="",
                html=None,
                title=None,
                provider=ScrapingProvider.FIRECRAWL,
                success=False,
                error=str(e)
            )

    async def _scrape_with_scrapegraph(self, url: str) -> ScrapeResult:
        """Scrape using ScrapeGraph."""
        if self._scrapegraph is None:
            self._init_providers()

        if self._scrapegraph is None:
            return ScrapeResult(
                url=url,
                content="",
                html=None,
                title=None,
                provider=ScrapingProvider.SCRAPEGRAPH,
                success=False,
                error="ScrapeGraph not available"
            )

        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None, self._scrapegraph.scrape, url
            )

            return ScrapeResult(
                url=url,
                content=result.get("content", ""),
                html=result.get("html"),
                title=result.get("title"),
                provider=ScrapingProvider.SCRAPEGRAPH,
                success=True,
                cost=0.01
            )
        except Exception as e:
            logger.warning(f"ScrapeGraph failed for {url}: {e}")
            return ScrapeResult(
                url=url,
                content="",
                html=None,
                title=None,
                provider=ScrapingProvider.SCRAPEGRAPH,
                success=False,
                error=str(e)
            )

    async def scrape(
        self,
        url: str,
        quality: Optional[ScrapingQuality] = None,
        use_cache: bool = True,
        force_provider: Optional[ScrapingProvider] = None
    ) -> ScrapeResult:
        """
        Scrape a URL with automatic provider fallback.

        Args:
            url: URL to scrape
            quality: Quality tier (FREE, STANDARD, PREMIUM)
            use_cache: Whether to use cached results
            force_provider: Force specific provider (skips routing)

        Returns:
            ScrapeResult with content and metadata
        """
        quality = quality or self.default_quality

        # Check cache first
        if use_cache:
            cached = self._get_cached(url)
            if cached:
                logger.info(f"Cache hit for {url}")
                return cached

        # Determine providers to try
        if force_provider:
            providers = [force_provider]
        else:
            providers = self._select_provider(url, quality)

        # Try each provider
        last_error = None
        for provider in providers:
            logger.info(f"Trying {provider.value} for {url}")

            if provider == ScrapingProvider.CRAWL4AI:
                result = await self._scrape_with_crawl4ai(url)
            elif provider == ScrapingProvider.JINA_READER:
                result = await self._scrape_with_jina(url)
            elif provider == ScrapingProvider.FIRECRAWL:
                result = await self._scrape_with_firecrawl(url)
            elif provider == ScrapingProvider.SCRAPEGRAPH:
                result = await self._scrape_with_scrapegraph(url)
            else:
                continue

            if result.success and result.content:
                # Track cost
                try:
                    from .cost_tracker import track_cost
                    track_cost(provider.value.replace("_", "-"), 1)
                except Exception as e:
                    logger.debug(f"Failed to track cost for {provider.value}: {e}")

                # Cache successful result
                if use_cache:
                    self._save_cache(result)

                logger.info(f"Successfully scraped {url} with {provider.value}")
                return result

            last_error = result.error

        # All providers failed
        return ScrapeResult(
            url=url,
            content="",
            html=None,
            title=None,
            provider=providers[0] if providers else ScrapingProvider.CRAWL4AI,
            success=False,
            error=f"All providers failed. Last error: {last_error}"
        )

    async def scrape_batch(
        self,
        urls: list[str],
        quality: Optional[ScrapingQuality] = None,
        max_concurrent: int = 5
    ) -> list[ScrapeResult]:
        """
        Scrape multiple URLs concurrently.

        Args:
            urls: List of URLs to scrape
            quality: Quality tier
            max_concurrent: Max concurrent scrapes

        Returns:
            List of ScrapeResults
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def scrape_with_limit(url: str) -> ScrapeResult:
            async with semaphore:
                return await self.scrape(url, quality)

        tasks = [scrape_with_limit(url) for url in urls]
        return await asyncio.gather(*tasks)

    def scrape_sync(
        self,
        url: str,
        quality: Optional[ScrapingQuality] = None
    ) -> ScrapeResult:
        """
        Synchronous wrapper for scrape().

        Args:
            url: URL to scrape
            quality: Quality tier

        Returns:
            ScrapeResult
        """
        return asyncio.run(self.scrape(url, quality))

    def get_provider_status(self) -> list[ProviderStatus]:
        """Get status of all providers."""
        statuses = []

        # Check each provider
        self._init_providers()

        providers = [
            (ScrapingProvider.CRAWL4AI, self._crawl4ai),
            (ScrapingProvider.JINA_READER, self._jina),
            (ScrapingProvider.FIRECRAWL, self._firecrawl),
            (ScrapingProvider.SCRAPEGRAPH, self._scrapegraph),
        ]

        for provider, client in providers:
            statuses.append(ProviderStatus(
                provider=provider,
                available=client is not None,
                last_used=self._provider_stats.get(provider, {}).get("last_used"),
                success_rate=self._provider_stats.get(provider, {}).get("success_rate", 0.0),
                avg_response_time=self._provider_stats.get(provider, {}).get("avg_time", 0.0),
                errors_today=self._provider_stats.get(provider, {}).get("errors_today", 0)
            ))

        return statuses

    def clear_cache(self, older_than_hours: Optional[int] = None) -> int:
        """
        Clear scraping cache.

        Args:
            older_than_hours: Only clear entries older than this many hours.
                             If None, clear all.

        Returns:
            Number of cache entries cleared
        """
        cleared = 0

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                if older_than_hours:
                    with open(cache_file, "r") as f:
                        data = json.load(f)
                    timestamp = datetime.fromisoformat(data["timestamp"])
                    if utc_now() - timestamp < timedelta(hours=older_than_hours):
                        continue

                cache_file.unlink()
                cleared += 1
            except Exception as e:
                logger.warning(f"Error clearing cache file {cache_file}: {e}")

        logger.info(f"Cleared {cleared} cache entries")
        return cleared


# Singleton instance
_scraping_router: Optional[ScrapingRouter] = None
_router_lock = Lock()


def get_scraping_router(
    cache_dir: Optional[Path] = None,
    default_quality: ScrapingQuality = ScrapingQuality.STANDARD
) -> ScrapingRouter:
    """
    Get or create singleton scraping router.

    Args:
        cache_dir: Directory for cache
        default_quality: Default quality tier

    Returns:
        ScrapingRouter instance
    """
    global _scraping_router

    with _router_lock:
        if _scraping_router is None:
            _scraping_router = ScrapingRouter(
                cache_dir=cache_dir,
                default_quality=default_quality
            )
        return _scraping_router


async def smart_scrape(
    url: str,
    quality: ScrapingQuality = ScrapingQuality.STANDARD
) -> ScrapeResult:
    """
    Quick function to scrape a URL with smart provider routing.

    Args:
        url: URL to scrape
        quality: Quality tier

    Returns:
        ScrapeResult
    """
    router = get_scraping_router()
    return await router.scrape(url, quality)


def smart_scrape_sync(
    url: str,
    quality: ScrapingQuality = ScrapingQuality.STANDARD
) -> ScrapeResult:
    """
    Synchronous version of smart_scrape.

    Args:
        url: URL to scrape
        quality: Quality tier

    Returns:
        ScrapeResult
    """
    router = get_scraping_router()
    return router.scrape_sync(url, quality)


# Example usage
if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)

    async def demo():
        router = get_scraping_router()

        # Test URLs
        urls = [
            "https://en.wikipedia.org/wiki/Apple_Inc.",
            "https://www.reuters.com/",
        ]

        print("Testing ScrapingRouter...")
        for url in urls:
            print(f"\nScraping: {url}")
            result = await router.scrape(url, quality=ScrapingQuality.FREE)
            print(f"  Provider: {result.provider.value}")
            print(f"  Success: {result.success}")
            print(f"  Content length: {len(result.content)} chars")
            if result.title:
                print(f"  Title: {result.title}")
            if result.error:
                print(f"  Error: {result.error}")

        # Check provider status
        print("\nProvider Status:")
        for status in router.get_provider_status():
            print(f"  {status.provider.value}: {'OK' if status.available else 'N/A'}")

    asyncio.run(demo())
