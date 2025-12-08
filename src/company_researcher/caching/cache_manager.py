"""
Cache Manager - Central cache management and coordination.

Provides:
- Multi-tier caching (memory -> Redis)
- Cache invalidation patterns
- Unified cache interface
- Cache statistics aggregation
"""

import asyncio
import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union

from .lru_cache import LRUCache, LRUCacheConfig
from .ttl_cache import TTLCache, TTLCacheConfig
from .redis_cache import RedisCache, RedisCacheConfig

K = TypeVar('K')
V = TypeVar('V')


class CacheTier(str, Enum):
    """Cache tiers for multi-level caching."""
    MEMORY = "memory"      # Fast, local memory
    REDIS = "redis"        # Distributed, persistent
    ALL = "all"            # Both tiers


class InvalidationStrategy(str, Enum):
    """Cache invalidation strategies."""
    IMMEDIATE = "immediate"   # Invalidate immediately
    LAZY = "lazy"             # Mark as stale, invalidate on access
    TTL = "ttl"               # Let TTL handle expiration
    BROADCAST = "broadcast"   # Broadcast invalidation to all caches


@dataclass
class CacheConfig:
    """Configuration for cache manager."""
    # Memory cache settings
    memory_max_size: int = 10000
    memory_ttl: float = 300.0  # seconds

    # Redis settings (optional)
    redis_enabled: bool = False
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_prefix: str = "company_researcher:"
    redis_ttl: int = 3600  # seconds

    # Multi-tier settings
    write_through: bool = True   # Write to all tiers
    read_through: bool = True    # Read from memory first, then Redis

    # Invalidation settings
    invalidation_strategy: InvalidationStrategy = InvalidationStrategy.IMMEDIATE


@dataclass
class CacheEntry(Generic[V]):
    """Cache entry with metadata."""
    key: str
    value: V
    tier: CacheTier
    created_at: datetime = field(default_factory=datetime.utcnow)
    accessed_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    ttl: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    stale: bool = False


@dataclass
class CacheStats:
    """Aggregated cache statistics."""
    memory_hits: int = 0
    memory_misses: int = 0
    redis_hits: int = 0
    redis_misses: int = 0
    total_requests: int = 0

    # Size info
    memory_size: int = 0
    memory_size_bytes: int = 0

    # Performance
    avg_read_time_ms: float = 0.0
    avg_write_time_ms: float = 0.0

    @property
    def total_hits(self) -> int:
        return self.memory_hits + self.redis_hits

    @property
    def total_misses(self) -> int:
        return self.memory_misses + self.redis_misses

    @property
    def hit_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.total_hits / self.total_requests

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_hits": self.memory_hits,
            "memory_misses": self.memory_misses,
            "redis_hits": self.redis_hits,
            "redis_misses": self.redis_misses,
            "total_hits": self.total_hits,
            "total_misses": self.total_misses,
            "total_requests": self.total_requests,
            "hit_rate": self.hit_rate,
            "memory_size": self.memory_size,
            "memory_size_bytes": self.memory_size_bytes,
            "avg_read_time_ms": self.avg_read_time_ms,
            "avg_write_time_ms": self.avg_write_time_ms
        }


