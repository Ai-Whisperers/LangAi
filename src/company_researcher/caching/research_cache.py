"""
Research Result Caching - Cache complete research results.

Provides:
- Full research result caching
- TTL-based expiration
- Event-based invalidation
- Cache statistics and warming
"""

import hashlib
import json
import pickle
import sqlite3
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from ..utils import get_logger, utc_now

logger = get_logger(__name__)


class ResearchCacheStatus(str, Enum):
    """Status of a cache entry."""
    FRESH = "fresh"
    STALE = "stale"
    EXPIRED = "expired"
    INVALID = "invalid"


@dataclass
class ResearchCacheEntry:
    """A cached research result."""
    key: str
    company_name: str
    research_depth: str
    result: Dict[str, Any]
    created_at: datetime
    expires_at: datetime
    access_count: int = 0
    last_accessed: datetime = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    invalidation_triggers: Set[str] = field(default_factory=set)

    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at

    @property
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        return utc_now() > self.expires_at

    @property
    def age_seconds(self) -> float:
        """Get age in seconds."""
        return (utc_now() - self.created_at).total_seconds()

    @property
    def status(self) -> ResearchCacheStatus:
        """Get cache status."""
        if self.is_expired:
            return ResearchCacheStatus.EXPIRED
        ttl = (self.expires_at - self.created_at).total_seconds()
        if self.age_seconds > ttl * 0.8:
            return ResearchCacheStatus.STALE
        return ResearchCacheStatus.FRESH

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "company_name": self.company_name,
            "research_depth": self.research_depth,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat(),
            "status": self.status.value,
            "age_seconds": self.age_seconds,
            "metadata": self.metadata
        }


