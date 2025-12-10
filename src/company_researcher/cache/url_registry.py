"""
URL Registry - Track useful and useless URLs.

Maintains a persistent registry of all URLs encountered during research:
- Good URLs with quality scores and extracted content summaries
- Bad URLs with reasons (paywall, 404, irrelevant, etc.)
- Prevents re-fetching known bad URLs
- Enables learning from past research
"""

import json
import logging
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class URLStatus(str, Enum):
    """Status of a URL in the registry."""
    USEFUL = "useful"           # Good content, worth keeping
    USELESS = "useless"         # Bad content, skip in future
    PAYWALL = "paywall"         # Behind paywall
    NOT_FOUND = "not_found"     # 404 or similar
    BLOCKED = "blocked"         # Access denied
    TIMEOUT = "timeout"         # Request timed out
    IRRELEVANT = "irrelevant"   # Content not relevant to research
    DUPLICATE = "duplicate"     # Same content as another URL
    LOW_QUALITY = "low_quality" # Low quality source
    PENDING = "pending"         # Not yet evaluated


@dataclass
class URLRecord:
    """Record for a single URL."""
    url: str
    domain: str
    status: URLStatus
    first_seen: datetime
    last_checked: datetime
    check_count: int = 1

    # For useful URLs
    quality_score: float = 0.0
    content_summary: str = ""
    extracted_facts: List[str] = field(default_factory=list)
    companies_used_for: List[str] = field(default_factory=list)

    # For useless URLs
    useless_reason: str = ""
    error_message: str = ""

    # Metadata
    title: str = ""
    content_type: str = ""
    response_code: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "url": self.url,
            "domain": self.domain,
            "status": self.status.value,
            "first_seen": self.first_seen.isoformat(),
            "last_checked": self.last_checked.isoformat(),
            "check_count": self.check_count,
            "quality_score": self.quality_score,
            "content_summary": self.content_summary,
            "extracted_facts": self.extracted_facts,
            "companies_used_for": self.companies_used_for,
            "useless_reason": self.useless_reason,
            "error_message": self.error_message,
            "title": self.title,
            "content_type": self.content_type,
            "response_code": self.response_code,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "URLRecord":
        """Create from dictionary."""
        return cls(
            url=data["url"],
            domain=data["domain"],
            status=URLStatus(data["status"]),
            first_seen=datetime.fromisoformat(data["first_seen"]),
            last_checked=datetime.fromisoformat(data["last_checked"]),
            check_count=data.get("check_count", 1),
            quality_score=data.get("quality_score", 0.0),
            content_summary=data.get("content_summary", ""),
            extracted_facts=data.get("extracted_facts", []),
            companies_used_for=data.get("companies_used_for", []),
            useless_reason=data.get("useless_reason", ""),
            error_message=data.get("error_message", ""),
            title=data.get("title", ""),
            content_type=data.get("content_type", ""),
            response_code=data.get("response_code", 0),
        )


