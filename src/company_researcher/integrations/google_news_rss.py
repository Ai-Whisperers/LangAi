"""
Google News RSS Integration - FREE News API.

Access Google News via RSS feeds - completely free, no API key required.
Unlimited queries, real-time news.

Features:
- Topic search
- Company news
- Geographic filtering
- Language support
- NO API KEY REQUIRED
- UNLIMITED QUERIES

Cost: $0 (completely free)
Replaces: NewsAPI ($30/mo), GNews ($30-80/mo), Mediastack ($15-50/mo)

Usage:
    from company_researcher.integrations.google_news_rss import get_google_news

    news = get_google_news()

    # Search for company news
    articles = news.search("Tesla earnings")

    # Get news by topic
    tech_news = news.get_topic_news("technology")

    # Get company-specific news
    company_news = news.get_company_news("Apple Inc")
"""

from dataclasses import dataclass
from datetime import datetime
from threading import Lock
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import feedparser

from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class NewsArticle:
    """A news article from Google News."""

    title: str
    link: str
    source: str
    published: Optional[datetime] = None
    published_str: str = ""
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "link": self.link,
            "source": self.source,
            "published": self.published.isoformat() if self.published else None,
            "published_str": self.published_str,
            "summary": self.summary,
        }


@dataclass
class NewsSearchResult:
    """Result from a news search."""

    query: str
    articles: List[NewsArticle]
    total_results: int = 0
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "articles": [a.to_dict() for a in self.articles],
            "total_results": self.total_results,
            "success": self.success,
            "error": self.error,
        }


