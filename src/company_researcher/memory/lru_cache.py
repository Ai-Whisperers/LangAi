"""
LRU Cache Implementation (Phase 11).

Hot memory layer with:
- LRU (Least Recently Used) eviction
- Configurable size limits
- Access tracking
- TTL (time-to-live) support
- Thread-safe operations

This is the fast-access layer for frequently used research data.
"""

import threading
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from ..utils import utc_now

# ============================================================================
# Data Models
# ============================================================================


@dataclass
class CacheEntry:
    """An entry in the LRU cache."""

    key: str
    value: Any
    created_at: datetime = field(default_factory=utc_now)
    last_accessed: datetime = field(default_factory=utc_now)
    access_count: int = 0
    ttl_seconds: Optional[int] = None

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl_seconds is None:
            return False
        return utc_now() > self.created_at + timedelta(seconds=self.ttl_seconds)

    def touch(self):
        """Update last access time and count."""
        self.last_accessed = utc_now()
        self.access_count += 1


class CacheStats:
    """Statistics for cache performance."""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expirations = 0
        self.total_gets = 0
        self.total_puts = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "expirations": self.expirations,
            "hit_rate": f"{self.hit_rate:.1f}%",
            "total_gets": self.total_gets,
            "total_puts": self.total_puts,
        }


# ============================================================================
# LRU Cache
# ============================================================================