class CacheManager(Generic[K, V]):
    """
    Central cache manager with multi-tier support.

    Usage:
        manager = CacheManager(CacheConfig(redis_enabled=True))
        await manager.connect()

        # Basic operations
        await manager.put("key1", {"data": "value"})
        value = await manager.get("key1")

        # With tags for group invalidation
        await manager.put("user:123", user_data, tags=["users", "active"])
        await manager.invalidate_by_tag("users")

        # Get stats
        stats = manager.get_stats()
    """

    def __init__(self, config: Optional[CacheConfig] = None):
        self._config = config or CacheConfig()

        # Memory cache (always enabled)
        self._memory_cache = TTLCache[K, CacheEntry[V]](TTLCacheConfig(
            default_ttl=self._config.memory_ttl,
            max_size=self._config.memory_max_size
        ))

        # Redis cache (optional)
        self._redis_cache: Optional[RedisCache] = None
        if self._config.redis_enabled:
            self._redis_cache = RedisCache(RedisCacheConfig(
                host=self._config.redis_host,
                port=self._config.redis_port,
                db=self._config.redis_db,
                password=self._config.redis_password,
                prefix=self._config.redis_prefix,
                default_ttl=self._config.redis_ttl
            ))

        # Tag index for group invalidation
        self._tag_index: Dict[str, set] = {}

        # Statistics
        self._stats = CacheStats()
        self._read_times: List[float] = []
        self._write_times: List[float] = []

    async def connect(self) -> bool:
        """Connect to external caches (Redis)."""
        if self._redis_cache:
            return await self._redis_cache.connect()
        return True

    async def disconnect(self) -> None:
        """Disconnect from external caches."""
        if self._redis_cache:
            await self._redis_cache.disconnect()

    async def get(
        self,
        key: K,
        default: Optional[V] = None,
        tier: CacheTier = CacheTier.ALL
    ) -> Optional[V]:
        """
        Get value from cache.

        Args:
            key: Cache key
            default: Default if not found
            tier: Which tier(s) to check

        Returns:
            Cached value or default
        """
        start = time.time()
        self._stats.total_requests += 1

        # Check memory cache first
        if tier in (CacheTier.MEMORY, CacheTier.ALL):
            entry = self._memory_cache.get(key)
            if entry and not entry.stale:
                self._stats.memory_hits += 1
                entry.accessed_at = datetime.utcnow()
                entry.access_count += 1
                self._record_read_time(start)
                return entry.value

            self._stats.memory_misses += 1

        # Check Redis if enabled and read-through
        if self._redis_cache and tier in (CacheTier.REDIS, CacheTier.ALL):
            if self._config.read_through or tier == CacheTier.REDIS:
                value = await self._redis_cache.get(key)
                if value is not None:
                    self._stats.redis_hits += 1

                    # Populate memory cache
                    if self._config.read_through and tier == CacheTier.ALL:
                        entry = CacheEntry(
                            key=str(key),
                            value=value,
                            tier=CacheTier.REDIS
                        )
                        self._memory_cache.put(key, entry)

                    self._record_read_time(start)
                    return value

                self._stats.redis_misses += 1

        self._record_read_time(start)
        return default

    async def put(
        self,
        key: K,
        value: V,
        ttl: Optional[float] = None,
        tags: Optional[List[str]] = None,
        tier: CacheTier = CacheTier.ALL
    ) -> bool:
        """
        Put value into cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            tags: Tags for group invalidation
            tier: Which tier(s) to write to

        Returns:
            True if successful
        """
        start = time.time()
        tags = tags or []

        # Create entry
        entry = CacheEntry(
            key=str(key),
            value=value,
            tier=tier,
            ttl=ttl,
            tags=tags
        )

        success = True

        # Write to memory cache
        if tier in (CacheTier.MEMORY, CacheTier.ALL):
            self._memory_cache.put(key, entry, ttl=ttl)

            # Update tag index
            for tag in tags:
                if tag not in self._tag_index:
                    self._tag_index[tag] = set()
                self._tag_index[tag].add(key)

        # Write to Redis if enabled
        if self._redis_cache and tier in (CacheTier.REDIS, CacheTier.ALL):
            if self._config.write_through or tier == CacheTier.REDIS:
                redis_ttl = int(ttl) if ttl else None
                success = await self._redis_cache.put(key, value, ttl=redis_ttl)

        self._record_write_time(start)
        self._stats.memory_size = len(self._memory_cache)

        return success

    async def delete(self, key: K, tier: CacheTier = CacheTier.ALL) -> bool:
        """Delete key from cache."""
        success = True

        # Delete from memory
        if tier in (CacheTier.MEMORY, CacheTier.ALL):
            # Remove from tag index
            entry = self._memory_cache.get(key)
            if entry:
                for tag in entry.tags:
                    if tag in self._tag_index:
                        self._tag_index[tag].discard(key)

            self._memory_cache.delete(key)

        # Delete from Redis
        if self._redis_cache and tier in (CacheTier.REDIS, CacheTier.ALL):
            success = await self._redis_cache.delete(key)

        return success

    async def invalidate_by_tag(self, tag: str) -> int:
        """
        Invalidate all entries with a specific tag.

        Returns:
            Number of entries invalidated
        """
        if tag not in self._tag_index:
            return 0

        keys = list(self._tag_index[tag])
        count = 0

        for key in keys:
            if self._config.invalidation_strategy == InvalidationStrategy.IMMEDIATE:
                await self.delete(key)
                count += 1
            elif self._config.invalidation_strategy == InvalidationStrategy.LAZY:
                entry = self._memory_cache.get(key)
                if entry:
                    entry.stale = True
                    count += 1

        # Clear tag index entry
        del self._tag_index[tag]

        return count

    async def invalidate_by_pattern(self, pattern: str) -> int:
        """
        Invalidate all entries matching a pattern.

        Args:
            pattern: Key pattern (supports * wildcard)

        Returns:
            Number of entries invalidated
        """
        count = 0

        # Memory cache
        import fnmatch
        keys_to_delete = [
            k for k in self._memory_cache.get_keys()
            if fnmatch.fnmatch(str(k), pattern)
        ]

        for key in keys_to_delete:
            self._memory_cache.delete(key)
            count += 1

        # Redis cache
        if self._redis_cache:
            redis_count = await self._redis_cache.clear_prefix(pattern.replace("*", ""))
            count += redis_count

        return count

    async def clear(self, tier: CacheTier = CacheTier.ALL) -> None:
        """Clear all cache entries."""
        if tier in (CacheTier.MEMORY, CacheTier.ALL):
            self._memory_cache.clear()
            self._tag_index.clear()

        if self._redis_cache and tier in (CacheTier.REDIS, CacheTier.ALL):
            await self._redis_cache.clear_prefix("")

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        # Update memory stats
        memory_stats = self._memory_cache.get_stats()
        self._stats.memory_size = memory_stats.get("size", 0)

        # Calculate average times
        if self._read_times:
            self._stats.avg_read_time_ms = sum(self._read_times) / len(self._read_times) * 1000
        if self._write_times:
            self._stats.avg_write_time_ms = sum(self._write_times) / len(self._write_times) * 1000

        return self._stats

    def _record_read_time(self, start: float) -> None:
        """Record read operation time."""
        self._read_times.append(time.time() - start)
        if len(self._read_times) > 1000:
            self._read_times = self._read_times[-100:]

    def _record_write_time(self, start: float) -> None:
        """Record write operation time."""
        self._write_times.append(time.time() - start)
        if len(self._write_times) > 1000:
            self._write_times = self._write_times[-100:]

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


def create_cache_manager(
    memory_max_size: int = 10000,
    memory_ttl: float = 300.0,
    redis_enabled: bool = False,
    redis_host: str = "localhost",
    redis_port: int = 6379,
    **kwargs
) -> CacheManager:
    """
    Factory function to create cache manager.

    Args:
        memory_max_size: Maximum memory cache size
        memory_ttl: Default memory TTL
        redis_enabled: Enable Redis tier
        redis_host: Redis host
        redis_port: Redis port
        **kwargs: Additional config options

    Returns:
        Configured CacheManager instance
    """
    config = CacheConfig(
        memory_max_size=memory_max_size,
        memory_ttl=memory_ttl,
        redis_enabled=redis_enabled,
        redis_host=redis_host,
        redis_port=redis_port,
        **kwargs
    )
    return CacheManager(config)
