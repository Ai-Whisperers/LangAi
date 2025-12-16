"""
News Router - Smart routing between free and paid news providers.

Fallback Chain (cheapest first):
1. Google News RSS (FREE) - Unlimited, real-time news
2. GNews (FREE tier: 100/day) - Good quality, 100 free/day
3. NewsAPI (FREE tier: 100/day) - Best quality, dev only
4. Mediastack (FREE tier: 500/month) - Live news

Features:
- Automatic fallback on failure or rate limits
- Source deduplication across providers
- Unified article format
- Cost tracking integration
- Caching support

Usage:
    from company_researcher.integrations import get_news_router

    router = get_news_router()
    articles = await router.search("Tesla earnings")
    # Automatically uses free Google News RSS first
"""

import asyncio
import logging

# Import from news package
from .news import (
    NewsArticle,
    NewsProvider,
    NewsQuality,
    NewsRouter,
    NewsSearchResult,
    ProviderQuota,
    get_news_router,
    smart_news_search,
    smart_news_search_sync,
)

# Re-export for backward compatibility
__all__ = [
    "NewsProvider",
    "NewsQuality",
    "NewsArticle",
    "NewsSearchResult",
    "ProviderQuota",
    "NewsRouter",
    "get_news_router",
    "smart_news_search",
    "smart_news_search_sync",
]


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    async def demo():
        router = get_news_router()

        # Test queries
        queries = [
            "Tesla earnings",
            "Apple iPhone",
        ]

        print("Testing NewsRouter...")
        for query in queries:
            print(f"\nSearching: '{query}'")
            result = await router.search(query, max_results=5, quality=NewsQuality.FREE)
            print(f"  Provider: {result.provider.value}")
            print(f"  Success: {result.success}")
            print(f"  Articles: {len(result.articles)}")
            for i, article in enumerate(result.articles[:3], 1):
                print(f"    {i}. {article.title[:60]}...")
                print(f"       Source: {article.source}")

        # Check quota status
        print("\nQuota Status:")
        for provider, status in router.get_quota_status().items():
            print(f"  {provider}: {status}")

    asyncio.run(demo())


# NOTE: Old implementation has been moved to the news/ package
# This file now serves as a backward-compatible entry point
# The actual implementation is in:
# - news/models.py: Data models
# - news/router.py: NewsRouter class
# - news/__init__.py: Package exports and convenience functions
