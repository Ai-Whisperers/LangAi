"""
Caching Module for Company Researcher.

Provides comprehensive caching strategies:
- In-memory LRU cache
- TTL-based expiration
- Redis distributed caching
- Result and response caching
- Cache invalidation patterns
- Query deduplication
"""

from .cache_manager import CacheConfig, CacheEntry, CacheManager, CacheStats, create_cache_manager
from .lru_cache import LRUCache, LRUCacheConfig, create_lru_cache
from .query_dedup import (
    CompanyNameNormalizer,
    DeduplicationStrategy,
    NormalizedQuery,
    PendingQuery,
    QueryDeduplicationStats,
    QueryDeduplicator,
    RequestCoalescer,
    create_deduplicator,
    normalize_company_name,
)
from .redis_cache import RedisCache, RedisCacheConfig, create_redis_cache
from .research_cache import (
    CacheWarmer,
    NewsBasedInvalidator,
    ResearchCacheEntry,
    ResearchCacheStats,
    ResearchCacheStatus,
    ResearchResultCache,
    create_research_cache,
)
from .result_cache import CachedResult, ResultCache, cache_result, cached
from .token_cache import TokenCache, TokenUsage, track_tokens
from .ttl_cache import TTLCache, TTLCacheConfig, create_ttl_cache
from .vector_store import (
    CHROMADB_AVAILABLE,
    ResearchVectorStore,
    SearchResult,
    get_vector_store,
    reset_vector_store,
)

__all__ = [
    # Cache Manager
    "CacheManager",
    "CacheConfig",
    "CacheStats",
    "CacheEntry",
    "create_cache_manager",
    # LRU Cache
    "LRUCache",
    "LRUCacheConfig",
    "create_lru_cache",
    # TTL Cache
    "TTLCache",
    "TTLCacheConfig",
    "create_ttl_cache",
    # Redis Cache
    "RedisCache",
    "RedisCacheConfig",
    "create_redis_cache",
    # Result Cache
    "ResultCache",
    "CachedResult",
    "cache_result",
    "cached",
    # Token Cache
    "TokenCache",
    "TokenUsage",
    "track_tokens",
    # Research Cache
    "ResearchResultCache",
    "ResearchCacheEntry",
    "ResearchCacheStatus",
    "ResearchCacheStats",
    "CacheWarmer",
    "NewsBasedInvalidator",
    "create_research_cache",
    # Query Deduplication
    "QueryDeduplicator",
    "NormalizedQuery",
    "PendingQuery",
    "QueryDeduplicationStats",
    "DeduplicationStrategy",
    "RequestCoalescer",
    "CompanyNameNormalizer",
    "create_deduplicator",
    "normalize_company_name",
    # Vector Store
    "ResearchVectorStore",
    "SearchResult",
    "get_vector_store",
    "reset_vector_store",
    "CHROMADB_AVAILABLE",
]