@dataclass
class ResearchCacheStats:
    """Cache statistics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    invalidations: int = 0
    total_entries: int = 0
    memory_bytes: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "invalidations": self.invalidations,
            "total_entries": self.total_entries,
            "hit_rate": f"{self.hit_rate:.2%}",
            "memory_bytes": self.memory_bytes
        }


class ResearchResultCache:
    """
    Cache for complete research results.

    Usage:
        cache = ResearchResultCache()

        # Cache a result
        cache.set(
            company_name="Tesla",
            depth="comprehensive",
            result=research_result,
            ttl_hours=24
        )

        # Get cached result
        cached = cache.get("Tesla", "comprehensive")
        if cached:
            return cached.result

        # Invalidate on news trigger
        cache.invalidate_company("Tesla")

        # Get stats
        stats = cache.stats
    """

    def __init__(
        self,
        max_entries: int = 1000,
        default_ttl_hours: float = 24,
        storage_path: str = None,
        enable_persistence: bool = True
    ):
        self.max_entries = max_entries
        self.default_ttl_hours = default_ttl_hours
        self.enable_persistence = enable_persistence
        self._cache: Dict[str, ResearchCacheEntry] = {}
        self._stats = ResearchCacheStats()
        self._lock = threading.RLock()
        self._invalidation_callbacks: List[Callable] = []

        if enable_persistence and storage_path:
            self._db_path = Path(storage_path)
            self._init_db()
        else:
            self._db_path = None

    def _init_db(self) -> None:
        """Initialize SQLite database."""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(str(self._db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS research_cache (
                    key TEXT PRIMARY KEY,
                    company_name TEXT,
                    research_depth TEXT,
                    result BLOB,
                    created_at TEXT,
                    expires_at TEXT,
                    access_count INTEGER,
                    last_accessed TEXT,
                    metadata TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_company
                ON research_cache(company_name)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires
                ON research_cache(expires_at)
            """)
            conn.commit()

    def _generate_key(self, company_name: str, depth: str) -> str:
        """Generate cache key."""
        normalized = f"{company_name.lower().strip()}:{depth.lower()}"
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def set(
        self,
        company_name: str,
        depth: str,
        result: Dict[str, Any],
        ttl_hours: float = None,
        metadata: Dict[str, Any] = None,
        invalidation_triggers: Set[str] = None
    ) -> ResearchCacheEntry:
        """
        Cache a research result.

        Args:
            company_name: Company name
            depth: Research depth level
            result: Research result dictionary
            ttl_hours: Time-to-live in hours
            metadata: Additional metadata
            invalidation_triggers: Events that invalidate this entry

        Returns:
            Created ResearchCacheEntry
        """
        key = self._generate_key(company_name, depth)
        ttl = ttl_hours or self.default_ttl_hours
        now = utc_now()

        entry = ResearchCacheEntry(
            key=key,
            company_name=company_name,
            research_depth=depth,
            result=result,
            created_at=now,
            expires_at=now + timedelta(hours=ttl),
            metadata=metadata or {},
            invalidation_triggers=invalidation_triggers or set()
        )

        with self._lock:
            while len(self._cache) >= self.max_entries:
                self._evict_oldest()

            self._cache[key] = entry
            self._stats.total_entries = len(self._cache)

            if self._db_path:
                self._persist_entry(entry)

        return entry

    def get(
        self,
        company_name: str,
        depth: str,
        allow_stale: bool = False
    ) -> Optional[ResearchCacheEntry]:
        """
        Get cached research result.

        Args:
            company_name: Company name
            depth: Research depth level
            allow_stale: Return stale entries if fresh not available

        Returns:
            ResearchCacheEntry if found and valid, None otherwise
        """
        key = self._generate_key(company_name, depth)

        with self._lock:
            entry = self._cache.get(key)

            if entry is None and self._db_path:
                entry = self._load_entry(key)
                if entry:
                    self._cache[key] = entry

            if entry is None:
                self._stats.misses += 1
                return None

            if entry.is_expired:
                self._remove_entry(key)
                self._stats.misses += 1
                return None

            if entry.status == ResearchCacheStatus.STALE and not allow_stale:
                self._stats.misses += 1
                return None

            entry.access_count += 1
            entry.last_accessed = utc_now()
            self._stats.hits += 1

            return entry

    def invalidate_company(self, company_name: str) -> int:
        """Invalidate all cache entries for a company."""
        count = 0
        with self._lock:
            keys_to_remove = [
                key for key, entry in self._cache.items()
                if entry.company_name.lower() == company_name.lower()
            ]
            for key in keys_to_remove:
                self._remove_entry(key)
                count += 1
            self._stats.invalidations += count

        for callback in self._invalidation_callbacks:
            try:
                callback(company_name)
            except Exception as e:
                logger.debug(f"Invalidation callback failed for {company_name}: {e}")

        return count

    def invalidate_by_trigger(self, trigger: str) -> int:
        """Invalidate entries with matching trigger."""
        count = 0
        with self._lock:
            keys_to_remove = [
                key for key, entry in self._cache.items()
                if trigger in entry.invalidation_triggers
            ]
            for key in keys_to_remove:
                self._remove_entry(key)
                count += 1
            self._stats.invalidations += count

        return count

    def _evict_oldest(self) -> None:
        """Evict oldest entry."""
        if not self._cache:
            return

        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed
        )
        self._remove_entry(oldest_key)
        self._stats.evictions += 1

    def _remove_entry(self, key: str) -> None:
        """Remove entry from cache and database."""
        if key in self._cache:
            del self._cache[key]

        if self._db_path:
            try:
                with sqlite3.connect(str(self._db_path)) as conn:
                    conn.execute("DELETE FROM research_cache WHERE key = ?", (key,))
                    conn.commit()
            except Exception as e:
                logger.warning(f"Failed to delete cache entry from DB (key={key}): {e}")

        self._stats.total_entries = len(self._cache)

    def _persist_entry(self, entry: ResearchCacheEntry) -> None:
        """Persist entry to database."""
        try:
            with sqlite3.connect(str(self._db_path)) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO research_cache
                    (key, company_name, research_depth, result, created_at,
                     expires_at, access_count, last_accessed, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.key,
                    entry.company_name,
                    entry.research_depth,
                    pickle.dumps(entry.result),
                    entry.created_at.isoformat(),
                    entry.expires_at.isoformat(),
                    entry.access_count,
                    entry.last_accessed.isoformat(),
                    json.dumps(entry.metadata)
                ))
                conn.commit()
        except Exception as e:
            logger.warning(f"Failed to persist cache entry for {entry.company_name}: {e}")

    def _load_entry(self, key: str) -> Optional[ResearchCacheEntry]:
        """Load entry from database."""
        try:
            with sqlite3.connect(str(self._db_path)) as conn:
                cursor = conn.execute(
                    "SELECT * FROM research_cache WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()

                if row:
                    return ResearchCacheEntry(
                        key=row[0],
                        company_name=row[1],
                        research_depth=row[2],
                        result=pickle.loads(row[3]),
                        created_at=datetime.fromisoformat(row[4]),
                        expires_at=datetime.fromisoformat(row[5]),
                        access_count=row[6],
                        last_accessed=datetime.fromisoformat(row[7]),
                        metadata=json.loads(row[8])
                    )
        except Exception as e:
            logger.debug(f"Failed to load cache entry (key={key}): {e}")

        return None

    def cleanup_expired(self) -> int:
        """Remove all expired entries."""
        count = 0
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired
            ]
            for key in expired_keys:
                self._remove_entry(key)
                count += 1

        return count

    def clear(self) -> None:
        """Clear all entries."""
        with self._lock:
            self._cache.clear()
            self._stats = ResearchCacheStats()

            if self._db_path:
                try:
                    with sqlite3.connect(str(self._db_path)) as conn:
                        conn.execute("DELETE FROM research_cache")
                        conn.commit()
                except Exception as e:
                    logger.warning(f"Failed to clear cache database: {e}")

    def on_invalidation(self, callback: Callable[[str], None]) -> None:
        """Register invalidation callback."""
        self._invalidation_callbacks.append(callback)

    @property
    def stats(self) -> ResearchCacheStats:
        """Get cache statistics."""
        return self._stats

    def get_all_entries(self) -> List[ResearchCacheEntry]:
        """Get all cache entries."""
        with self._lock:
            return list(self._cache.values())

    def get_companies(self) -> List[str]:
        """Get all cached company names."""
        with self._lock:
            return list(set(e.company_name for e in self._cache.values()))


