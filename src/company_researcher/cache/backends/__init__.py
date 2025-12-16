"""
Canonical cache backends.

This is the preferred import surface for low-level caching primitives (TTL/LRU/Redis/etc.).

These implementations currently live under `company_researcher.caching` but are re-exported
here so the rest of the codebase can standardize on `company_researcher.cache.*`.
"""

from __future__ import annotations

from ...caching import (  # noqa: F401
    CacheConfig,
    CacheEntry,
    CacheManager,
    CacheStats,
    CacheTier,
    InvalidationStrategy,
    LRUCache,
    LRUCacheConfig,
    RedisCache,
    RedisCacheConfig,
    TTLCache,
    TTLCacheConfig,
    create_cache_manager,
    create_lru_cache,
    create_redis_cache,
    create_ttl_cache,
)

__all__ = [
    "CacheTier",
    "InvalidationStrategy",
    "CacheConfig",
    "CacheEntry",
    "CacheStats",
    "CacheManager",
    "create_cache_manager",
    "TTLCache",
    "TTLCacheConfig",
    "create_ttl_cache",
    "LRUCache",
    "LRUCacheConfig",
    "create_lru_cache",
    "RedisCache",
    "RedisCacheConfig",
    "create_redis_cache",
]
