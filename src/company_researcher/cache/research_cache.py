"""
Research Cache Module.

Caches Tavily search results to avoid redundant API calls and token spending
during testing and repeated research runs.

Cache Structure:
- data/cache/sources/{query_hash}.json - Cached search results by query hash
- data/cache/reports/{company_slug}_{date}.json - Cached generated reports

Features:
- Query hash-based lookup
- TTL-based expiration (configurable)
- Force refresh option
- Cache statistics

Usage:
    cache = ResearchCache(cache_dir="data/cache", ttl_days=7)

    # Check cache before API call
    cached = cache.get_search_results(query)
    if cached:
        return cached

    # Store new results
    results = tavily_client.search(query)
    cache.store_search_results(query, results)
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class CacheStats:
    """Statistics about cache usage."""
    hits: int = 0
    misses: int = 0
    expired: int = 0
    stored: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "expired": self.expired,
            "stored": self.stored,
            "hit_rate_percent": round(self.hit_rate, 1),
            "total_lookups": self.hits + self.misses,
        }


@dataclass
class CacheEntry:
    """A cached search result entry."""
    query: str
    query_hash: str
    results: Dict[str, Any]
    timestamp: str
    expires: str
    source_count: int

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        expires_dt = datetime.fromisoformat(self.expires)
        return datetime.now() > expires_dt

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CacheEntry":
        """Create from dictionary."""
        return cls(
            query=data["query"],
            query_hash=data["query_hash"],
            results=data["results"],
            timestamp=data["timestamp"],
            expires=data["expires"],
            source_count=data.get("source_count", 0),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "query_hash": self.query_hash,
            "results": self.results,
            "timestamp": self.timestamp,
            "expires": self.expires,
            "source_count": self.source_count,
        }


class ResearchCache:
    """
    Cache for research data to avoid redundant API calls.

    Stores:
    - Tavily search results by query hash
    - Generated reports by company and date
    """

    def __init__(
        self,
        cache_dir: str = "data/cache",
        ttl_days: int = 7,
        enabled: bool = True
    ):
        """
        Initialize research cache.

        Args:
            cache_dir: Base directory for cache files
            ttl_days: Time-to-live for cache entries in days
            enabled: Whether caching is enabled
        """
        self.cache_dir = Path(cache_dir)
        self.ttl_days = ttl_days
        self.enabled = enabled
        self.stats = CacheStats()

        # Create cache directories
        self.sources_dir = self.cache_dir / "sources"
        self.reports_dir = self.cache_dir / "reports"
        self.index_file = self.cache_dir / "cache_index.json"

        if self.enabled:
            self._setup_directories()
            self._load_index()

    def _setup_directories(self):
        """Create cache directory structure."""
        self.sources_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _load_index(self):
        """Load cache index from disk."""
        self.index: Dict[str, Dict[str, Any]] = {
            "sources": {},  # query_hash -> metadata
            "reports": {},  # company_date -> metadata
        }

        if self.index_file.exists():
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    self.index = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass  # Start fresh if index is corrupted

    def _save_index(self):
        """Save cache index to disk."""
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _generate_query_hash(query: str) -> str:
        """Generate deterministic hash from query string."""
        # Normalize query: lowercase, strip, collapse whitespace
        normalized = " ".join(query.lower().strip().split())
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    @staticmethod
    def _generate_company_slug(company_name: str) -> str:
        """Generate URL-safe slug from company name."""
        slug = company_name.lower().strip()
        slug = slug.replace(" ", "_").replace(".", "").replace(",", "")
        return slug

    # =====================================================================
    # Search Results Cache
    # =====================================================================

    def get_search_results(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get cached search results for a query.

        Args:
            query: The search query string

        Returns:
            Cached results dict if found and not expired, None otherwise
        """
        if not self.enabled:
            return None

        query_hash = self._generate_query_hash(query)
        cache_file = self.sources_dir / f"{query_hash}.json"

        if not cache_file.exists():
            self.stats.misses += 1
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            entry = CacheEntry.from_dict(data)

            if entry.is_expired():
                self.stats.expired += 1
                self.stats.misses += 1
                # Clean up expired entry
                cache_file.unlink(missing_ok=True)
                return None

            self.stats.hits += 1
            return entry.results

        except (json.JSONDecodeError, IOError, KeyError):
            self.stats.misses += 1
            return None

    def store_search_results(
        self,
        query: str,
        results: Dict[str, Any],
        ttl_days: Optional[int] = None
    ) -> str:
        """
        Store search results in cache.

        Args:
            query: The search query string
            results: The search results to cache
            ttl_days: Override TTL for this entry

        Returns:
            The query hash used for storage
        """
        if not self.enabled:
            return ""

        query_hash = self._generate_query_hash(query)
        ttl = ttl_days if ttl_days is not None else self.ttl_days

        now = datetime.now()
        expires = now + timedelta(days=ttl)

        entry = CacheEntry(
            query=query,
            query_hash=query_hash,
            results=results,
            timestamp=now.isoformat(),
            expires=expires.isoformat(),
            source_count=len(results.get("results", [])),
        )

        cache_file = self.sources_dir / f"{query_hash}.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(entry.to_dict(), f, indent=2, ensure_ascii=False)

        # Update index
        self.index["sources"][query_hash] = {
            "query": query[:100],  # Truncate for index
            "timestamp": now.isoformat(),
            "expires": expires.isoformat(),
            "source_count": entry.source_count,
        }
        self._save_index()

        self.stats.stored += 1
        return query_hash

    # =====================================================================
    # Report Cache
    # =====================================================================

    def get_cached_report(
        self,
        company_name: str,
        date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached report for a company.

        Args:
            company_name: Company name
            date: Optional date string (YYYYMMDD), defaults to today

        Returns:
            Cached report data if found and not expired, None otherwise
        """
        if not self.enabled:
            return None

        slug = self._generate_company_slug(company_name)
        date_str = date or datetime.now().strftime("%Y%m%d")
        cache_key = f"{slug}_{date_str}"
        cache_file = self.reports_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Check expiration
            expires = datetime.fromisoformat(data.get("expires", "2000-01-01"))
            if datetime.now() > expires:
                cache_file.unlink(missing_ok=True)
                return None

            return data

        except (json.JSONDecodeError, IOError):
            return None

    def store_report(
        self,
        company_name: str,
        report_data: Dict[str, Any],
        ttl_days: Optional[int] = None
    ) -> str:
        """
        Store generated report in cache.

        Args:
            company_name: Company name
            report_data: Report data to cache (should include 'summary', 'metrics', etc.)
            ttl_days: Override TTL for this entry

        Returns:
            The cache key used for storage
        """
        if not self.enabled:
            return ""

        slug = self._generate_company_slug(company_name)
        date_str = datetime.now().strftime("%Y%m%d")
        cache_key = f"{slug}_{date_str}"

        ttl = ttl_days if ttl_days is not None else self.ttl_days
        now = datetime.now()
        expires = now + timedelta(days=ttl)

        cache_data = {
            "company_name": company_name,
            "cache_key": cache_key,
            "timestamp": now.isoformat(),
            "expires": expires.isoformat(),
            **report_data,
        }

        cache_file = self.reports_dir / f"{cache_key}.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

        # Update index
        self.index["reports"][cache_key] = {
            "company_name": company_name,
            "timestamp": now.isoformat(),
            "expires": expires.isoformat(),
        }
        self._save_index()

        return cache_key

    # =====================================================================
    # Bulk Operations
    # =====================================================================

    def get_all_cached_queries(self, company_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all cached search queries.

        Args:
            company_filter: Optional company name to filter by

        Returns:
            List of cached query metadata
        """
        results = []

        for query_hash, metadata in self.index.get("sources", {}).items():
            if company_filter:
                if company_filter.lower() not in metadata.get("query", "").lower():
                    continue

            results.append({
                "query_hash": query_hash,
                **metadata,
            })

        return sorted(results, key=lambda x: x.get("timestamp", ""), reverse=True)

    def clear_expired(self) -> int:
        """
        Remove all expired cache entries.

        Returns:
            Number of entries removed
        """
        removed = 0
        now = datetime.now()

        # Clear expired source cache
        for cache_file in self.sources_dir.glob("*.json"):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                expires = datetime.fromisoformat(data.get("expires", "2000-01-01"))
                if now > expires:
                    cache_file.unlink()
                    removed += 1
            except (json.JSONDecodeError, IOError):
                pass

        # Clear expired report cache
        for cache_file in self.reports_dir.glob("*.json"):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                expires = datetime.fromisoformat(data.get("expires", "2000-01-01"))
                if now > expires:
                    cache_file.unlink()
                    removed += 1
            except (json.JSONDecodeError, IOError):
                pass

        # Rebuild index
        self._rebuild_index()

        return removed

    def clear_all(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries removed
        """
        removed = 0

        for cache_file in self.sources_dir.glob("*.json"):
            cache_file.unlink()
            removed += 1

        for cache_file in self.reports_dir.glob("*.json"):
            cache_file.unlink()
            removed += 1

        self.index = {"sources": {}, "reports": {}}
        self._save_index()

        return removed

    def _rebuild_index(self):
        """Rebuild index from disk files."""
        self.index = {"sources": {}, "reports": {}}

        # Rebuild sources index
        for cache_file in self.sources_dir.glob("*.json"):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                query_hash = cache_file.stem
                self.index["sources"][query_hash] = {
                    "query": data.get("query", "")[:100],
                    "timestamp": data.get("timestamp", ""),
                    "expires": data.get("expires", ""),
                    "source_count": data.get("source_count", 0),
                }
            except (json.JSONDecodeError, IOError):
                pass

        # Rebuild reports index
        for cache_file in self.reports_dir.glob("*.json"):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                cache_key = cache_file.stem
                self.index["reports"][cache_key] = {
                    "company_name": data.get("company_name", ""),
                    "timestamp": data.get("timestamp", ""),
                    "expires": data.get("expires", ""),
                }
            except (json.JSONDecodeError, IOError):
                pass

        self._save_index()

    # =====================================================================
    # Statistics & Info
    # =====================================================================

    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache statistics and info."""
        source_count = len(list(self.sources_dir.glob("*.json")))
        report_count = len(list(self.reports_dir.glob("*.json")))

        # Calculate total cache size
        total_size = 0
        for cache_file in self.sources_dir.glob("*.json"):
            total_size += cache_file.stat().st_size
        for cache_file in self.reports_dir.glob("*.json"):
            total_size += cache_file.stat().st_size

        return {
            "enabled": self.enabled,
            "cache_dir": str(self.cache_dir),
            "ttl_days": self.ttl_days,
            "source_entries": source_count,
            "report_entries": report_count,
            "total_entries": source_count + report_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "session_stats": self.stats.to_dict(),
        }

    def print_stats(self):
        """Print cache statistics."""
        info = self.get_cache_info()
        print(f"\n{'='*50}")
        print("CACHE STATISTICS")
        print(f"{'='*50}")
        print(f"Enabled:        {info['enabled']}")
        print(f"Cache Dir:      {info['cache_dir']}")
        print(f"TTL (days):     {info['ttl_days']}")
        print(f"Source Entries: {info['source_entries']}")
        print(f"Report Entries: {info['report_entries']}")
        print(f"Total Size:     {info['total_size_mb']} MB")
        print(f"\nSession Stats:")
        print(f"  Hits:         {info['session_stats']['hits']}")
        print(f"  Misses:       {info['session_stats']['misses']}")
        print(f"  Expired:      {info['session_stats']['expired']}")
        print(f"  Stored:       {info['session_stats']['stored']}")
        print(f"  Hit Rate:     {info['session_stats']['hit_rate_percent']}%")
        print(f"{'='*50}\n")


# Convenience function for creating cache with environment defaults
def create_cache(
    cache_dir: Optional[str] = None,
    ttl_days: Optional[int] = None,
    enabled: Optional[bool] = None
) -> ResearchCache:
    """
    Create ResearchCache with environment variable defaults.

    Environment variables:
    - RESEARCH_CACHE_DIR: Cache directory (default: data/cache)
    - RESEARCH_CACHE_TTL: TTL in days (default: 7)
    - RESEARCH_CACHE_ENABLED: Whether caching is enabled (default: true)
    """
    cache_dir = cache_dir or os.getenv("RESEARCH_CACHE_DIR", "data/cache")
    ttl_days = ttl_days or int(os.getenv("RESEARCH_CACHE_TTL", "7"))

    if enabled is None:
        enabled_str = os.getenv("RESEARCH_CACHE_ENABLED", "true").lower()
        enabled = enabled_str in ("true", "1", "yes", "on")

    return ResearchCache(cache_dir=cache_dir, ttl_days=ttl_days, enabled=enabled)
