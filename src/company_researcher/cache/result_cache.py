"""
Canonical runtime result cache API.

This module consolidates the file-based TTL cache that historically lived under
`company_researcher.integrations.result_cache`.

Use this module for caching search/scrape/news/Wikipedia/SEC results.
"""

from __future__ import annotations

# Re-export integration cache for backward compatibility while centralizing imports.
from ..integrations.result_cache import (  # noqa: F401
    CacheEntry,
    ResultCache,
    cache_classification,
    cache_financial,
    cache_news,
    cache_scrape,
    cache_search,
    cache_sec_filing,
    cache_wikipedia,
    get_cached_classification,
    get_cached_financial,
    get_cached_news,
    get_cached_scrape,
    get_cached_search,
    get_cached_sec_filing,
    get_cached_wikipedia,
    get_result_cache,
)

__all__ = [
    "CacheEntry",
    "ResultCache",
    "get_result_cache",
    "cache_search",
    "get_cached_search",
    "cache_scrape",
    "get_cached_scrape",
    "cache_news",
    "get_cached_news",
    "cache_wikipedia",
    "get_cached_wikipedia",
    "cache_sec_filing",
    "get_cached_sec_filing",
    "cache_classification",
    "get_cached_classification",
    "cache_financial",
    "get_cached_financial",
]
