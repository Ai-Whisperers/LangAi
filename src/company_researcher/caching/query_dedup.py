"""
Query Deduplication - Prevent redundant research queries.

Provides:
- Query normalization (case, whitespace, synonyms)
- Semantic similarity detection
- Request coalescing (merge concurrent identical queries)
- Result sharing for duplicate queries
"""

import asyncio
import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


def _utcnow() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class DeduplicationStrategy(str, Enum):
    """How to handle duplicate queries."""

    EXACT = "exact"
    NORMALIZED = "normalized"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


@dataclass
class NormalizedQuery:
    """A normalized query representation."""

    original: str
    normalized: str
    tokens: Set[str]
    hash: str
    company_name: Optional[str] = None
    depth: Optional[str] = None

    @classmethod
    def from_query(
        cls, query: str, company_name: str = None, depth: str = None
    ) -> "NormalizedQuery":
        """Create normalized query from raw input."""
        normalized = cls._normalize(query)
        tokens = cls._tokenize(normalized)
        query_hash = hashlib.md5(normalized.encode()).hexdigest()[:16]
        return cls(
            original=query,
            normalized=normalized,
            tokens=tokens,
            hash=query_hash,
            company_name=company_name,
            depth=depth,
        )

    @staticmethod
    def _normalize(query: str) -> str:
        """Normalize query string."""
        normalized = query.lower().strip()
        normalized = re.sub(r"\s+", " ", normalized)
        filler_words = {"the", "a", "an", "and", "or", "of", "for", "to", "in", "on"}
        words = normalized.split()
        words = [w for w in words if w not in filler_words]
        words.sort()
        return " ".join(words)

    @staticmethod
    def _tokenize(text: str) -> Set[str]:
        """Extract tokens from text."""
        tokens = re.findall(r"\b\w+\b", text.lower())
        return set(tokens)


@dataclass
class PendingQuery:
    """A query currently being processed."""

    query: NormalizedQuery
    future: asyncio.Future
    started_at: datetime
    requester_count: int = 1

    def add_requester(self):
        """Add another requester waiting for this query."""
        self.requester_count += 1


@dataclass
class QueryDeduplicationStats:
    """Statistics for query deduplication."""

    total_queries: int = 0
    deduplicated_queries: int = 0
    coalesced_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_similarity_score: float = 0.0

    @property
    def deduplication_rate(self) -> float:
        if self.total_queries == 0:
            return 0.0
        return self.deduplicated_queries / self.total_queries

    @property
    def coalescence_rate(self) -> float:
        if self.total_queries == 0:
            return 0.0
        return self.coalesced_requests / self.total_queries


