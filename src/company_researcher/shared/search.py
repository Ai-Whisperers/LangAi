"""
Robust Search Module.

Implements diversified search with:
1. Semantic query diversification
2. Connection pooling
3. Adaptive health tracking
4. Exponential backoff
5. Calibrated scoring
6. Deduplication

Replaces quantity-based search with coverage-based search.
"""

import asyncio
import re
import random
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


@dataclass
class ProviderHealth:
    """Track provider health for adaptive behavior."""
    name: str
    consecutive_failures: int = 0
    last_failure: Optional[datetime] = None
    last_success: Optional[datetime] = None
    avg_response_time_ms: float = 0.0
    total_requests: int = 0
    total_successes: int = 0

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 1.0
        return self.total_successes / self.total_requests

    @property
    def is_healthy(self) -> bool:
        """Check if provider is healthy (can accept requests)."""
        if self.consecutive_failures >= 3:
            # Allow retry after exponential cooldown
            if self.last_failure:
                cooldown = timedelta(seconds=60 * (2 ** min(self.consecutive_failures - 3, 5)))
                if datetime.now() - self.last_failure < cooldown:
                    return False
        return True

    def record_success(self, response_time_ms: float):
        """Record a successful request."""
        self.consecutive_failures = 0
        self.last_success = datetime.now()
        self.total_requests += 1
        self.total_successes += 1
        # Rolling average (90% old, 10% new)
        self.avg_response_time_ms = self.avg_response_time_ms * 0.9 + response_time_ms * 0.1

    def record_failure(self):
        """Record a failed request."""
        self.consecutive_failures += 1
        self.last_failure = datetime.now()
        self.total_requests += 1


@dataclass
class SearchResult:
    """Standardized search result with calibrated scoring."""
    url: str
    title: str
    snippet: str
    provider: str
    raw_rank: int  # Position in provider's results
    authority_score: float = 0.0  # 0-1, based on domain
    relevance_score: float = 0.0  # 0-1, based on query match
    combined_score: float = 0.0  # Weighted combination
    category: str = ""  # Query category

    def calculate_combined_score(self, query: str):
        """Calculate calibrated combined score."""
        self.authority_score = self._calculate_authority()
        self.relevance_score = self._calculate_relevance(query)

        # Rank decay (first results better)
        rank_factor = 1.0 / (1.0 + 0.1 * self.raw_rank)

        # Combined: 40% authority, 40% relevance, 20% rank
        self.combined_score = (
            self.authority_score * 0.4 +
            self.relevance_score * 0.4 +
            rank_factor * 0.2
        )

    def _calculate_authority(self) -> float:
        """Domain-based authority scoring."""
        domain = self.url.lower()

        # Tier 1: Official/regulatory (1.0)
        if any(d in domain for d in ['sec.gov', 'investor.', 'ir.']):
            return 1.0

        # Tier 2: Major financial news (0.85)
        if any(d in domain for d in ['bloomberg.com', 'reuters.com', 'wsj.com', 'ft.com']):
            return 0.85

        # Tier 3: Reputable tech/business (0.70)
        if any(d in domain for d in ['techcrunch.com', 'forbes.com', 'cnbc.com',
                                      'businessinsider.com', 'venturebeat.com']):
            return 0.70

        # Tier 4: General domains (0.55)
        if any(d in domain for d in ['.com', '.org', '.net']):
            return 0.55

        return 0.40

    def _calculate_relevance(self, query: str) -> float:
        """Query relevance scoring."""
        query_terms = set(query.lower().split())
        title_terms = set(self.title.lower().split()) if self.title else set()
        snippet_terms = set(self.snippet.lower().split()) if self.snippet else set()

        # Remove stopwords
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'to', 'of',
                     'and', 'in', 'for', 'on', 'with', 'at', 'by'}
        query_terms -= stopwords

        if not query_terms:
            return 0.5

        # Title match (weighted higher)
        title_overlap = len(query_terms & title_terms) / len(query_terms)

        # Snippet match
        snippet_overlap = len(query_terms & snippet_terms) / len(query_terms) if snippet_terms else 0

        return title_overlap * 0.6 + snippet_overlap * 0.4

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "snippet": self.snippet,
            "provider": self.provider,
            "authority_score": round(self.authority_score, 2),
            "relevance_score": round(self.relevance_score, 2),
            "combined_score": round(self.combined_score, 2),
            "category": self.category
        }


