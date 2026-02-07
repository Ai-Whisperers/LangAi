"""
Research Cache System.

Persistent storage for research data that:
- Stores all collected data by company and topic
- Remembers useful and useless URLs
- Prevents redundant searches
- Tracks data freshness
- Enables incremental research

Usage:
    from company_researcher.cache import ResearchCache, get_cache

    cache = get_cache()

    # Check what we already have
    existing = cache.get_company_data("Apple Inc")
    gaps = cache.identify_gaps("Apple Inc")

    # After research, store results
    cache.store_search_results("Apple Inc", results, sources)
    cache.mark_url_useless(url, reason="paywall")

For runtime TTL caching of external calls (search/scrape/news/Wikipedia/SEC), use:
    from company_researcher.cache.result_cache import get_result_cache, cache_search, get_cached_search
"""

from .data_completeness import (
    CompletenessChecker,
    CompletenessReport,
    DataSection,
    ResearchGap,
    SectionStatus,
)
from .models import CachedCompanyData, CachedSource, DataCompleteness, SourceQuality
from .result_cache import (  # Runtime TTL result cache (canonical entry point)
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
from .storage import ResearchCache, create_cache, get_cache
from .url_registry import URLRecord, URLRegistry, URLStatus

__all__ = [
    # Main cache
    "ResearchCache",
    "CachedCompanyData",
    "CachedSource",
    "SourceQuality",
    "DataSection",
    "DataCompleteness",
    "get_cache",
    "create_cache",
    # URL registry
    "URLRegistry",
    "URLStatus",
    "URLRecord",
    # Completeness
    "CompletenessChecker",
    "SectionStatus",
    "ResearchGap",
    "CompletenessReport",
    # Runtime result cache (TTL)
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
