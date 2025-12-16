"""
Unified News Data Provider with Fallback Chain.

Implements a priority-based fallback strategy:
    1. NewsAPI (100 req/day dev, excellent coverage)
    2. GNews (100 req/day, global coverage)
    3. Mediastack (500 req/month, good coverage)
    4. Tavily (fallback to web search for news)

Each provider is tried in order until news is successfully retrieved.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from ..utils import get_logger, utc_now

logger = get_logger(__name__)


class NewsProviderStatus(Enum):
    """Provider availability status."""

    AVAILABLE = "available"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class NewsArticle:
    """Unified news article structure."""

    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: str = ""
    source_name: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    sentiment: Optional[str] = None  # positive, negative, neutral
    relevance_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "content": self.content,
            "url": self.url,
            "source_name": self.source_name,
            "author": self.author,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "image_url": self.image_url,
            "category": self.category,
            "sentiment": self.sentiment,
            "relevance_score": self.relevance_score,
        }


@dataclass
class NewsResult:
    """Result from news search."""

    query: str
    articles: List[NewsArticle] = field(default_factory=list)
    total_results: int = 0
    sources_used: List[str] = field(default_factory=list)
    search_time: datetime = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "articles": [a.to_dict() for a in self.articles],
            "total_results": self.total_results,
            "sources_used": self.sources_used,
            "search_time": self.search_time.isoformat(),
        }


@dataclass
class ProviderState:
    """Tracks state of a news provider."""

    name: str
    status: NewsProviderStatus = NewsProviderStatus.AVAILABLE
    last_call: Optional[datetime] = None
    last_error: Optional[str] = None
    calls_count: int = 0
    limit: Optional[int] = None
    reset_period: str = "daily"  # daily, monthly
    reset_time: Optional[datetime] = None

    def can_call(self) -> bool:
        """Check if provider can be called."""
        if self.status == NewsProviderStatus.DISABLED:
            return False
        if self.status == NewsProviderStatus.RATE_LIMITED:
            if self.reset_time and utc_now() > self.reset_time:
                self.status = NewsProviderStatus.AVAILABLE
                self.calls_count = 0
                return True
            return False
        if self.limit and self.calls_count >= self.limit:
            self.status = NewsProviderStatus.RATE_LIMITED
            if self.reset_period == "daily":
                self.reset_time = utc_now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
            else:  # monthly
                next_month = utc_now().replace(day=1) + timedelta(days=32)
                self.reset_time = next_month.replace(day=1)
            return False
        return True

    def record_call(self, success: bool, error: Optional[str] = None):
        """Record a call attempt."""
        self.last_call = utc_now()
        self.calls_count += 1
        if not success:
            self.last_error = error
            if error and "rate limit" in error.lower():
                self.status = NewsProviderStatus.RATE_LIMITED


class NewsProvider:
    """
    Unified news provider with automatic fallback.

    Usage:
        provider = NewsProvider(config)
        news = provider.search_news("Microsoft", max_results=10)

        # Or search with date range
        news = provider.search_news(
            "Apple earnings",
            from_date=utc_now() - timedelta(days=7)
        )
    """

    def __init__(
        self, config: Any, providers: Optional[List[str]] = None, enable_caching: bool = True
    ):
        """
        Initialize the news provider.

        Args:
            config: Application configuration
            providers: List of provider names to use (default: all available)
            enable_caching: Whether to cache results
        """
        self.config = config
        self.enable_caching = enable_caching
        self._cache: Dict[str, NewsResult] = {}
        self._cache_ttl = timedelta(minutes=30)  # News cache shorter

        # Initialize provider states
        self.providers: Dict[str, ProviderState] = {}

        # Register available providers
        self._register_providers(providers)

    def _register_providers(self, providers: Optional[List[str]] = None):
        """Register available providers based on configuration."""
        all_providers = [
            ("newsapi", 100, "daily"),
            ("gnews", 100, "daily"),
            ("mediastack", 500, "monthly"),
            ("tavily", 1000, "daily"),  # Fallback to Tavily search
        ]

        for name, limit, reset_period in all_providers:
            # Skip if not in requested providers list
            if providers and name not in providers:
                continue

            # Check if API key is configured
            if name == "newsapi" and not getattr(self.config, "newsapi_api_key", None):
                logger.debug("NewsAPI key not configured, skipping")
                continue
            if name == "gnews" and not getattr(self.config, "gnews_api_key", None):
                logger.debug("GNews key not configured, skipping")
                continue
            if name == "mediastack" and not getattr(self.config, "mediastack_api_key", None):
                logger.debug("Mediastack key not configured, skipping")
                continue
            if name == "tavily" and not getattr(self.config, "tavily_api_key", None):
                logger.debug("Tavily key not configured, skipping")
                continue

            self.providers[name] = ProviderState(name=name, limit=limit, reset_period=reset_period)
            logger.info(f"Registered news provider: {name}")

    def search_news(
        self,
        query: str,
        max_results: int = 10,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        language: str = "en",
        category: Optional[str] = None,
        force_refresh: bool = False,
    ) -> NewsResult:
        """
        Search for news articles using fallback chain.

        Args:
            query: Search query
            max_results: Maximum number of results
            from_date: Start date for search
            to_date: End date for search
            language: Language code
            category: News category filter
            force_refresh: Bypass cache if True

        Returns:
            NewsResult with articles from available providers
        """
        cache_key = f"{query}:{max_results}:{language}"

        # Check cache
        if self.enable_caching and not force_refresh:
            cached = self._get_cached(cache_key)
            if cached:
                logger.debug(f"Returning cached news for '{query}'")
                return cached

        result = NewsResult(query=query)
        successful_providers = []

        for name, state in self.providers.items():
            if not state.can_call():
                logger.debug(f"Skipping {name}: {state.status.value}")
                continue

            try:
                logger.info(f"Fetching news for '{query}' from {name}...")
                articles = self._fetch_from_provider(
                    name, query, max_results, from_date, to_date, language, category
                )

                if articles:
                    result.articles.extend(articles)
                    successful_providers.append(name)
                    state.record_call(success=True)
                    logger.info(f"Got {len(articles)} articles from {name}")

                    # If we have enough results, stop
                    if len(result.articles) >= max_results:
                        break
                else:
                    state.record_call(success=False, error="No articles returned")

            except Exception as e:
                error_msg = str(e)
                logger.warning(f"{name} failed for '{query}': {error_msg}")
                state.record_call(success=False, error=error_msg)
                continue

        # Deduplicate and sort by date
        result.articles = self._deduplicate_articles(result.articles)
        result.articles = sorted(
            result.articles, key=lambda a: a.published_at or datetime.min, reverse=True
        )[:max_results]

        result.total_results = len(result.articles)
        result.sources_used = successful_providers

        # Cache result
        if self.enable_caching and result.articles:
            self._cache[cache_key] = result

        logger.info(
            f"Got {len(result.articles)} articles for '{query}' "
            f"from {', '.join(successful_providers) or 'no providers'}"
        )
        return result

    def _fetch_from_provider(
        self,
        provider: str,
        query: str,
        max_results: int,
        from_date: Optional[datetime],
        to_date: Optional[datetime],
        language: str,
        category: Optional[str],
    ) -> List[NewsArticle]:
        """Fetch articles from a specific provider."""
        if provider == "newsapi":
            return self._fetch_newsapi(query, max_results, from_date, to_date, language)
        elif provider == "gnews":
            return self._fetch_gnews(query, max_results, language)
        elif provider == "mediastack":
            return self._fetch_mediastack(query, max_results, language, category)
        elif provider == "tavily":
            return self._fetch_tavily_news(query, max_results)
        return []

    def _fetch_newsapi(
        self,
        query: str,
        max_results: int,
        from_date: Optional[datetime],
        to_date: Optional[datetime],
        language: str,
    ) -> List[NewsArticle]:
        """Fetch from NewsAPI."""
        from .news_api import NewsAPIClient

        client = NewsAPIClient(self.config.newsapi_api_key)

        articles_data = client.search_everything(
            query=query,
            from_date=from_date,
            to_date=to_date,
            language=language,
            page_size=max_results,
        )

        articles = []
        for a in articles_data:
            articles.append(
                NewsArticle(
                    title=a.get("title", ""),
                    description=a.get("description"),
                    content=a.get("content"),
                    url=a.get("url", ""),
                    source_name=a.get("source", {}).get("name"),
                    author=a.get("author"),
                    published_at=self._parse_date(a.get("publishedAt")),
                    image_url=a.get("urlToImage"),
                )
            )
        return articles

    def _fetch_gnews(self, query: str, max_results: int, language: str) -> List[NewsArticle]:
        """Fetch from GNews."""
        from .gnews import GNewsClient

        client = GNewsClient(self.config.gnews_api_key)

        articles_data = client.search(query=query, max_results=max_results, language=language)

        articles = []
        for a in articles_data:
            articles.append(
                NewsArticle(
                    title=a.get("title", ""),
                    description=a.get("description"),
                    content=a.get("content"),
                    url=a.get("url", ""),
                    source_name=a.get("source", {}).get("name"),
                    published_at=self._parse_date(a.get("publishedAt")),
                    image_url=a.get("image"),
                )
            )
        return articles

    def _fetch_mediastack(
        self, query: str, max_results: int, language: str, category: Optional[str]
    ) -> List[NewsArticle]:
        """Fetch from Mediastack."""
        from .mediastack import MediastackClient

        client = MediastackClient(self.config.mediastack_api_key)

        articles_data = client.search(
            keywords=query, limit=max_results, languages=language, categories=category
        )

        articles = []
        for a in articles_data:
            articles.append(
                NewsArticle(
                    title=a.get("title", ""),
                    description=a.get("description"),
                    url=a.get("url", ""),
                    source_name=a.get("source"),
                    author=a.get("author"),
                    published_at=self._parse_date(a.get("published_at")),
                    image_url=a.get("image"),
                    category=a.get("category"),
                )
            )
        return articles

    def _fetch_tavily_news(self, query: str, max_results: int) -> List[NewsArticle]:
        """Fetch news via Tavily web search."""
        from tavily import TavilyClient

        client = TavilyClient(api_key=self.config.tavily_api_key)

        # Search for news specifically
        news_query = f"{query} news latest"
        results = client.search(query=news_query, max_results=max_results, search_depth="basic")

        articles = []
        for r in results.get("results", []):
            articles.append(
                NewsArticle(
                    title=r.get("title", ""),
                    description=r.get("content", "")[:500] if r.get("content") else None,
                    content=r.get("content"),
                    url=r.get("url", ""),
                    source_name=self._extract_domain(r.get("url", "")),
                    relevance_score=r.get("score", 0.0),
                )
            )
        return articles

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse various date formats."""
        if not date_str:
            return None
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            pass
        try:
            # Try common format
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except (ValueError, AttributeError):
            pass
        try:
            # Try date only
            return datetime.strptime(date_str[:10], "%Y-%m-%d")
        except (ValueError, AttributeError):
            return None

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return url

    def _deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on URL."""
        seen_urls = set()
        unique = []
        for article in articles:
            # Normalize URL
            url = article.url.lower().rstrip("/")
            if url not in seen_urls:
                seen_urls.add(url)
                unique.append(article)
        return unique

    def _get_cached(self, cache_key: str) -> Optional[NewsResult]:
        """Get cached result if valid."""
        if cache_key not in self._cache:
            return None
        cached = self._cache[cache_key]
        if utc_now() - cached.search_time > self._cache_ttl:
            del self._cache[cache_key]
            return None
        return cached

    def get_company_news(
        self, company_name: str, max_results: int = 10, days_back: int = 30
    ) -> NewsResult:
        """
        Get recent news for a specific company.

        Args:
            company_name: Company name to search for
            max_results: Maximum number of results
            days_back: How many days back to search

        Returns:
            NewsResult with company news
        """
        from_date = utc_now() - timedelta(days=days_back)
        return self.search_news(query=company_name, max_results=max_results, from_date=from_date)

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers."""
        return {
            name: {
                "status": state.status.value,
                "calls_count": state.calls_count,
                "limit": state.limit,
                "reset_period": state.reset_period,
                "last_call": state.last_call.isoformat() if state.last_call else None,
                "last_error": state.last_error,
            }
            for name, state in self.providers.items()
        }

    def clear_cache(self):
        """Clear the news cache."""
        self._cache.clear()


# Factory function
def create_news_provider(config: Any) -> NewsProvider:
    """Create a configured news provider."""
    return NewsProvider(config)
