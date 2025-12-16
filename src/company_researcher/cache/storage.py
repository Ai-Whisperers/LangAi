"""
Research Cache Storage Service.

Contains the ResearchCache class for persistent storage of research data:
- Store research data by company (never delete)
- Track data freshness and quality
- Prevent redundant searches
- Enable incremental research
- Merge new data with existing data

Storage structure:
    .research_cache/
        url_registry.json       # All URLs encountered
        domain_stats.json       # Domain-level statistics
        companies/
            apple_inc/
                data.json       # All cached data
                sources.json    # Source tracking
                history.json    # Research history
            microsoft/
                ...

Usage:
    from company_researcher.cache.storage import ResearchCache, get_cache

    # Get global instance
    cache = get_cache()

    # Or create custom instance
    cache = ResearchCache(Path(".research_cache"))

    # Store data
    cache.store_company_data("Tesla Inc", "financials", {...})

    # Check for gaps
    gaps = cache.identify_gaps("Tesla Inc")
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils import get_logger
from .models import CachedCompanyData, CachedSource, DataCompleteness, SourceQuality

# Support both package and standalone imports
try:
    from .data_completeness import CompletenessChecker, CompletenessReport, DataSection
    from .url_registry import URLRegistry, URLStatus
except ImportError:
    from data_completeness import CompletenessChecker, CompletenessReport, DataSection
    from url_registry import URLRegistry, URLStatus

logger = get_logger(__name__)


class ResearchCache:
    """
    Persistent cache for all research data.

    Features:
    - Store all research data by company
    - Never delete data (only update/merge)
    - Track URL usefulness
    - Identify gaps in existing data
    - Prevent redundant research
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize research cache.

        Args:
            storage_path: Path to storage directory
        """
        self.storage_path = storage_path or Path(".research_cache")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.companies_path = self.storage_path / "companies"
        self.companies_path.mkdir(exist_ok=True)

        # Sub-components
        self.url_registry = URLRegistry(self.storage_path)
        self.completeness_checker = CompletenessChecker()

        # In-memory index of companies
        self._company_index: Dict[str, str] = {}  # normalized_name -> folder_name
        self._load_index()

        logger.info(f"Research cache initialized at {self.storage_path}")
        logger.info(f"Cached companies: {len(self._company_index)}")

    def _normalize_name(self, company_name: str) -> str:
        """Normalize company name for consistent lookup."""
        return company_name.lower().strip().replace(" ", "_").replace(".", "").replace(",", "")

    def _load_index(self):
        """Load company index from disk."""
        for folder in self.companies_path.iterdir():
            if folder.is_dir():
                data_file = folder / "data.json"
                if data_file.exists():
                    try:
                        with open(data_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            normalized = data.get("normalized_name", folder.name)
                            self._company_index[normalized] = folder.name
                    except Exception as e:
                        logger.warning(f"Failed to load {folder.name}: {e}")

    def _get_company_path(self, company_name: str) -> Path:
        """Get storage path for a company."""
        normalized = self._normalize_name(company_name)

        # Check if already indexed
        if normalized in self._company_index:
            folder_name = self._company_index[normalized]
        else:
            folder_name = normalized[:50]  # Limit folder name length
            self._company_index[normalized] = folder_name

        path = self.companies_path / folder_name
        path.mkdir(exist_ok=True)
        return path

    # =========================================================================
    # Core API
    # =========================================================================

    def has_company_data(self, company_name: str) -> bool:
        """Check if we have any cached data for a company."""
        normalized = self._normalize_name(company_name)
        return normalized in self._company_index

    def get_company_data(self, company_name: str) -> Optional[CachedCompanyData]:
        """
        Get all cached data for a company.

        Args:
            company_name: Company name

        Returns:
            CachedCompanyData if exists, None otherwise
        """
        if not self.has_company_data(company_name):
            return None

        path = self._get_company_path(company_name)
        data_file = path / "data.json"

        if not data_file.exists():
            return None

        try:
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return CachedCompanyData.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load company data: {e}")
            return None

    def identify_gaps(self, company_name: str) -> CompletenessReport:
        """
        Identify what data is missing for a company.

        Args:
            company_name: Company name

        Returns:
            CompletenessReport with gaps and recommendations
        """
        cached_data = self.get_company_data(company_name)

        if not cached_data:
            # No data at all - everything is a gap
            return self.completeness_checker.check_completeness(company_name, {})

        # Convert cached data to dict for completeness check
        data_dict = {
            "overview": cached_data.overview,
            "overview_updated": cached_data.section_updated.get("overview"),
            "financials": cached_data.financials,
            "financials_updated": cached_data.section_updated.get("financials"),
            "leadership": cached_data.leadership,
            "leadership_updated": cached_data.section_updated.get("leadership"),
            "products": cached_data.products,
            "products_updated": cached_data.section_updated.get("products"),
            "competitors": cached_data.competitors,
            "competitors_updated": cached_data.section_updated.get("competitors"),
            "market": cached_data.market,
            "market_updated": cached_data.section_updated.get("market"),
            "news": cached_data.news,
            "news_updated": cached_data.section_updated.get("news"),
            "esg": cached_data.esg,
            "esg_updated": cached_data.section_updated.get("esg"),
            "risks": cached_data.risks,
            "risks_updated": cached_data.section_updated.get("risks"),
        }

        return self.completeness_checker.check_completeness(company_name, data_dict)

    def get_research_priority(self, company_name: str) -> Dict[str, Any]:
        """
        Get prioritized research tasks for a company.

        Returns dict with high/medium priority sections and recommended sources.
        """
        report = self.identify_gaps(company_name)
        return self.completeness_checker.get_research_priority(report)

    def should_research(self, company_name: str, force: bool = False) -> Dict[str, Any]:
        """
        Determine if research is needed and what to research.

        Args:
            company_name: Company name
            force: Force research even if data exists

        Returns:
            Dict with:
            - needs_research: bool
            - reason: str
            - priority_sections: list
            - skip_sections: list
            - existing_completeness: float
        """
        if force:
            return {
                "needs_research": True,
                "reason": "Forced research",
                "priority_sections": [s.value for s in DataSection],
                "skip_sections": [],
                "existing_completeness": 0.0,
            }

        if not self.has_company_data(company_name):
            return {
                "needs_research": True,
                "reason": "No existing data",
                "priority_sections": [s.value for s in DataSection],
                "skip_sections": [],
                "existing_completeness": 0.0,
            }

        report = self.identify_gaps(company_name)
        priority = self.completeness_checker.get_research_priority(report)

        return {
            "needs_research": report.needs_research,
            "reason": "Data gaps detected" if report.needs_research else "Data complete",
            "priority_sections": priority["high_priority"] + priority["medium_priority"],
            "skip_sections": priority["skip"],
            "existing_completeness": report.overall_completeness,
            "recommendations": report.recommendations,
        }

    # =========================================================================
    # Data Storage
    # =========================================================================

    def store_company_data(
        self,
        company_name: str,
        section: str,
        data: Dict[str, Any],
        sources: Optional[List[Dict]] = None,
        merge: bool = True,
    ):
        """
        Store data for a company section.

        Args:
            company_name: Company name
            section: Section name (overview, financials, etc.)
            data: Data to store
            sources: Sources used
            merge: If True, merge with existing data; if False, replace
        """
        now = datetime.now(timezone.utc)
        path = self._get_company_path(company_name)
        data_file = path / "data.json"

        # Load existing or create new
        existing = self.get_company_data(company_name)
        if existing:
            cached = existing
            cached.research_count += 1
            cached.last_updated = now
        else:
            cached = CachedCompanyData(
                company_name=company_name,
                normalized_name=self._normalize_name(company_name),
                first_researched=now,
                last_updated=now,
            )

        # Update section
        section_attr = getattr(cached, section, None)
        if section_attr is not None:
            if merge and isinstance(section_attr, dict):
                # Merge with existing
                section_attr.update(data)
                setattr(cached, section, section_attr)
            else:
                setattr(cached, section, data)
        else:
            logger.warning(f"Unknown section: {section}")

        cached.section_updated[section] = now

        # Add sources
        if sources:
            for src in sources:
                cached_source = CachedSource(
                    url=src.get("url", ""),
                    title=src.get("title", ""),
                    domain=self._extract_domain(src.get("url", "")),
                    quality=SourceQuality(src.get("quality", "unknown")),
                    used_for=[section],
                    extracted_at=now,
                    relevance_score=src.get("score", 0.0),
                )
                cached.sources.append(cached_source)

                # Mark URL as useful in registry
                self.url_registry.mark_useful(
                    url=cached_source.url,
                    quality_score=cached_source.relevance_score,
                    company_name=company_name,
                    title=cached_source.title,
                )

        # Update completeness
        cached.completeness = self._calculate_completeness(cached)

        # Save
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(cached.to_dict(), f, indent=2)

        logger.info(f"Stored {section} data for {company_name}")

    def store_search_results(
        self,
        company_name: str,
        results: List[Dict],
        evaluate_quality: bool = True,
    ):
        """
        Store search results and evaluate URL quality.

        Args:
            company_name: Company being researched
            results: Search results from Tavily or similar
            evaluate_quality: If True, mark URLs as useful/useless
        """
        for result in results:
            url = result.get("url", "")
            if not url:
                continue

            score = result.get("score", 0.5)
            content = result.get("content", "")

            if evaluate_quality:
                if score > 0.6 and len(content) > 100:
                    self.url_registry.mark_useful(
                        url=url,
                        quality_score=score,
                        content_summary=content[:500],
                        company_name=company_name,
                        title=result.get("title", ""),
                    )
                elif score < 0.3 or len(content) < 50:
                    self.url_registry.mark_useless(
                        url=url,
                        reason="Low relevance score" if score < 0.3 else "Insufficient content",
                        status=URLStatus.LOW_QUALITY,
                    )

    def mark_url_useless(
        self,
        url: str,
        reason: str,
        status: URLStatus = URLStatus.USELESS,
    ):
        """Mark a URL as useless (paywall, blocked, irrelevant, etc.)."""
        self.url_registry.mark_useless(url, reason, status)

    def filter_urls(self, urls: List[str]) -> Dict[str, List[str]]:
        """
        Filter URLs based on registry.

        Returns dict with: new, useful, useless, skip
        """
        return self.url_registry.filter_urls(urls)

    def is_url_useless(self, url: str) -> bool:
        """Check if URL should be skipped."""
        return self.url_registry.is_known_useless(url)

    # =========================================================================
    # Bulk Operations
    # =========================================================================

    def store_full_research(
        self,
        company_name: str,
        research_data: Dict[str, Any],
        sources: List[Dict],
    ):
        """
        Store complete research results.

        Args:
            company_name: Company name
            research_data: Full research data with all sections
            sources: All sources used
        """
        section_mapping = {
            "company_overview": "overview",
            "overview": "overview",
            "financial_data": "financials",
            "financials": "financials",
            "leadership": "leadership",
            "products_services": "products",
            "products": "products",
            "competitors": "competitors",
            "market": "market",
            "news": "news",
            "news_sentiment": "news",
            "esg": "esg",
            "risk_profile": "risks",
            "risks": "risks",
            "contacts": "contacts",
            "social": "social",
        }

        for key, data in research_data.items():
            if key in section_mapping and data:
                section = section_mapping[key]
                section_sources = [
                    s for s in sources if section in s.get("used_for", []) or not s.get("used_for")
                ]
                self.store_company_data(
                    company_name=company_name,
                    section=section,
                    data=data if isinstance(data, dict) else {"content": data},
                    sources=section_sources,
                )

        # Store raw results for audit
        self._store_research_history(company_name, research_data, sources)

    def _store_research_history(
        self,
        company_name: str,
        data: Dict,
        sources: List[Dict],
    ):
        """Store research history for audit trail."""
        path = self._get_company_path(company_name)
        history_file = path / "history.json"

        history = []
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception as e:
                logger.debug(f"Failed to load history for {company_name}: {e}")

        history.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "sections_updated": list(data.keys()),
                "sources_count": len(sources),
            }
        )

        # Keep last 100 entries
        history = history[-100:]

        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

    # =========================================================================
    # Helpers
    # =========================================================================

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse

            return urlparse(url).netloc.lower()
        except Exception:
            return ""

    def _calculate_completeness(self, data: CachedCompanyData) -> DataCompleteness:
        """Calculate completeness level."""
        scores = []

        # Check each section
        if data.overview:
            scores.append(1.0)
        if data.financials:
            scores.append(1.0)
        if data.leadership:
            scores.append(0.5)
        if data.products:
            scores.append(1.0)
        if data.competitors:
            scores.append(0.5)
        if data.market:
            scores.append(0.5)
        if data.news:
            scores.append(0.3)

        if not scores:
            return DataCompleteness.EMPTY

        avg = sum(scores) / 7  # Weighted by importance

        if avg >= 0.8:
            return DataCompleteness.COMPLETE
        elif avg >= 0.6:
            return DataCompleteness.SUBSTANTIAL
        elif avg >= 0.3:
            return DataCompleteness.PARTIAL
        else:
            return DataCompleteness.MINIMAL

    # =========================================================================
    # Statistics
    # =========================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics."""
        url_stats = self.url_registry.get_statistics()

        company_stats = {
            "total_companies": len(self._company_index),
            "companies": list(self._company_index.keys()),
        }

        return {
            "storage_path": str(self.storage_path),
            "companies": company_stats,
            "urls": url_stats,
        }

    def print_summary(self):
        """Print cache summary."""
        stats = self.get_statistics()

        print("\n" + "=" * 60)
        print("RESEARCH CACHE SUMMARY")
        print("=" * 60)
        print(f"Storage: {stats['storage_path']}")
        print(f"\nCompanies cached: {stats['companies']['total_companies']}")

        for name in list(stats["companies"]["companies"])[:10]:
            data = self.get_company_data(name.replace("_", " "))
            if data:
                print(f"  - {data.company_name}: {data.completeness.value}")

        if stats["companies"]["total_companies"] > 10:
            print(f"  ... and {stats['companies']['total_companies'] - 10} more")

        print(f"\nURLs tracked: {stats['urls']['total_urls']}")
        print(f"Domains: {stats['urls']['total_domains']}")
        print(f"Blacklisted domains: {stats['urls']['useless_domains']}")
        print("=" * 60)


# =========================================================================
# Module-level cache instance
# =========================================================================

_cache_instance: Optional[ResearchCache] = None


def get_cache() -> ResearchCache:
    """Get the global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = ResearchCache()
    return _cache_instance


def create_cache(storage_path: Optional[Path] = None) -> ResearchCache:
    """Create a new cache instance."""
    global _cache_instance
    _cache_instance = ResearchCache(storage_path)
    return _cache_instance
