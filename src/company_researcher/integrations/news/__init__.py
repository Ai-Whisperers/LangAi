"""
News Routing Package.

This package provides smart routing between free and paid news providers with:
- Automatic provider selection and fallback
- Quota tracking
- Caching
- Cost tracking integration

Modules:
    - models: Data models (NewsProvider, NewsQuality, NewsArticle, etc.)
    - router: NewsRouter class with routing logic

Usage:
    from company_researcher.integrations.news import (
        get_news_router,
        smart_news_search,
        NewsQuality,
    )

    # Use singleton router
    router = get_news_router()
    result = await router.search("Tesla earnings")

    # Or use convenience function
    result = await smart_news_search("Tesla earnings", quality=NewsQuality.FREE)
"""

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
from .router import NewsRouter

# Re-export all public APIs
__all__ = [
    # Models
    "NewsProvider",
    "NewsQuality",
    "NewsArticle",
    "NewsSearchResult",
    "ProviderQuota",
    # Router
    "NewsRouter",
    # Convenience functions
    "get_news_router",
    "smart_news_search",
    "smart_news_search_sync",
]


# Singleton instance
_news_router: Optional[NewsRouter] = None
_router_lock = Lock()


def get_news_router(
    cache_dir: Optional[Path] = None,
    default_quality: NewsQuality = NewsQuality.STANDARD
) -> NewsRouter:
    """
    Get or create singleton news router.

    Args:
        cache_dir: Directory for cache
        default_quality: Default quality tier

    Returns:
        NewsRouter instance
    """
    global _news_router

    with _router_lock:
        if _news_router is None:
            _news_router = NewsRouter(
                cache_dir=cache_dir,
                default_quality=default_quality
            )
        return _news_router


async def smart_news_search(
    query: str,
    max_results: int = 10,
    quality: NewsQuality = NewsQuality.STANDARD
) -> NewsSearchResult:
    """
    Quick function to search news with smart provider routing.

    Args:
        query: Search query
        max_results: Maximum results
        quality: Quality tier

    Returns:
        NewsSearchResult
    """
    router = get_news_router()
    return await router.search(query, max_results, quality=quality)


def smart_news_search_sync(
    query: str,
    max_results: int = 10,
    quality: NewsQuality = NewsQuality.STANDARD
) -> NewsSearchResult:
    """
    Synchronous version of smart_news_search.

    Args:
        query: Search query
        max_results: Maximum results
        quality: Quality tier

    Returns:
        NewsSearchResult
    """
    router = get_news_router()
    return router.search_sync(query, max_results, quality)
