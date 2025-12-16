"""
Result Cache - File-based caching for search and scraping results.

Reduces API costs by caching:
- Search results by query (24h TTL)
- Scraped content by URL (7d TTL)
- Company classification (30d TTL)
- Financial data by ticker (1h TTL)

Usage:
    from company_researcher.integrations.result_cache import (
        get_result_cache,
        cache_search,
        cache_scrape,
        get_cached_search,
        get_cached_scrape
    )

    # Cache search results
    cache_search("Tesla news", results)

    # Get cached results (returns None if expired/missing)
    cached = get_cached_search("Tesla news")

    # Manual cache management
    cache = get_result_cache()
    cache.set("custom_key", data, ttl_hours=12)
"""

import gzip
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

from ..utils import get_config, get_logger, utc_now

logger = get_logger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    key: str
    data: Any
    created_at: str
    expires_at: str
    cache_type: str
    hit_count: int = 0
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if entry is expired."""
        expires = datetime.fromisoformat(self.expires_at)
        return utc_now() > expires

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CacheEntry":
        return cls(**data)


class ResultCache:
    """
    File-based result cache with TTL support.

    Features:
    - Type-specific TTLs (search, scrape, classification, financial)
    - Compressed storage for large results
    - Automatic cleanup of expired entries
    - Thread-safe operations
    - Cache statistics
    """

    # Default TTLs in hours
    DEFAULT_TTLS = {
        "search": 24,  # Search results: 24 hours
        "scrape": 168,  # Scraped content: 7 days
        "classification": 720,  # Company classification: 30 days
        "financial": 1,  # Financial data: 1 hour (real-time)
        "news": 6,  # News results: 6 hours
        "wikipedia": 720,  # Wikipedia: 30 days
        "sec_filing": 720,  # SEC filings: 30 days (rarely change)
        "default": 24,  # Default: 24 hours
    }

    def __init__(
        self, cache_dir: Optional[str] = None, compress: bool = True, max_size_mb: int = 500
    ):
        """
        Initialize result cache.

        Args:
            cache_dir: Directory for cache files (default: .research_cache)
            compress: Whether to compress cached data
            max_size_mb: Maximum cache size in MB
        """
        self.cache_dir = Path(
            cache_dir or get_config("RESEARCH_CACHE_DIR", default=".research_cache")
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.compress = compress
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self._lock = Lock()
        self._stats = {"hits": 0, "misses": 0, "writes": 0, "expired": 0}

        logger.info(f"Result cache initialized: {self.cache_dir}")

    def _hash_key(self, key: str) -> str:
        """Create hash from key for filename."""
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def _get_path(self, key_hash: str, cache_type: str) -> Path:
        """Get file path for cache entry."""
        type_dir = self.cache_dir / cache_type
        type_dir.mkdir(exist_ok=True)
        suffix = ".json.gz" if self.compress else ".json"
        return type_dir / f"{key_hash}{suffix}"

    def get(self, key: str, cache_type: str = "default") -> Optional[Any]:
        """
        Get cached value.

        Args:
            key: Cache key
            cache_type: Type of cache (search, scrape, etc.)

        Returns:
            Cached data or None if not found/expired
        """
        key_hash = self._hash_key(key)
        path = self._get_path(key_hash, cache_type)

        if not path.exists():
            self._stats["misses"] += 1
            return None

        try:
            with self._lock:
                if self.compress:
                    with gzip.open(path, "rt", encoding="utf-8") as f:
                        entry_data = json.load(f)
                else:
                    with open(path, "r", encoding="utf-8") as f:
                        entry_data = json.load(f)

                entry = CacheEntry.from_dict(entry_data)

                if entry.is_expired():
                    self._stats["expired"] += 1
                    path.unlink()
                    return None

                # Update hit count
                entry.hit_count += 1
                self._write_entry(path, entry)

                self._stats["hits"] += 1
                logger.debug(f"Cache hit: {cache_type}/{key_hash}")
                return entry.data

        except (json.JSONDecodeError, KeyError, gzip.BadGzipFile) as e:
            logger.warning(f"Cache read error: {e}")
            self._stats["misses"] += 1
            return None

    def set(
        self, key: str, data: Any, cache_type: str = "default", ttl_hours: Optional[int] = None
    ) -> bool:
        """
        Set cached value.

        Args:
            key: Cache key
            data: Data to cache
            cache_type: Type of cache
            ttl_hours: Custom TTL in hours (uses default if None)

        Returns:
            True if cached successfully
        """
        if ttl_hours is None:
            ttl_hours = self.DEFAULT_TTLS.get(cache_type, self.DEFAULT_TTLS["default"])

        key_hash = self._hash_key(key)
        path = self._get_path(key_hash, cache_type)

        now = utc_now()
        expires = now + timedelta(hours=ttl_hours)

        entry = CacheEntry(
            key=key[:100],  # Truncate key for readability
            data=data,
            created_at=now.isoformat(),
            expires_at=expires.isoformat(),
            cache_type=cache_type,
            hit_count=0,
            size_bytes=0,
        )

        try:
            with self._lock:
                self._write_entry(path, entry)
                self._stats["writes"] += 1
                logger.debug(f"Cache write: {cache_type}/{key_hash}")
                return True

        except (IOError, OSError) as e:
            logger.warning(f"Cache write error: {e}")
            return False

    def _write_entry(self, path: Path, entry: CacheEntry) -> None:
        """Write entry to file."""
        data = entry.to_dict()

        if self.compress:
            with gzip.open(path, "wt", encoding="utf-8") as f:
                json.dump(data, f)
        else:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

        entry.size_bytes = path.stat().st_size

    def delete(self, key: str, cache_type: str = "default") -> bool:
        """Delete cached entry."""
        key_hash = self._hash_key(key)
        path = self._get_path(key_hash, cache_type)

        if path.exists():
            with self._lock:
                path.unlink()
            return True
        return False

    def clear_type(self, cache_type: str) -> int:
        """Clear all entries of a specific type."""
        type_dir = self.cache_dir / cache_type
        if not type_dir.exists():
            return 0

        count = 0
        with self._lock:
            for path in type_dir.glob("*"):
                if path.is_file():
                    path.unlink()
                    count += 1
        return count

    def clear_all(self) -> int:
        """Clear entire cache."""
        count = 0
        with self._lock:
            for type_dir in self.cache_dir.iterdir():
                if type_dir.is_dir():
                    for path in type_dir.glob("*"):
                        if path.is_file():
                            path.unlink()
                            count += 1
        return count

    def cleanup_expired(self) -> int:
        """Remove all expired entries."""
        count = 0
        with self._lock:
            for type_dir in self.cache_dir.iterdir():
                if type_dir.is_dir():
                    for path in type_dir.glob("*"):
                        if path.is_file():
                            try:
                                if self.compress:
                                    with gzip.open(path, "rt", encoding="utf-8") as f:
                                        entry_data = json.load(f)
                                else:
                                    with open(path, "r", encoding="utf-8") as f:
                                        entry_data = json.load(f)

                                entry = CacheEntry.from_dict(entry_data)
                                if entry.is_expired():
                                    path.unlink()
                                    count += 1
                            except Exception as e:
                                logger.debug(f"Failed to clean cache file {path}: {e}")
        return count

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        # Count files and size
        total_files = 0
        total_size = 0
        by_type = {}

        for type_dir in self.cache_dir.iterdir():
            if type_dir.is_dir():
                type_name = type_dir.name
                type_files = 0
                type_size = 0

                for path in type_dir.glob("*"):
                    if path.is_file():
                        type_files += 1
                        type_size += path.stat().st_size

                by_type[type_name] = {
                    "files": type_files,
                    "size_mb": round(type_size / 1024 / 1024, 2),
                }
                total_files += type_files
                total_size += type_size

        return {
            "total_files": total_files,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "by_type": by_type,
            "hit_rate": self._stats["hits"] / max(self._stats["hits"] + self._stats["misses"], 1),
            **self._stats,
        }


# Singleton instance
_result_cache: Optional[ResultCache] = None
_cache_lock = Lock()


def get_result_cache() -> ResultCache:
    """Get singleton cache instance."""
    global _result_cache
    if _result_cache is None:
        with _cache_lock:
            if _result_cache is None:
                _result_cache = ResultCache()
    return _result_cache


# Convenience functions for common cache types
def cache_search(query: str, results: List[Dict[str, Any]]) -> bool:
    """Cache search results."""
    return get_result_cache().set(query, results, cache_type="search")


def get_cached_search(query: str) -> Optional[List[Dict[str, Any]]]:
    """Get cached search results."""
    return get_result_cache().get(query, cache_type="search")


def cache_scrape(url: str, content: Dict[str, Any]) -> bool:
    """Cache scraped content."""
    return get_result_cache().set(url, content, cache_type="scrape")


def get_cached_scrape(url: str) -> Optional[Dict[str, Any]]:
    """Get cached scraped content."""
    return get_result_cache().get(url, cache_type="scrape")


def cache_classification(company_name: str, classification: Dict[str, Any]) -> bool:
    """Cache company classification."""
    return get_result_cache().set(company_name.lower(), classification, cache_type="classification")


def get_cached_classification(company_name: str) -> Optional[Dict[str, Any]]:
    """Get cached company classification."""
    return get_result_cache().get(company_name.lower(), cache_type="classification")


def cache_financial(ticker: str, data: Dict[str, Any]) -> bool:
    """Cache financial data (short TTL)."""
    return get_result_cache().set(ticker.upper(), data, cache_type="financial")


def get_cached_financial(ticker: str) -> Optional[Dict[str, Any]]:
    """Get cached financial data."""
    return get_result_cache().get(ticker.upper(), cache_type="financial")


def cache_news(query: str, articles: List[Dict[str, Any]]) -> bool:
    """Cache news results."""
    return get_result_cache().set(query, articles, cache_type="news")


def get_cached_news(query: str) -> Optional[List[Dict[str, Any]]]:
    """Get cached news results."""
    return get_result_cache().get(query, cache_type="news")


def cache_wikipedia(company_name: str, data: Dict[str, Any]) -> bool:
    """Cache Wikipedia data."""
    return get_result_cache().set(company_name.lower(), data, cache_type="wikipedia")


def get_cached_wikipedia(company_name: str) -> Optional[Dict[str, Any]]:
    """Get cached Wikipedia data."""
    return get_result_cache().get(company_name.lower(), cache_type="wikipedia")


def cache_sec_filing(ticker: str, filing_type: str, data: Dict[str, Any]) -> bool:
    """Cache SEC filing data."""
    cache_key = f"{ticker.upper()}:{filing_type}"
    return get_result_cache().set(cache_key, data, cache_type="sec_filing")


def get_cached_sec_filing(ticker: str, filing_type: str) -> Optional[Dict[str, Any]]:
    """Get cached SEC filing data."""
    cache_key = f"{ticker.upper()}:{filing_type}"
    return get_result_cache().get(cache_key, cache_type="sec_filing")


def print_cache_stats() -> None:
    """Print cache statistics."""
    stats = get_result_cache().get_stats()
    print("\n=== Result Cache Stats ===")
    print(f"Total files: {stats['total_files']}")
    print(f"Total size: {stats['total_size_mb']} MB")
    print(f"Hit rate: {stats['hit_rate']:.1%}")
    print(f"Hits: {stats['hits']}, Misses: {stats['misses']}, Writes: {stats['writes']}")
    print("\nBy type:")
    for type_name, type_stats in stats.get("by_type", {}).items():
        print(f"  {type_name}: {type_stats['files']} files, {type_stats['size_mb']} MB")