@dataclass
class DiverseQuery:
    """A query designed for specific coverage."""
    query: str
    category: str
    expected_domains: List[str]
    min_results: int
    priority: int


# Query categories for diversified search
QUERY_CATEGORIES = {
    "official_filings": {
        "template": '"{company}" site:sec.gov 10-K OR 10-Q {year}',
        "domains": ["sec.gov"],
        "priority": 1,
        "min_results": 3
    },
    "investor_relations": {
        "template": '"{company}" investor relations earnings call transcript {year}',
        "domains": ["seekingalpha.com", "fool.com"],
        "priority": 1,
        "min_results": 5
    },
    "financial_news": {
        "template": '"{company}" revenue profit financial results {year}',
        "domains": ["bloomberg.com", "reuters.com", "wsj.com"],
        "priority": 2,
        "min_results": 8
    },
    "company_overview": {
        "template": '"{company}" company overview history headquarters employees',
        "domains": [],
        "priority": 2,
        "min_results": 5
    },
    "competitive_analysis": {
        "template": '"{company}" competitors market share comparison',
        "domains": [],
        "priority": 2,
        "min_results": 5
    },
    "product_info": {
        "template": '"{company}" products services offerings technology',
        "domains": [],
        "priority": 3,
        "min_results": 5
    },
    "recent_news": {
        "template": '"{company}" news announcement {year}',
        "domains": ["techcrunch.com", "venturebeat.com"],
        "priority": 3,
        "min_results": 5
    },
    "leadership": {
        "template": '"{company}" CEO executive leadership team management',
        "domains": ["linkedin.com", "forbes.com"],
        "priority": 3,
        "min_results": 3
    }
}


