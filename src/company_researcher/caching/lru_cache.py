"""
LRU Cache - Least Recently Used cache implementation.

Thread-safe LRU cache with configurable size limits.
"""

import json
import threading
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Generic, Optional, TypeVar

from ..utils import get_logger

logger = get_logger(__name__)


def _utcnow() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


K = TypeVar("K")
V = TypeVar("V")


@dataclass
class LRUCacheConfig:
    """Configuration for LRU cache."""

    max_size: int = 1000
    max_memory_mb: Optional[float] = None  # Optional memory limit
    on_evict: Optional[Callable[[Any, Any], None]] = None  # Callback when item evicted


@dataclass
class CacheItem(Generic[V]):
    """Item stored in cache with metadata."""

    value: V
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    size_bytes: int = 0


class LRUCache(Generic[K, V]):
    """
    Thread-safe Least Recently Used cache.

    Usage:
        cache = LRUCache(max_size=1000)

        # Store and retrieve
        cache.put("key1", {"data": "value"})
        value = cache.get("key1")

        # Check existence
        if "key1" in cache:
            print("Found!")

        # Get with default
        value = cache.get("missing", default="default_value")
    """

    def __init__(self, config: Optional[LRUCacheConfig] = None):
        self._config = config or LRUCacheConfig()
        self._cache: OrderedDict[K, CacheItem[V]] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._total_size_bytes = 0

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """
        Get value from cache.

        Args:
            key: Cache key
            default: Default value if not found

        Returns:
            Cached value or default
        """
        with self._lock:
            if key in self._cache:
                self._hits += 1
                item = self._cache[key]
                item.last_accessed = _utcnow()
                item.access_count += 1
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                return item.value
            else:
                self._misses += 1
                return default

    def put(self, key: K, value: V) -> None:
        """
        Put value into cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        with self._lock:
            # Estimate size
            size_bytes = self._estimate_size(value)

            # Remove existing if present
            if key in self._cache:
                old_item = self._cache.pop(key)
                self._total_size_bytes -= old_item.size_bytes

            # Evict if needed
            self._evict_if_needed(size_bytes)

            # Add new item
            now = _utcnow()
            item = CacheItem(
                value=value,
                created_at=now,
                last_accessed=now,
                access_count=1,
                size_bytes=size_bytes,
            )
            self._cache[key] = item
            self._total_size_bytes += size_bytes

    def delete(self, key: K) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                item = self._cache.pop(key)
                self._total_size_bytes -= item.size_bytes
                return True
            return False

    def clear(self) -> None:
        """Clear all items from cache."""
        with self._lock:
            self._cache.clear()
            self._total_size_bytes = 0

    def __contains__(self, key: K) -> bool:
        """Check if key exists in cache."""
        with self._lock:
            return key in self._cache

    def __len__(self) -> int:
        """Get number of items in cache."""
        with self._lock:
            return len(self._cache)

    def _evict_if_needed(self, incoming_size: int = 0) -> None:
        """Evict items if cache is full."""
        # Check size limit
        while len(self._cache) >= self._config.max_size:
            self._evict_oldest()

        # Check memory limit if configured
        if self._config.max_memory_mb:
            max_bytes = self._config.max_memory_mb * 1024 * 1024
            while self._total_size_bytes + incoming_size > max_bytes and self._cache:
                self._evict_oldest()

    def _evict_oldest(self) -> None:
        """Evict the oldest (least recently used) item."""
        if self._cache:
            key, item = self._cache.popitem(last=False)
            self._total_size_bytes -= item.size_bytes
            self._evictions += 1

            # Call eviction callback if configured
            if self._config.on_evict:
                try:
                    self._config.on_evict(key, item.value)
                except Exception as e:
                    logger.warning(f"LRU cache eviction callback error for key {key}: {e}")

    def _estimate_size(self, value: Any) -> int:
        """Estimate memory size of value in bytes."""
        try:
            # Try JSON serialization for size estimate
            return len(json.dumps(value, default=str).encode("utf-8"))
        except Exception as e:
            # Fallback to string representation
            logger.debug(f"JSON size estimation failed, using string fallback: {e}")
            return len(str(value).encode("utf-8"))

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            return {
                "size": len(self._cache),
                "max_size": self._config.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "hit_rate": hit_rate,
                "total_size_bytes": self._total_size_bytes,
                "total_size_mb": self._total_size_bytes / (1024 * 1024),
            }

    def get_keys(self) -> list:
        """Get all cache keys."""
        with self._lock:
            return list(self._cache.keys())

    def get_item_info(self, key: K) -> Optional[Dict[str, Any]]:
        """Get metadata about a cached item."""
        with self._lock:
            if key in self._cache:
                item = self._cache[key]
                return {
                    "created_at": item.created_at.isoformat(),
                    "last_accessed": item.last_accessed.isoformat(),
                    "access_count": item.access_count,
                    "size_bytes": item.size_bytes,
                }
            return None


def create_lru_cache(
    max_size: int = 1000, max_memory_mb: Optional[float] = None, on_evict: Optional[Callable] = None
) -> LRUCache:
    """
    Factory function to create LRU cache.

    Args:
        max_size: Maximum number of items
        max_memory_mb: Optional memory limit in MB
        on_evict: Optional callback when items are evicted

    Returns:
        Configured LRUCache instance
    """
    config = LRUCacheConfig(max_size=max_size, max_memory_mb=max_memory_mb, on_evict=on_evict)
    return LRUCache(config)