class URLRegistry:
    """
    Persistent registry of URLs encountered during research.

    Stores:
    - All URLs ever encountered
    - Quality scores for useful URLs
    - Reasons for useless URLs
    - Domain-level statistics

    Never deletes data - only updates and appends.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize URL registry.

        Args:
            storage_path: Path to storage directory. Defaults to .research_cache/
        """
        self.storage_path = storage_path or Path(".research_cache")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.urls_file = self.storage_path / "url_registry.json"
        self.domains_file = self.storage_path / "domain_stats.json"

        # In-memory caches
        self._urls: Dict[str, URLRecord] = {}
        self._domains: Dict[str, Dict[str, Any]] = {}
        self._useless_domains: Set[str] = set()

        # Load existing data
        self._load()

    def _load(self):
        """Load registry from disk."""
        # Load URLs
        if self.urls_file.exists():
            try:
                with open(self.urls_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for url_data in data.get("urls", []):
                        record = URLRecord.from_dict(url_data)
                        self._urls[record.url] = record
                logger.info(f"Loaded {len(self._urls)} URLs from registry")
            except Exception as e:
                logger.error(f"Failed to load URL registry: {e}")

        # Load domain stats
        if self.domains_file.exists():
            try:
                with open(self.domains_file, "r", encoding="utf-8") as f:
                    self._domains = json.load(f)

                # Build useless domains set
                for domain, stats in self._domains.items():
                    if stats.get("useless_ratio", 0) > 0.8:
                        self._useless_domains.add(domain)

                logger.info(f"Loaded {len(self._domains)} domain stats")
            except Exception as e:
                logger.error(f"Failed to load domain stats: {e}")

    def _save(self):
        """Save registry to disk."""
        # Save URLs
        try:
            data = {
                "version": "1.0",
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "total_urls": len(self._urls),
                "urls": [r.to_dict() for r in self._urls.values()]
            }
            with open(self.urls_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save URL registry: {e}")

        # Save domain stats
        try:
            with open(self.domains_file, "w", encoding="utf-8") as f:
                json.dump(self._domains, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save domain stats: {e}")

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return ""

    def _update_domain_stats(self, domain: str, status: URLStatus):
        """Update domain-level statistics."""
        if not domain:
            return

        if domain not in self._domains:
            self._domains[domain] = {
                "total_urls": 0,
                "useful_count": 0,
                "useless_count": 0,
                "useless_ratio": 0.0,
                "first_seen": datetime.now(timezone.utc).isoformat(),
                "last_seen": datetime.now(timezone.utc).isoformat(),
            }

        stats = self._domains[domain]
        stats["total_urls"] += 1
        stats["last_seen"] = datetime.now(timezone.utc).isoformat()

        if status == URLStatus.USEFUL:
            stats["useful_count"] += 1
        elif status in [URLStatus.USELESS, URLStatus.PAYWALL, URLStatus.BLOCKED,
                        URLStatus.IRRELEVANT, URLStatus.LOW_QUALITY]:
            stats["useless_count"] += 1

        # Calculate useless ratio
        if stats["total_urls"] > 0:
            stats["useless_ratio"] = stats["useless_count"] / stats["total_urls"]

        # Mark domain as useless if ratio is high
        if stats["useless_ratio"] > 0.8 and stats["total_urls"] >= 3:
            self._useless_domains.add(domain)

    # =========================================================================
    # Public API
    # =========================================================================

    def is_known_useless(self, url: str) -> bool:
        """
        Check if URL is known to be useless.

        Args:
            url: URL to check

        Returns:
            True if URL should be skipped
        """
        # Check exact URL
        if url in self._urls:
            record = self._urls[url]
            if record.status in [URLStatus.USELESS, URLStatus.PAYWALL,
                                 URLStatus.BLOCKED, URLStatus.NOT_FOUND,
                                 URLStatus.IRRELEVANT, URLStatus.LOW_QUALITY]:
                return True

        # Check if domain is mostly useless
        domain = self._extract_domain(url)
        if domain in self._useless_domains:
            return True

        return False

    def is_known_useful(self, url: str) -> bool:
        """Check if URL is known to be useful."""
        if url in self._urls:
            return self._urls[url].status == URLStatus.USEFUL
        return False

    def get_url_record(self, url: str) -> Optional[URLRecord]:
        """Get record for a URL if it exists."""
        return self._urls.get(url)

    def mark_useful(
        self,
        url: str,
        quality_score: float,
        content_summary: str = "",
        extracted_facts: Optional[List[str]] = None,
        company_name: str = "",
        title: str = "",
    ):
        """
        Mark a URL as useful.

        Args:
            url: The URL
            quality_score: Quality score (0-1)
            content_summary: Summary of useful content
            extracted_facts: List of facts extracted
            company_name: Company this was used for
            title: Page title
        """
        domain = self._extract_domain(url)
        now = datetime.now(timezone.utc)

        if url in self._urls:
            record = self._urls[url]
            record.status = URLStatus.USEFUL
            record.last_checked = now
            record.check_count += 1
            record.quality_score = max(record.quality_score, quality_score)
            if content_summary:
                record.content_summary = content_summary
            if extracted_facts:
                record.extracted_facts = list(set(record.extracted_facts + extracted_facts))
            if company_name and company_name not in record.companies_used_for:
                record.companies_used_for.append(company_name)
            if title:
                record.title = title
        else:
            record = URLRecord(
                url=url,
                domain=domain,
                status=URLStatus.USEFUL,
                first_seen=now,
                last_checked=now,
                quality_score=quality_score,
                content_summary=content_summary,
                extracted_facts=extracted_facts or [],
                companies_used_for=[company_name] if company_name else [],
                title=title,
            )
            self._urls[url] = record

        self._update_domain_stats(domain, URLStatus.USEFUL)
        self._save()

        logger.debug(f"Marked URL as useful: {url} (score: {quality_score})")

    def mark_useless(
        self,
        url: str,
        reason: str,
        status: URLStatus = URLStatus.USELESS,
        error_message: str = "",
        response_code: int = 0,
    ):
        """
        Mark a URL as useless.

        Args:
            url: The URL
            reason: Why it's useless
            status: Specific status (paywall, blocked, etc.)
            error_message: Error message if applicable
            response_code: HTTP response code
        """
        domain = self._extract_domain(url)
        now = datetime.now(timezone.utc)

        if url in self._urls:
            record = self._urls[url]
            record.status = status
            record.last_checked = now
            record.check_count += 1
            record.useless_reason = reason
            record.error_message = error_message
            record.response_code = response_code
        else:
            record = URLRecord(
                url=url,
                domain=domain,
                status=status,
                first_seen=now,
                last_checked=now,
                useless_reason=reason,
                error_message=error_message,
                response_code=response_code,
            )
            self._urls[url] = record

        self._update_domain_stats(domain, status)
        self._save()

        logger.debug(f"Marked URL as {status.value}: {url} ({reason})")

    def get_useful_urls_for_company(self, company_name: str) -> List[URLRecord]:
        """Get all useful URLs previously used for a company."""
        return [
            r for r in self._urls.values()
            if r.status == URLStatus.USEFUL
            and company_name in r.companies_used_for
        ]

    def get_useful_urls_by_domain(self, domain: str) -> List[URLRecord]:
        """Get all useful URLs from a domain."""
        return [
            r for r in self._urls.values()
            if r.domain == domain and r.status == URLStatus.USEFUL
        ]

    def get_useless_domains(self) -> Set[str]:
        """Get set of domains that are mostly useless."""
        return self._useless_domains.copy()

    def filter_urls(self, urls: List[str]) -> Dict[str, List[str]]:
        """
        Filter a list of URLs into categories.

        Args:
            urls: List of URLs to filter

        Returns:
            Dict with keys: "new", "useful", "useless", "skip"
        """
        result = {
            "new": [],      # Never seen before
            "useful": [],   # Known to be useful
            "useless": [],  # Known to be useless
            "skip": [],     # From useless domain
        }

        for url in urls:
            if url in self._urls:
                record = self._urls[url]
                if record.status == URLStatus.USEFUL:
                    result["useful"].append(url)
                else:
                    result["useless"].append(url)
            elif self._extract_domain(url) in self._useless_domains:
                result["skip"].append(url)
            else:
                result["new"].append(url)

        return result

    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        status_counts = {}
        for record in self._urls.values():
            status = record.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_urls": len(self._urls),
            "total_domains": len(self._domains),
            "useless_domains": len(self._useless_domains),
            "status_breakdown": status_counts,
            "storage_path": str(self.storage_path),
        }

    def print_summary(self):
        """Print a summary of the registry."""
        stats = self.get_statistics()
        print("\n" + "=" * 50)
        print("URL REGISTRY SUMMARY")
        print("=" * 50)
        print(f"Total URLs tracked: {stats['total_urls']}")
        print(f"Total domains: {stats['total_domains']}")
        print(f"Blacklisted domains: {stats['useless_domains']}")
        print("\nBy status:")
        for status, count in stats["status_breakdown"].items():
            print(f"  {status}: {count}")
        print("=" * 50)