class QueryDiversifier:
    """
    Generate semantically diverse queries to maximize information coverage.

    Instead of similar queries returning overlapping results, generates
    queries for different information categories.
    """

    def __init__(self):
        self._seen_urls: Set[str] = set()
        try:
            from sentence_transformers import SentenceTransformer
            self._encoder = SentenceTransformer('all-MiniLM-L6-v2')
            self._embeddings: List = []
            self._use_embeddings = True
        except ImportError:
            logger.warning("sentence-transformers not installed, using URL-only deduplication")
            self._use_embeddings = False

    def generate_diverse_queries(
        self,
        company_name: str,
        competitors: Optional[List[str]] = None,
        industry: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[DiverseQuery]:
        """Generate diverse queries covering all categories."""
        if year is None:
            year = datetime.now().year

        queries = []

        for category, config in QUERY_CATEGORIES.items():
            query_text = config["template"].format(
                company=company_name,
                year=year
            )

            queries.append(DiverseQuery(
                query=query_text,
                category=category,
                expected_domains=config["domains"],
                min_results=config["min_results"],
                priority=config["priority"]
            ))

        # Add competitor comparison if competitors provided
        if competitors:
            for competitor in competitors[:2]:  # Top 2 competitors
                queries.append(DiverseQuery(
                    query=f'"{company_name}" vs "{competitor}" comparison',
                    category="competitive_analysis",
                    expected_domains=[],
                    min_results=3,
                    priority=2
                ))

        return sorted(queries, key=lambda q: q.priority)

    def is_duplicate(self, result: Dict[str, Any]) -> bool:
        """Check if result is duplicate (URL or semantic)."""
        url = result.get("url", "").lower().rstrip('/')

        # URL deduplication
        if url in self._seen_urls:
            return True

        # Semantic deduplication if enabled
        if self._use_embeddings:
            content = result.get("content", "") or result.get("snippet", "")
            if content and len(content) > 50:
                try:
                    import numpy as np
                    embedding = self._encoder.encode([content])[0]

                    for seen_emb in self._embeddings:
                        similarity = np.dot(embedding, seen_emb) / (
                            np.linalg.norm(embedding) * np.linalg.norm(seen_emb)
                        )
                        if similarity > 0.85:  # 85% similarity threshold
                            return True

                    self._embeddings.append(embedding)
                except Exception as e:
                    logger.debug(f"Embedding comparison failed: {e}")

        self._seen_urls.add(url)
        return False

    def reset(self):
        """Reset deduplication state for new search session."""
        self._seen_urls.clear()
        if self._use_embeddings:
            self._embeddings.clear()


class RobustSearchClient:
    """
    Search client with:
    1. Connection pooling (reuse instances)
    2. Adaptive health tracking
    3. Exponential backoff
    4. Calibrated scoring
    5. Category-based diversification
    6. Deduplication

    Usage:
        client = RobustSearchClient(config)
        results = await client.search_company("Apple Inc", competitors=["Microsoft"])
    """

    def __init__(self, config: Any = None):
        """Initialize search client."""
        self.config = config
        self.diversifier = QueryDiversifier()

        # Provider health tracking
        self._health: Dict[str, ProviderHealth] = {
            "duckduckgo": ProviderHealth(name="duckduckgo"),
            "serper": ProviderHealth(name="serper"),
            "brave": ProviderHealth(name="brave"),
            "google": ProviderHealth(name="google"),
            "tavily": ProviderHealth(name="tavily"),
        }

        # Connection pools
        self._ddgs_instance = None
        self._http_session = None

    async def search_company(
        self,
        company_name: str,
        competitors: Optional[List[str]] = None,
        industry: Optional[str] = None,
        providers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search with category-based diversification.

        Args:
            company_name: Company to research
            competitors: Known competitors (optional)
            industry: Industry sector (optional)
            providers: Specific providers to use (optional)

        Returns:
            Dict with results, coverage report, and metadata
        """
        providers = providers or ["duckduckgo", "serper", "tavily"]

        # Reset deduplication for new search
        self.diversifier.reset()

        # Generate diverse queries
        queries = self.diversifier.generate_diverse_queries(
            company_name, competitors, industry
        )

        all_results: List[SearchResult] = []
        category_results: Dict[str, List[SearchResult]] = {}

        for query in queries:
            category = query.category

            try:
                # Search with fallback across providers
                results = await self._search_with_fallback(
                    query=query.query,
                    providers=providers,
                    max_results=query.min_results * 2  # Get 2x, filter to unique
                )

                # Filter duplicates and score
                unique_results = []
                for raw in results:
                    if not self.diversifier.is_duplicate(raw):
                        result = SearchResult(
                            url=raw.get("href", raw.get("url", "")),
                            title=raw.get("title", ""),
                            snippet=raw.get("body", raw.get("snippet", "")),
                            provider=raw.get("provider", "unknown"),
                            raw_rank=len(unique_results),
                            category=category
                        )
                        result.calculate_combined_score(query.query)
                        unique_results.append(result)

                        if len(unique_results) >= query.min_results:
                            break

                category_results[category] = unique_results
                all_results.extend(unique_results)

                logger.info(
                    f"[{category}] Found {len(unique_results)} unique results "
                    f"(target: {query.min_results})"
                )

            except Exception as e:
                logger.error(f"Search failed for category {category}: {e}")
                category_results[category] = []

        # Generate coverage report
        coverage_report = self._generate_coverage_report(category_results)

        return {
            "results": [r.to_dict() for r in all_results],
            "by_category": {k: [r.to_dict() for r in v] for k, v in category_results.items()},
            "coverage_report": coverage_report,
            "total_results": len(all_results),
            "provider_health": self.get_health_report()
        }

    async def _search_with_fallback(
        self,
        query: str,
        providers: List[str],
        max_results: int
    ) -> List[Dict]:
        """Search with fallback across providers."""
        # Filter to healthy providers
        healthy_providers = [p for p in providers if self._health[p].is_healthy]

        if not healthy_providers:
            logger.warning("No healthy providers, resetting health")
            for h in self._health.values():
                h.consecutive_failures = 0
            healthy_providers = providers

        for provider in healthy_providers:
            try:
                start_time = datetime.now()
                results = await self._search_provider(provider, query, max_results)
                response_time = (datetime.now() - start_time).total_seconds() * 1000

                if results:
                    self._health[provider].record_success(response_time)
                    # Add provider info to results
                    for r in results:
                        r["provider"] = provider
                    return results

            except Exception as e:
                logger.warning(f"Provider {provider} failed: {e}")
                self._health[provider].record_failure()
                await self._exponential_backoff(provider)

        return []

    async def _search_provider(
        self,
        provider: str,
        query: str,
        max_results: int
    ) -> List[Dict]:
        """Execute search on specific provider."""
        if provider == "duckduckgo":
            return await self._search_duckduckgo(query, max_results)
        elif provider == "serper":
            return await self._search_serper(query, max_results)
        elif provider == "tavily":
            return await self._search_tavily(query, max_results)
        elif provider == "brave":
            return await self._search_brave(query, max_results)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict]:
        """Search using DuckDuckGo."""
        try:
            from duckduckgo_search import DDGS

            # Reuse instance
            if self._ddgs_instance is None:
                self._ddgs_instance = DDGS()

            results = await asyncio.to_thread(
                lambda: list(self._ddgs_instance.text(query, max_results=max_results))
            )
            return results

        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            # Reset instance on error
            self._ddgs_instance = None
            raise

    async def _search_serper(self, query: str, max_results: int) -> List[Dict]:
        """Search using Serper API."""
        api_key = getattr(self.config, 'serper_api_key', None) if self.config else None
        if not api_key:
            raise ValueError("Serper API key not configured")

        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": api_key},
                json={"q": query, "num": max_results}
            ) as response:
                data = await response.json()
                results = data.get("organic", [])
                return [
                    {
                        "href": r.get("link", ""),
                        "title": r.get("title", ""),
                        "body": r.get("snippet", "")
                    }
                    for r in results
                ]

    async def _search_tavily(self, query: str, max_results: int) -> List[Dict]:
        """Search using Tavily API."""
        api_key = getattr(self.config, 'tavily_api_key', None) if self.config else None
        if not api_key:
            raise ValueError("Tavily API key not configured")

        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": query,
                    "max_results": max_results
                }
            ) as response:
                data = await response.json()
                results = data.get("results", [])
                return [
                    {
                        "href": r.get("url", ""),
                        "title": r.get("title", ""),
                        "body": r.get("content", "")
                    }
                    for r in results
                ]

    async def _search_brave(self, query: str, max_results: int) -> List[Dict]:
        """Search using Brave API."""
        api_key = getattr(self.config, 'brave_api_key', None) if self.config else None
        if not api_key:
            raise ValueError("Brave API key not configured")

        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={"X-Subscription-Token": api_key},
                params={"q": query, "count": max_results}
            ) as response:
                data = await response.json()
                results = data.get("web", {}).get("results", [])
                return [
                    {
                        "href": r.get("url", ""),
                        "title": r.get("title", ""),
                        "body": r.get("description", "")
                    }
                    for r in results
                ]

    async def _exponential_backoff(self, provider: str):
        """Exponential backoff after failure."""
        failures = self._health[provider].consecutive_failures

        # Base delay: 1 second, max: 32 seconds
        delay = min(1 * (2 ** failures), 32)

        # Add jitter
        delay += random.uniform(0, delay * 0.1)

        logger.info(f"Backing off {provider} for {delay:.1f}s (failures: {failures})")
        await asyncio.sleep(delay)

    def _generate_coverage_report(
        self,
        category_results: Dict[str, List[SearchResult]]
    ) -> Dict[str, Any]:
        """Generate coverage report for search results."""
        report = {}

        for category, config in QUERY_CATEGORIES.items():
            results = category_results.get(category, [])
            target = config["min_results"]

            report[category] = {
                "found": len(results),
                "target": target,
                "coverage_pct": min(100, len(results) / target * 100) if target > 0 else 100,
                "gap": max(0, target - len(results)),
                "priority": config["priority"]
            }

        # Calculate overall coverage
        total_found = sum(r["found"] for r in report.values())
        total_target = sum(r["target"] for r in report.values())
        overall_coverage = (total_found / total_target * 100) if total_target > 0 else 0

        report["overall"] = {
            "total_found": total_found,
            "total_target": total_target,
            "coverage_pct": round(overall_coverage, 1)
        }

        return report

    def get_health_report(self) -> Dict[str, Dict]:
        """Get health report for all providers."""
        return {
            name: {
                "healthy": health.is_healthy,
                "success_rate": f"{health.success_rate:.1%}",
                "consecutive_failures": health.consecutive_failures,
                "avg_response_time_ms": f"{health.avg_response_time_ms:.0f}",
            }
            for name, health in self._health.items()
        }

    def reset_health(self):
        """Reset health tracking for all providers."""
        for health in self._health.values():
            health.consecutive_failures = 0
            health.last_failure = None