class LRUCache:
    """
    Thread-safe LRU (Least Recently Used) cache.

    Features:
    - Configurable maximum size
    - Automatic LRU eviction
    - Optional TTL for entries
    - Access statistics
    - Thread-safe operations

    Usage:
        cache = LRUCache(max_size=100)
        cache.put("key", "value")
        value = cache.get("key")
    """

    def __init__(self, max_size: int = 100, default_ttl: Optional[int] = None):
        """
        Initialize LRU cache.

        Args:
            max_size: Maximum number of entries
            default_ttl: Default TTL in seconds (None = no expiration)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = CacheStats()

    @property
    def size(self) -> int:
        """Current number of entries."""
        return len(self._cache)

    @property
    def stats(self) -> CacheStats:
        """Get cache statistics."""
        return self._stats

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.

        Args:
            key: Cache key
            default: Value to return if not found

        Returns:
            Cached value or default
        """
        with self._lock:
            self._stats.total_gets += 1

            if key not in self._cache:
                self._stats.misses += 1
                return default

            entry = self._cache[key]

            # Check expiration
            if entry.is_expired():
                self._stats.expirations += 1
                self._stats.misses += 1
                del self._cache[key]
                return default

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            entry.touch()

            self._stats.hits += 1
            return entry.value

    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Put value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL override (uses default if None)
        """
        with self._lock:
            self._stats.total_puts += 1

            # Use provided TTL or default
            entry_ttl = ttl if ttl is not None else self.default_ttl

            # Update existing or create new
            if key in self._cache:
                self._cache.move_to_end(key)
                entry = self._cache[key]
                entry.value = value
                entry.last_accessed = utc_now()
            else:
                # Evict if at capacity
                while len(self._cache) >= self.max_size:
                    self._evict_oldest()

                self._cache[key] = CacheEntry(key=key, value=value, ttl_seconds=entry_ttl)

    def delete(self, key: str) -> bool:
        """
        Delete entry from cache.

        Args:
            key: Cache key

        Returns:
            True if entry was deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def contains(self, key: str) -> bool:
        """Check if key exists (without updating access time)."""
        with self._lock:
            if key not in self._cache:
                return False
            entry = self._cache[key]
            if entry.is_expired():
                del self._cache[key]
                return False
            return True

    def clear(self) -> int:
        """
        Clear all entries.

        Returns:
            Number of entries cleared
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count

    def keys(self) -> List[str]:
        """Get all keys (excluding expired)."""
        with self._lock:
            self._cleanup_expired()
            return list(self._cache.keys())

    def values(self) -> List[Any]:
        """Get all values (excluding expired)."""
        with self._lock:
            self._cleanup_expired()
            return [entry.value for entry in self._cache.values()]

    def items(self) -> List[Tuple[str, Any]]:
        """Get all key-value pairs (excluding expired)."""
        with self._lock:
            self._cleanup_expired()
            return [(k, v.value) for k, v in self._cache.items()]

    def get_entry(self, key: str) -> Optional[CacheEntry]:
        """Get full cache entry with metadata."""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired():
                    return entry
            return None

    def get_most_accessed(self, n: int = 10) -> List[Tuple[str, int]]:
        """Get n most accessed keys."""
        with self._lock:
            entries = [(k, v.access_count) for k, v in self._cache.items()]
            entries.sort(key=lambda x: x[1], reverse=True)
            return entries[:n]

    def _evict_oldest(self) -> Optional[str]:
        """Evict least recently used entry."""
        if not self._cache:
            return None

        # First, try to evict expired entries
        for key, entry in list(self._cache.items()):
            if entry.is_expired():
                del self._cache[key]
                self._stats.expirations += 1
                return key

        # Otherwise, evict LRU (first item)
        oldest_key = next(iter(self._cache))
        del self._cache[oldest_key]
        self._stats.evictions += 1
        return oldest_key

    def _cleanup_expired(self) -> int:
        """Remove all expired entries."""
        expired = []
        for key, entry in self._cache.items():
            if entry.is_expired():
                expired.append(key)

        for key in expired:
            del self._cache[key]
            self._stats.expirations += 1

        return len(expired)


# ============================================================================
# Typed LRU Cache
# ============================================================================


class TypedLRUCache:
    """
    Type-aware LRU cache with separate namespaces.

    Useful for caching different types of research data:
    - company_info
    - financial_data
    - market_data
    - search_results

    Usage:
        cache = TypedLRUCache()
        cache.put("company_info", "Tesla", data)
        cache.put("financial_data", "Tesla", financial)
        company = cache.get("company_info", "Tesla")
    """

    def __init__(self, max_size_per_type: int = 100, default_ttl: Optional[int] = None):
        """
        Initialize typed cache.

        Args:
            max_size_per_type: Max entries per type
            default_ttl: Default TTL in seconds
        """
        self._caches: Dict[str, LRUCache] = {}
        self._max_size = max_size_per_type
        self._default_ttl = default_ttl
        self._lock = threading.RLock()

    def _get_cache(self, type_name: str) -> LRUCache:
        """Get or create cache for type."""
        with self._lock:
            if type_name not in self._caches:
                self._caches[type_name] = LRUCache(
                    max_size=self._max_size, default_ttl=self._default_ttl
                )
            return self._caches[type_name]

    def get(self, type_name: str, key: str, default: Any = None) -> Any:
        """Get value from typed cache."""
        cache = self._get_cache(type_name)
        return cache.get(key, default)

    def get_any_type(self, key: str, default: Any = None) -> Any:
        """Get value from any type cache by key only.

        Searches all type caches for the key.

        Args:
            key: The key to search for
            default: Default value if not found

        Returns:
            The cached value if found, default otherwise
        """
        with self._lock:
            for cache in self._caches.values():
                result = cache.get(key)
                if result is not None:
                    return result
        return default

    def put(self, type_name: str, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Put value in typed cache."""
        cache = self._get_cache(type_name)
        cache.put(key, value, ttl)

    def delete(self, type_name: str, key: str) -> bool:
        """Delete from typed cache."""
        cache = self._get_cache(type_name)
        return cache.delete(key)

    def clear_type(self, type_name: str) -> int:
        """Clear all entries of a type."""
        if type_name in self._caches:
            return self._caches[type_name].clear()
        return 0

    def clear_all(self) -> int:
        """Clear all caches."""
        total = 0
        with self._lock:
            for cache in self._caches.values():
                total += cache.clear()
            self._caches.clear()
        return total

    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get stats for all type caches."""
        return {type_name: cache.stats.to_dict() for type_name, cache in self._caches.items()}

    @property
    def types(self) -> List[str]:
        """Get all cache types."""
        return list(self._caches.keys())


# ============================================================================
# Research-Specific Cache
# ============================================================================


class ResearchCache(TypedLRUCache):
    """
    Specialized cache for research data.

    Pre-configured types:
    - company: Company overview data
    - financial: Financial analysis
    - market: Market analysis
    - product: Product analysis
    - competitive: Competitive intelligence
    - search: Search results
    """

    CACHE_TYPES = ["company", "financial", "market", "product", "competitive", "search"]

    def __init__(self, max_size_per_type: int = 50, default_ttl: int = 3600):  # 1 hour default
        """Initialize research cache."""
        super().__init__(max_size_per_type, default_ttl)

        # Pre-initialize all cache types
        for cache_type in self.CACHE_TYPES:
            self._get_cache(cache_type)

    def cache_company(
        self, company_name: str, data: Dict[str, Any], ttl: Optional[int] = None
    ) -> None:
        """Cache company overview data."""
        self.put("company", company_name.lower(), data, ttl)

    def get_company(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Get cached company data."""
        return self.get("company", company_name.lower())

    def cache_financial(
        self, company_name: str, data: Dict[str, Any], ttl: Optional[int] = None
    ) -> None:
        """Cache financial analysis."""
        self.put("financial", company_name.lower(), data, ttl)

    def get_financial(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Get cached financial data."""
        return self.get("financial", company_name.lower())

    def cache_search_results(
        self, query: str, results: List[Dict[str, Any]], ttl: int = 1800  # 30 minutes
    ) -> None:
        """Cache search results."""
        self.put("search", query.lower(), results, ttl)

    def get_search_results(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached search results."""
        return self.get("search", query.lower())

    def has_recent_research(self, company_name: str, max_age_hours: int = 24) -> bool:
        """Check if recent research exists."""
        entry = self._get_cache("company").get_entry(company_name.lower())
        if entry is None:
            return False

        age = utc_now() - entry.created_at
        return age.total_seconds() < max_age_hours * 3600
