"""
TTL Cache - Time-To-Live based cache with automatic expiration.

Supports:
- Per-item TTL
- Default TTL
- Automatic cleanup
- Sliding expiration
"""

import asyncio
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Generic, Optional, TypeVar

K = TypeVar('K')
V = TypeVar('V')


@dataclass
class TTLCacheConfig:
    """Configuration for TTL cache."""
    default_ttl: float = 300.0  # seconds
    max_size: int = 10000
    cleanup_interval: float = 60.0  # seconds
    sliding_expiration: bool = False  # Reset TTL on access
    on_expire: Optional[Callable[[Any, Any], None]] = None


@dataclass
class TTLCacheItem(Generic[V]):
    """Cache item with TTL."""
    value: V
    created_at: float  # timestamp
    expires_at: float  # timestamp
    ttl: float  # original TTL
    access_count: int = 0
    last_accessed: float = 0  # timestamp


class TTLCache(Generic[K, V]):
    """
    Time-To-Live based cache with automatic expiration.

    Usage:
        cache = TTLCache(default_ttl=300)  # 5 minutes

        # Store with default TTL
        cache.put("key1", "value1")

        # Store with custom TTL
        cache.put("key2", "value2", ttl=60)  # 1 minute

        # Get value (returns None if expired)
        value = cache.get("key1")

        # Get with remaining TTL
        value, remaining = cache.get_with_ttl("key1")
    """

    def __init__(self, config: Optional[TTLCacheConfig] = None):
        self._config = config or TTLCacheConfig()
        self._cache: Dict[K, TTLCacheItem[V]] = {}
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        self._expirations = 0
        self._cleanup_task: Optional[asyncio.Task] = None

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """
        Get value from cache if not expired.

        Args:
            key: Cache key
            default: Default value if not found or expired

        Returns:
            Cached value or default
        """
        with self._lock:
            if key in self._cache:
                item = self._cache[key]
                now = time.time()

                if now < item.expires_at:
                    self._hits += 1
                    item.access_count += 1
                    item.last_accessed = now

                    # Sliding expiration - reset TTL on access
                    if self._config.sliding_expiration:
                        item.expires_at = now + item.ttl

                    return item.value
                else:
                    # Expired
                    self._expire_item(key, item)

            self._misses += 1
            return default

    def get_with_ttl(self, key: K) -> tuple[Optional[V], Optional[float]]:
        """
        Get value with remaining TTL.

        Returns:
            Tuple of (value, remaining_ttl) or (None, None) if not found
        """
        with self._lock:
            if key in self._cache:
                item = self._cache[key]
                now = time.time()

                if now < item.expires_at:
                    self._hits += 1
                    item.access_count += 1
                    item.last_accessed = now

                    if self._config.sliding_expiration:
                        item.expires_at = now + item.ttl

                    remaining = item.expires_at - now
                    return item.value, remaining
                else:
                    self._expire_item(key, item)

            self._misses += 1
            return None, None

    def put(self, key: K, value: V, ttl: Optional[float] = None) -> None:
        """
        Put value into cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        with self._lock:
            # Evict if at max size
            if len(self._cache) >= self._config.max_size:
                self._evict_expired()
                if len(self._cache) >= self._config.max_size:
                    self._evict_oldest()

            now = time.time()
            actual_ttl = ttl if ttl is not None else self._config.default_ttl

            item = TTLCacheItem(
                value=value,
                created_at=now,
                expires_at=now + actual_ttl,
                ttl=actual_ttl,
                access_count=1,
                last_accessed=now
            )
            self._cache[key] = item

    def delete(self, key: K) -> bool:
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Clear all items from cache."""
        with self._lock:
            self._cache.clear()

    def refresh(self, key: K, ttl: Optional[float] = None) -> bool:
        """
        Refresh TTL for a key.

        Args:
            key: Cache key
            ttl: New TTL (uses original if not specified)

        Returns:
            True if refreshed, False if key not found
        """
        with self._lock:
            if key in self._cache:
                item = self._cache[key]
                now = time.time()

                if now < item.expires_at:
                    new_ttl = ttl if ttl is not None else item.ttl
                    item.expires_at = now + new_ttl
                    item.ttl = new_ttl
                    return True

            return False

    def __contains__(self, key: K) -> bool:
        """Check if key exists and is not expired."""
        with self._lock:
            if key in self._cache:
                item = self._cache[key]
                if time.time() < item.expires_at:
                    return True
                self._expire_item(key, item)
            return False

    def __len__(self) -> int:
        """Get number of non-expired items."""
        with self._lock:
            self._evict_expired()
            return len(self._cache)

    def _expire_item(self, key: K, item: TTLCacheItem) -> None:
        """Handle item expiration."""
        del self._cache[key]
        self._expirations += 1

        if self._config.on_expire:
            try:
                self._config.on_expire(key, item.value)
            except Exception:
                pass

    def _evict_expired(self) -> int:
        """Remove all expired items."""
        now = time.time()
        expired_keys = [
            k for k, v in self._cache.items()
            if v.expires_at <= now
        ]

        for key in expired_keys:
            item = self._cache[key]
            self._expire_item(key, item)

        return len(expired_keys)

    def _evict_oldest(self) -> None:
        """Evict the oldest item."""
        if not self._cache:
            return

        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].created_at
        )
        item = self._cache.pop(oldest_key)
        self._expirations += 1

    def cleanup(self) -> int:
        """
        Manual cleanup of expired items.

        Returns:
            Number of items removed
        """
        with self._lock:
            return self._evict_expired()

    async def start_cleanup_task(self) -> None:
        """Start automatic cleanup background task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop_cleanup_task(self) -> None:
        """Stop automatic cleanup background task."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while True:
            try:
                await asyncio.sleep(self._config.cleanup_interval)
                self.cleanup()
            except asyncio.CancelledError:
                break
            except Exception:
                pass

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            # Get TTL distribution
            now = time.time()
            ttl_values = [
                item.expires_at - now
                for item in self._cache.values()
                if item.expires_at > now
            ]

            return {
                "size": len(self._cache),
                "max_size": self._config.max_size,
                "default_ttl": self._config.default_ttl,
                "hits": self._hits,
                "misses": self._misses,
                "expirations": self._expirations,
                "hit_rate": hit_rate,
                "min_remaining_ttl": min(ttl_values) if ttl_values else None,
                "max_remaining_ttl": max(ttl_values) if ttl_values else None,
                "avg_remaining_ttl": sum(ttl_values) / len(ttl_values) if ttl_values else None
            }

    def get_keys(self) -> list:
        """Get all non-expired keys."""
        with self._lock:
            now = time.time()
            return [
                k for k, v in self._cache.items()
                if v.expires_at > now
            ]


def create_ttl_cache(
    default_ttl: float = 300.0,
    max_size: int = 10000,
    sliding_expiration: bool = False,
    cleanup_interval: float = 60.0,
    on_expire: Optional[Callable] = None
) -> TTLCache:
    """
    Factory function to create TTL cache.

    Args:
        default_ttl: Default time-to-live in seconds
        max_size: Maximum number of items
        sliding_expiration: Reset TTL on access
        cleanup_interval: Interval for automatic cleanup
        on_expire: Callback when items expire

    Returns:
        Configured TTLCache instance
    """
    config = TTLCacheConfig(
        default_ttl=default_ttl,
        max_size=max_size,
        sliding_expiration=sliding_expiration,
        cleanup_interval=cleanup_interval,
        on_expire=on_expire
    )
    return TTLCache(config)