class QueryDeduplicator:
    """Deduplicates research queries to avoid redundant processing."""

    def __init__(
        self,
        strategy: DeduplicationStrategy = DeduplicationStrategy.HYBRID,
        similarity_threshold: float = 0.85,
        cache_ttl_seconds: int = 300,
        max_cache_size: int = 1000,
        enable_coalescence: bool = True,
    ):
        self.strategy = strategy
        self.similarity_threshold = similarity_threshold
        self.cache_ttl_seconds = cache_ttl_seconds
        self.max_cache_size = max_cache_size
        self.enable_coalescence = enable_coalescence
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._pending: Dict[str, PendingQuery] = {}
        self._pending_lock = asyncio.Lock()
        self._recent_queries: List[NormalizedQuery] = []
        self._stats = QueryDeduplicationStats()
        self._synonyms: Dict[str, str] = {}

    def add_synonym(self, alias: str, canonical: str):
        """Add company name synonym."""
        self._synonyms[alias.lower()] = canonical.lower()

    def add_synonyms(self, mappings: Dict[str, str]):
        """Add multiple synonyms."""
        for alias, canonical in mappings.items():
            self.add_synonym(alias, canonical)

    async def deduplicate(
        self,
        query: str,
        company_name: str = None,
        depth: str = "standard",
        executor: Callable = None,
    ) -> Tuple[Any, bool]:
        """Deduplicate a query and return result."""
        self._stats.total_queries += 1
        if company_name:
            company_name = self._synonyms.get(company_name.lower(), company_name)
        normalized = NormalizedQuery.from_query(query, company_name, depth)

        cached_result = self._get_cached(normalized)
        if cached_result is not None:
            self._stats.cache_hits += 1
            self._stats.deduplicated_queries += 1
            return cached_result, True

        self._stats.cache_misses += 1

        if self.strategy in (DeduplicationStrategy.SEMANTIC, DeduplicationStrategy.HYBRID):
            similar_result = self._find_similar_cached(normalized)
            if similar_result is not None:
                self._stats.deduplicated_queries += 1
                return similar_result, True

        if self.enable_coalescence:
            async with self._pending_lock:
                if normalized.hash in self._pending:
                    pending = self._pending[normalized.hash]
                    pending.add_requester()
                    self._stats.coalesced_requests += 1

            if normalized.hash in self._pending:
                result = await self._pending[normalized.hash].future
                self._stats.deduplicated_queries += 1
                return result, True

        if executor is None:
            raise ValueError("No executor provided and query not in cache")

        future = asyncio.get_event_loop().create_future()
        pending_query = PendingQuery(query=normalized, future=future, started_at=_utcnow())

        async with self._pending_lock:
            self._pending[normalized.hash] = pending_query

        try:
            result = await executor()
            self._set_cached(normalized, result)
            future.set_result(result)
            return result, False
        except Exception as e:
            future.set_exception(e)
            raise
        finally:
            async with self._pending_lock:
                self._pending.pop(normalized.hash, None)

    def _get_cached(self, query: NormalizedQuery) -> Optional[Any]:
        """Get result from cache if valid."""
        if query.hash not in self._cache:
            return None
        result, timestamp = self._cache[query.hash]
        if _utcnow() - timestamp > timedelta(seconds=self.cache_ttl_seconds):
            del self._cache[query.hash]
            return None
        return result

    def _set_cached(self, query: NormalizedQuery, result: Any):
        """Cache a query result."""
        if len(self._cache) >= self.max_cache_size:
            oldest_key = min(self._cache, key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]
        self._cache[query.hash] = (result, _utcnow())
        self._recent_queries.append(query)
        if len(self._recent_queries) > self.max_cache_size:
            self._recent_queries.pop(0)

    def _find_similar_cached(self, query: NormalizedQuery) -> Optional[Any]:
        """Find semantically similar cached query."""
        best_match = None
        best_score = 0.0
        for recent in self._recent_queries:
            if query.company_name and recent.company_name:
                if query.company_name.lower() != recent.company_name.lower():
                    continue
            if query.depth and recent.depth:
                if query.depth != recent.depth:
                    continue
            score = self._calculate_similarity(query, recent)
            if score > best_score and score >= self.similarity_threshold:
                best_score = score
                best_match = recent
        if best_match and best_match.hash in self._cache:
            self._stats.avg_similarity_score = (self._stats.avg_similarity_score + best_score) / 2
            return self._cache[best_match.hash][0]
        return None

    def _calculate_similarity(self, q1: NormalizedQuery, q2: NormalizedQuery) -> float:
        """Calculate Jaccard similarity between queries."""
        if not q1.tokens or not q2.tokens:
            return 0.0
        intersection = len(q1.tokens & q2.tokens)
        union = len(q1.tokens | q2.tokens)
        return intersection / union if union > 0 else 0.0

    def get_stats(self) -> QueryDeduplicationStats:
        """Get deduplication statistics."""
        return self._stats

    def clear_cache(self):
        """Clear all cached results."""
        self._cache.clear()
        self._recent_queries.clear()

    def invalidate(self, company_name: str = None, query_hash: str = None):
        """Invalidate cache entries."""
        if query_hash and query_hash in self._cache:
            del self._cache[query_hash]
            return
        if company_name:
            company_lower = company_name.lower()
            to_remove = [
                q.hash
                for q in self._recent_queries
                if q.company_name and q.company_name.lower() == company_lower
            ]
            for h in to_remove:
                self._cache.pop(h, None)
            self._recent_queries = [
                q
                for q in self._recent_queries
                if not (q.company_name and q.company_name.lower() == company_lower)
            ]