class CacheWarmer:
    """
    Pre-warms cache with popular companies.

    Usage:
        warmer = CacheWarmer(cache, research_func)
        warmer.add_companies(["Tesla", "Apple", "Google"])
        await warmer.warm()
    """

    def __init__(
        self,
        cache: ResearchResultCache,
        research_func: Callable,
        max_concurrent: int = 3
    ):
        self.cache = cache
        self.research_func = research_func
        self.max_concurrent = max_concurrent
        self._companies: List[str] = []

    def add_companies(self, companies: List[str]) -> None:
        """Add companies to warming list."""
        self._companies.extend(companies)

    def add_from_popularity(self, top_n: int = 10) -> None:
        """Add most accessed companies to warming list."""
        entries = self.cache.get_all_entries()
        sorted_entries = sorted(
            entries,
            key=lambda e: e.access_count,
            reverse=True
        )
        popular = [e.company_name for e in sorted_entries[:top_n]]
        self._companies.extend(popular)

    async def warm(self, depth: str = "standard") -> Dict[str, bool]:
        """Warm cache for all listed companies."""
        import asyncio

        results = {}
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def warm_company(company: str):
            async with semaphore:
                try:
                    existing = self.cache.get(company, depth)
                    if existing and existing.status == ResearchCacheStatus.FRESH:
                        results[company] = True
                        return

                    result = await self.research_func(company, depth)
                    self.cache.set(
                        company_name=company,
                        depth=depth,
                        result=result
                    )
                    results[company] = True

                except Exception as e:
                    logger.warning(f"Cache warming failed for {company}: {e}")
                    results[company] = False

        unique_companies = list(set(self._companies))
        await asyncio.gather(*[
            warm_company(company) for company in unique_companies
        ])

        return results


class NewsBasedInvalidator:
    """
    Invalidates cache entries based on news events.

    Usage:
        invalidator = NewsBasedInvalidator(cache)
        invalidator.add_news_source(news_api)
        await invalidator.monitor()
    """

    def __init__(
        self,
        cache: ResearchResultCache,
        check_interval: float = 300  # 5 minutes
    ):
        self.cache = cache
        self.check_interval = check_interval
        self._news_sources: List[Callable] = []
        self._running = False
        self._keywords = {
            "earnings": ["earnings", "quarterly results", "revenue"],
            "leadership": ["ceo", "cfo", "appoint", "resign"],
            "merger": ["acquire", "merger", "acquisition"],
            "lawsuit": ["lawsuit", "litigation", "sec"],
            "product": ["launch", "announce", "release"]
        }

    def add_news_source(self, source: Callable) -> None:
        """Add a news source callable."""
        self._news_sources.append(source)

    async def check_for_updates(self, company_name: str) -> bool:
        """Check if company has significant news."""
        for source in self._news_sources:
            try:
                news = await source(company_name)
                if self._has_significant_news(news):
                    return True
            except Exception as e:
                logger.debug(f"News source check failed for {company_name}: {e}")
                continue
        return False

    def _has_significant_news(self, news: List[Dict]) -> bool:
        """Check if news contains significant updates."""
        for article in news:
            title = article.get("title", "").lower()
            for category, keywords in self._keywords.items():
                if any(kw in title for kw in keywords):
                    return True
        return False

    async def monitor(self) -> None:
        """Continuously monitor for invalidation triggers."""
        import asyncio

        self._running = True
        while self._running:
            companies = self.cache.get_companies()

            for company in companies:
                if await self.check_for_updates(company):
                    self.cache.invalidate_company(company)

            await asyncio.sleep(self.check_interval)

    def stop(self) -> None:
        """Stop monitoring."""
        self._running = False


# Convenience functions

def create_research_cache(
    max_entries: int = 1000,
    ttl_hours: float = 24,
    storage_path: str = None
) -> ResearchResultCache:
    """Create a research result cache."""
    return ResearchResultCache(
        max_entries=max_entries,
        default_ttl_hours=ttl_hours,
        storage_path=storage_path
    )
