"""
Result Cache - Caching for function results and tool outputs.

Provides:
- Function result memoization
- Decorator-based caching
- Cache key generation
- Async support
"""

import asyncio
import functools
import hashlib
import inspect
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Generic, Optional, TypeVar
from ..utils import get_logger

logger = get_logger(__name__)


def _utcnow() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)

from .lru_cache import LRUCache, LRUCacheConfig
from .ttl_cache import TTLCache, TTLCacheConfig

T = TypeVar('T')


@dataclass
class CachedResult(Generic[T]):
    """Wrapper for cached results with metadata."""
    value: T
    cached_at: datetime
    cache_key: str
    hit: bool = True  # True if from cache, False if computed
    compute_time: Optional[float] = None  # Time to compute if not cached
    ttl_remaining: Optional[float] = None

    def is_stale(self, max_age: float) -> bool:
        """Check if result is older than max_age seconds."""
        age = (_utcnow() - self.cached_at).total_seconds()
        return age > max_age


class ResultCache(Generic[T]):
    """
    Cache for function/tool results.

    Usage:
        cache = ResultCache(ttl=300)

        # Cache a result
        cache.set("search:tesla", search_results)

        # Get cached result
        result = cache.get("search:tesla")

        # Get with metadata
        cached = cache.get_with_metadata("search:tesla")
        if cached and not cached.is_stale(60):
            use(cached.value)
    """

    def __init__(
        self,
        ttl: Optional[float] = None,
        max_size: int = 1000,
        use_ttl: bool = True
    ):
        self._use_ttl = use_ttl and ttl is not None
        self._ttl = ttl

        if self._use_ttl:
            self._cache: TTLCache = TTLCache(TTLCacheConfig(
                default_ttl=ttl or 300.0,
                max_size=max_size
            ))
        else:
            self._cache: LRUCache = LRUCache(LRUCacheConfig(
                max_size=max_size
            ))

        self._metadata: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """Get cached result."""
        return self._cache.get(key, default)

    def get_with_metadata(self, key: str) -> Optional[CachedResult[T]]:
        """Get cached result with metadata."""
        if self._use_ttl:
            value, ttl_remaining = self._cache.get_with_ttl(key)
        else:
            value = self._cache.get(key)
            ttl_remaining = None

        if value is not None:
            meta = self._metadata.get(key, {})
            return CachedResult(
                value=value,
                cached_at=meta.get("cached_at", _utcnow()),
                cache_key=key,
                hit=True,
                compute_time=meta.get("compute_time"),
                ttl_remaining=ttl_remaining
            )
        return None

    def set(
        self,
        key: str,
        value: T,
        ttl: Optional[float] = None,
        compute_time: Optional[float] = None
    ) -> None:
        """
        Cache a result.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Override TTL for this item
            compute_time: How long it took to compute
        """
        if self._use_ttl:
            self._cache.put(key, value, ttl=ttl)
        else:
            self._cache.put(key, value)

        self._metadata[key] = {
            "cached_at": _utcnow(),
            "compute_time": compute_time
        }

    def delete(self, key: str) -> bool:
        """Delete cached result."""
        self._metadata.pop(key, None)
        return self._cache.delete(key)

    def clear(self) -> None:
        """Clear all cached results."""
        self._cache.clear()
        self._metadata.clear()

    def __contains__(self, key: str) -> bool:
        """Check if key is cached."""
        return key in self._cache

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self._cache.get_stats()


def _make_cache_key(
    func: Callable,
    args: tuple,
    kwargs: dict,
    key_prefix: Optional[str] = None,
    exclude_args: Optional[list] = None
) -> str:
    """Generate cache key from function and arguments."""
    exclude_args = exclude_args or []

    # Get function signature
    sig = inspect.signature(func)
    params = list(sig.parameters.keys())

    # Build key parts
    key_parts = [key_prefix or func.__name__]

    # Add positional args
    for i, arg in enumerate(args):
        if i < len(params) and params[i] not in exclude_args:
            key_parts.append(f"{params[i]}={_serialize_arg(arg)}")

    # Add keyword args
    for key, value in sorted(kwargs.items()):
        if key not in exclude_args:
            key_parts.append(f"{key}={_serialize_arg(value)}")

    # Create hash for long keys
    key_str = ":".join(key_parts)
    if len(key_str) > 200:
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{key_prefix or func.__name__}:{key_hash}"

    return key_str


def _serialize_arg(arg: Any) -> str:
    """Serialize argument for cache key."""
    try:
        return json.dumps(arg, sort_keys=True, default=str)
    except Exception:
        return str(arg)


# Global cache for decorator
_global_cache: Optional[ResultCache] = None


def _get_global_cache() -> ResultCache:
    """Get or create global result cache."""
    global _global_cache
    if _global_cache is None:
        _global_cache = ResultCache(ttl=300.0, max_size=10000)
    return _global_cache


def cache_result(
    key: str,
    value: Any,
    ttl: Optional[float] = None
) -> None:
    """
    Cache a result with the global cache.

    Args:
        key: Cache key
        value: Value to cache
        ttl: Time-to-live in seconds
    """
    cache = _get_global_cache()
    cache.set(key, value, ttl=ttl)


def cached(
    ttl: Optional[float] = 300.0,
    key_prefix: Optional[str] = None,
    exclude_args: Optional[list] = None,
    cache: Optional[ResultCache] = None
):
    """
    Decorator to cache function results.

    Usage:
        @cached(ttl=60)
        def expensive_function(x, y):
            return x + y

        @cached(ttl=300, exclude_args=["callback"])
        async def async_function(query, callback=None):
            return await search(query)

    Args:
        ttl: Time-to-live in seconds
        key_prefix: Custom key prefix
        exclude_args: Arguments to exclude from cache key
        cache: Custom cache instance
    """
    def decorator(func: Callable) -> Callable:
        result_cache = cache or _get_global_cache()

        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                cache_key = _make_cache_key(
                    func, args, kwargs,
                    key_prefix=key_prefix,
                    exclude_args=exclude_args
                )

                # Check cache
                cached_result = result_cache.get_with_metadata(cache_key)
                if cached_result is not None:
                    return cached_result.value

                # Compute result
                start = time.time()
                result = await func(*args, **kwargs)
                compute_time = time.time() - start

                # Cache result
                result_cache.set(
                    cache_key,
                    result,
                    ttl=ttl,
                    compute_time=compute_time
                )

                return result

            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                cache_key = _make_cache_key(
                    func, args, kwargs,
                    key_prefix=key_prefix,
                    exclude_args=exclude_args
                )

                # Check cache
                cached_result = result_cache.get_with_metadata(cache_key)
                if cached_result is not None:
                    return cached_result.value

                # Compute result
                start = time.time()
                result = func(*args, **kwargs)
                compute_time = time.time() - start

                # Cache result
                result_cache.set(
                    cache_key,
                    result,
                    ttl=ttl,
                    compute_time=compute_time
                )

                return result

            return sync_wrapper

    return decorator