class RequestCoalescer:
    """Coalesces multiple concurrent requests for the same resource."""

    def __init__(self, timeout_seconds: float = 30.0):
        self.timeout_seconds = timeout_seconds
        self._in_flight: Dict[str, asyncio.Future] = {}
        self._lock = asyncio.Lock()
        self._stats = {"total_requests": 0, "coalesced": 0, "executed": 0}

    async def coalesce(self, key: str, executor: Callable[[], Any]) -> Tuple[Any, bool]:
        """Execute with coalescing. Returns (result, was_coalesced)."""
        self._stats["total_requests"] += 1
        async with self._lock:
            if key in self._in_flight:
                self._stats["coalesced"] += 1
                future = self._in_flight[key]
        if key in self._in_flight:
            try:
                result = await asyncio.wait_for(
                    asyncio.shield(future), timeout=self.timeout_seconds
                )
                return result, True
            except asyncio.TimeoutError:
                pass
        future = asyncio.get_event_loop().create_future()
        async with self._lock:
            self._in_flight[key] = future
        try:
            self._stats["executed"] += 1
            result = await executor()
            future.set_result(result)
            return result, False
        except Exception as e:
            future.set_exception(e)
            raise
        finally:
            async with self._lock:
                self._in_flight.pop(key, None)

    def get_stats(self) -> Dict[str, int]:
        """Get coalescence statistics."""
        return dict(self._stats)


class CompanyNameNormalizer:
    """Normalizes company names for better matching."""

    SUFFIXES = [
        r"\s+inc\.?$",
        r"\s+incorporated$",
        r"\s+corp\.?$",
        r"\s+corporation$",
        r"\s+ltd\.?$",
        r"\s+limited$",
        r"\s+llc\.?$",
        r"\s+plc\.?$",
        r"\s+co\.?$",
        r"\s+company$",
        r"\s+&\s+co\.?$",
        r"\s+group$",
        r"\s+holdings?$",
        r"\s+international$",
        r"\s+intl\.?$",
    ]

    def __init__(self):
        self._aliases: Dict[str, str] = {}
        self._tickers: Dict[str, str] = {}
        self._load_common_aliases()

    def _load_common_aliases(self):
        """Load common company aliases."""
        common = {
            "alphabet": "google",
            "googl": "google",
            "goog": "google",
            "meta platforms": "meta",
            "facebook": "meta",
            "fb": "meta",
            "microsoft corporation": "microsoft",
            "msft": "microsoft",
            "apple inc": "apple",
            "aapl": "apple",
            "amazon.com": "amazon",
            "amzn": "amazon",
            "jpmorgan chase": "jp morgan",
            "jpm": "jp morgan",
            "berkshire hathaway": "berkshire",
            "brk": "berkshire",
            "exxon mobil": "exxonmobil",
            "xom": "exxonmobil",
        }
        self._aliases.update(common)

    def add_alias(self, alias: str, canonical: str):
        """Add a company alias."""
        self._aliases[alias.lower()] = canonical.lower()

    def add_ticker(self, ticker: str, company_name: str):
        """Map a stock ticker to company name."""
        self._tickers[ticker.upper()] = company_name.lower()

    def normalize(self, name: str) -> str:
        """Normalize a company name."""
        if not name:
            return ""
        normalized = name.strip().lower()
        if normalized.upper() in self._tickers:
            return self._tickers[normalized.upper()]
        if normalized in self._aliases:
            return self._aliases[normalized]
        for suffix_pattern in self.SUFFIXES:
            normalized = re.sub(suffix_pattern, "", normalized, flags=re.IGNORECASE)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        if normalized in self._aliases:
            return self._aliases[normalized]
        return normalized

    def are_same_company(self, name1: str, name2: str) -> bool:
        """Check if two names refer to the same company."""
        return self.normalize(name1) == self.normalize(name2)


def create_deduplicator(
    strategy: str = "hybrid", similarity_threshold: float = 0.85, cache_ttl_seconds: int = 300
) -> QueryDeduplicator:
    """Create a query deduplicator with common settings."""
    strategy_enum = DeduplicationStrategy(strategy)
    return QueryDeduplicator(
        strategy=strategy_enum,
        similarity_threshold=similarity_threshold,
        cache_ttl_seconds=cache_ttl_seconds,
    )


def normalize_company_name(name: str) -> str:
    """Normalize a company name."""
    normalizer = CompanyNameNormalizer()
    return normalizer.normalize(name)
