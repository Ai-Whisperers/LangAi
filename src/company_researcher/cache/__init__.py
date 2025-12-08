"""
DEPRECATED: This cache module has been replaced by the comprehensive caching/ module.

Please update your imports to use the new module:

    # Old import (deprecated)
    from company_researcher.cache import ResearchCache

    # New import (recommended)
    from company_researcher.caching import ResearchResultCache, create_research_cache

The new caching module provides:
- In-memory LRU cache
- TTL-based expiration
- Redis distributed caching
- Query deduplication
- Vector store integration

This module will be removed in a future version.
"""

import warnings

warnings.warn(
    "company_researcher.cache is deprecated. Use company_researcher.caching instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from old module for backward compatibility
from .research_cache import ResearchCache, CacheStats, CacheEntry, create_cache

__all__ = ["ResearchCache", "CacheStats", "CacheEntry", "create_cache"]