class GoogleNewsRSS:
    """
    Free news aggregator using Google News RSS feeds.

    100% free, no API key required, unlimited queries.
    Real-time news from thousands of sources.
    """

    BASE_URL = "https://news.google.com/rss"

    # Google News topic codes
    TOPICS = {
        "world": "WORLD",
        "nation": "NATION",
        "business": "BUSINESS",
        "technology": "TECHNOLOGY",
        "entertainment": "ENTERTAINMENT",
        "sports": "SPORTS",
        "science": "SCIENCE",
        "health": "HEALTH",
    }

    # Language/country codes
    LOCALES = {
        "en-US": {"hl": "en-US", "gl": "US", "ceid": "US:en"},
        "en-GB": {"hl": "en-GB", "gl": "GB", "ceid": "GB:en"},
        "es-ES": {"hl": "es-419", "gl": "ES", "ceid": "ES:es"},
        "es-MX": {"hl": "es-419", "gl": "MX", "ceid": "MX:es"},
        "pt-BR": {"hl": "pt-BR", "gl": "BR", "ceid": "BR:pt-419"},
        "de-DE": {"hl": "de", "gl": "DE", "ceid": "DE:de"},
        "fr-FR": {"hl": "fr", "gl": "FR", "ceid": "FR:fr"},
        "zh-CN": {"hl": "zh-CN", "gl": "CN", "ceid": "CN:zh-Hans"},
    }

    def __init__(self, locale: str = "en-US", timeout: int = 10):
        """
        Initialize Google News RSS client.

        Args:
            locale: Language/country code (en-US, es-ES, etc.)
            timeout: Request timeout in seconds
        """
        self.locale = locale
        self.timeout = timeout
        self.locale_params = self.LOCALES.get(locale, self.LOCALES["en-US"])

        self._total_queries = 0
        self._lock = Lock()

    def _build_url(self, path: str = "", query: str = "") -> str:
        """Build Google News RSS URL with locale params."""
        params = self.locale_params.copy()

        if query:
            url = f"{self.BASE_URL}/search?q={quote(query)}"
        elif path:
            url = f"{self.BASE_URL}/{path}"
        else:
            url = self.BASE_URL

        # Add locale params
        url += f"&hl={params['hl']}&gl={params['gl']}&ceid={params['ceid']}"

        return url

    def _parse_entry(self, entry: Any) -> NewsArticle:
        """Parse a feedparser entry into NewsArticle."""
        # Extract source from title (Google News format: "Title - Source")
        title = entry.get("title", "")
        source = ""

        if " - " in title:
            parts = title.rsplit(" - ", 1)
            if len(parts) == 2:
                title = parts[0]
                source = parts[1]

        # Parse published date
        published = None
        published_str = entry.get("published", "")

        if published_str:
            try:
                # feedparser provides parsed time
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
            except Exception as e:
                logger.debug(f"Failed to parse RSS published date '{published_str}': {e}")

        return NewsArticle(
            title=title,
            link=entry.get("link", ""),
            source=source,
            published=published,
            published_str=published_str,
            summary=entry.get("summary", ""),
        )

    def search(
        self, query: str, max_results: int = 20, when: Optional[str] = None
    ) -> NewsSearchResult:
        """
        Search Google News (with caching).

        Args:
            query: Search query
            max_results: Maximum results to return
            when: Time filter (1h, 1d, 7d, 1m, 1y)

        Returns:
            NewsSearchResult with articles
        """
        # Check cache first (6-hour TTL)
        cache_key = f"{query}:{max_results}:{when or 'all'}"
        try:
            from ..cache.result_cache import cache_news, get_cached_news

            cached = get_cached_news(cache_key)
            if cached:
                logger.debug(f"[CACHE HIT] News search: '{query}'")
                return NewsSearchResult(
                    query=query,
                    articles=[NewsArticle(**a) for a in cached],
                    total_results=len(cached),
                    success=True,
                )
        except ImportError:
            pass

        try:
            # Add time filter to query if specified
            search_query = query
            if when:
                search_query = f"{query} when:{when}"

            url = self._build_url(query=search_query)

            feed = feedparser.parse(url)

            articles = []
            for entry in feed.entries[:max_results]:
                articles.append(self._parse_entry(entry))

            with self._lock:
                self._total_queries += 1

            # Cache results (6 hours)
            try:
                from ..cache.result_cache import cache_news

                cache_news(cache_key, [a.to_dict() for a in articles])
                logger.debug(f"[CACHED] News search: '{query}'")
            except ImportError:
                pass

            return NewsSearchResult(
                query=query, articles=articles, total_results=len(articles), success=True
            )

        except Exception as e:
            logger.error(f"Google News search error for '{query}': {e}")
            return NewsSearchResult(query=query, articles=[], success=False, error=str(e))

    def get_topic_news(self, topic: str, max_results: int = 20) -> NewsSearchResult:
        """
        Get news for a specific topic.

        Args:
            topic: Topic name (world, business, technology, etc.)
            max_results: Maximum results

        Returns:
            NewsSearchResult with articles
        """
        topic_code = self.TOPICS.get(topic.lower())

        if not topic_code:
            # Treat as search query if not a known topic
            return self.search(topic, max_results)

        try:
            url = self._build_url(path=f"headlines/section/topic/{topic_code}")

            feed = feedparser.parse(url)

            articles = []
            for entry in feed.entries[:max_results]:
                articles.append(self._parse_entry(entry))

            with self._lock:
                self._total_queries += 1

            return NewsSearchResult(
                query=f"topic:{topic}", articles=articles, total_results=len(articles), success=True
            )

        except Exception as e:
            logger.error(f"Google News topic error for '{topic}': {e}")
            return NewsSearchResult(
                query=f"topic:{topic}", articles=[], success=False, error=str(e)
            )

    def get_company_news(
        self,
        company_name: str,
        ticker: Optional[str] = None,
        max_results: int = 20,
        when: str = "7d",
    ) -> NewsSearchResult:
        """
        Get news for a specific company.

        Args:
            company_name: Company name
            ticker: Stock ticker (optional, improves results)
            max_results: Maximum results
            when: Time filter (1d, 7d, 1m)

        Returns:
            NewsSearchResult with company news
        """
        # Build optimized search query
        query_parts = [f'"{company_name}"']

        if ticker:
            query_parts.append(f"OR {ticker}")

        # Add business/financial context
        query_parts.append("(earnings OR revenue OR stock OR CEO OR announcement)")

        query = " ".join(query_parts)

        return self.search(query, max_results, when)

    def get_industry_news(
        self, industry: str, max_results: int = 20, when: str = "7d"
    ) -> NewsSearchResult:
        """
        Get news for an industry.

        Args:
            industry: Industry name (e.g., "electric vehicles", "AI chips")
            max_results: Maximum results
            when: Time filter

        Returns:
            NewsSearchResult with industry news
        """
        query = f"{industry} industry market"
        return self.search(query, max_results, when)

    def get_headlines(self, max_results: int = 20) -> NewsSearchResult:
        """
        Get top headlines.

        Args:
            max_results: Maximum results

        Returns:
            NewsSearchResult with top headlines
        """
        try:
            url = self._build_url()

            feed = feedparser.parse(url)

            articles = []
            for entry in feed.entries[:max_results]:
                articles.append(self._parse_entry(entry))

            with self._lock:
                self._total_queries += 1

            return NewsSearchResult(
                query="headlines", articles=articles, total_results=len(articles), success=True
            )

        except Exception as e:
            logger.error(f"Google News headlines error: {e}")
            return NewsSearchResult(query="headlines", articles=[], success=False, error=str(e))

    def get_geo_news(self, location: str, max_results: int = 20) -> NewsSearchResult:
        """
        Get news for a geographic location.

        Args:
            location: Location name (city, country, region)
            max_results: Maximum results

        Returns:
            NewsSearchResult with location news
        """
        query = f"location:{location}"
        return self.search(query, max_results)

    def set_locale(self, locale: str) -> None:
        """
        Change the locale for news results.

        Args:
            locale: New locale code (en-US, es-ES, etc.)
        """
        if locale in self.LOCALES:
            self.locale = locale
            self.locale_params = self.LOCALES[locale]
        else:
            logger.warning(f"Unknown locale: {locale}. Available: {list(self.LOCALES.keys())}")

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        with self._lock:
            return {
                "total_queries": self._total_queries,
                "locale": self.locale,
                "cost": 0.0,  # FREE!
            }

    def reset_stats(self) -> None:
        """Reset statistics."""
        with self._lock:
            self._total_queries = 0


# Singleton instance
_google_news: Optional[GoogleNewsRSS] = None
_news_lock = Lock()


def get_google_news(locale: str = "en-US") -> GoogleNewsRSS:
    """Get singleton Google News instance."""
    global _google_news
    if _google_news is None:
        with _news_lock:
            if _google_news is None:
                _google_news = GoogleNewsRSS(locale=locale)
    return _google_news


def reset_google_news() -> None:
    """Reset Google News instance."""
    global _google_news
    _google_news = None


# Convenience functions
def search_news(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Quick function to search news."""
    news = get_google_news()
    result = news.search(query, max_results)
    return [a.to_dict() for a in result.articles] if result.success else []


def get_company_news(company: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Quick function to get company news."""
    news = get_google_news()
    result = news.get_company_news(company, max_results=max_results)
    return [a.to_dict() for a in result.articles] if result.success else []
