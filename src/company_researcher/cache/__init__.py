"""
Research Cache System.

Persistent storage for research data that:
- Stores all collected data by company
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
"""

from .data_completeness import (
    CompletenessChecker,
    CompletenessReport,
    DataSection,
    ResearchGap,
    SectionStatus,
)
from .models import CachedCompanyData, CachedSource, DataCompleteness, SourceQuality
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
]
