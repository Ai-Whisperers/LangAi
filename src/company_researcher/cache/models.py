"""
Research Cache Data Models.

Contains enums and dataclasses for research cache storage:
- SourceQuality enum: Quality tiers for data sources
- DataCompleteness enum: Completeness levels for company data
- CachedSource dataclass: Source metadata
- CachedCompanyData dataclass: Comprehensive company research data

Usage:
    from company_researcher.cache.models import (
        SourceQuality,
        DataCompleteness,
        CachedSource,
        CachedCompanyData,
    )

    source = CachedSource(
        url="https://example.com",
        title="Company Report",
        domain="example.com",
        quality=SourceQuality.HIGH,
        used_for=["financials", "overview"],
        extracted_at=datetime.now(timezone.utc)
    )
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class SourceQuality(str, Enum):
    """Quality tier of a data source."""
    PRIMARY = "primary"         # Official sources (SEC, company website)
    HIGH = "high"               # Reputable news, financial APIs
    MEDIUM = "medium"           # General web search results
    LOW = "low"                 # User-generated, unverified
    UNKNOWN = "unknown"


class DataCompleteness(str, Enum):
    """Completeness level of company data."""
    COMPLETE = "complete"       # All major sections present
    SUBSTANTIAL = "substantial" # Most important data present
    PARTIAL = "partial"         # Some data but major gaps
    MINIMAL = "minimal"         # Very little data
    EMPTY = "empty"             # No data


@dataclass
class CachedSource:
    """A source used in cached research."""
    url: str
    title: str
    domain: str
    quality: SourceQuality
    used_for: List[str]  # Which sections
    extracted_at: datetime
    relevance_score: float = 0.0
    content_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "domain": self.domain,
            "quality": self.quality.value,
            "used_for": self.used_for,
            "extracted_at": self.extracted_at.isoformat(),
            "relevance_score": self.relevance_score,
            "content_hash": self.content_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CachedSource":
        return cls(
            url=data["url"],
            title=data["title"],
            domain=data["domain"],
            quality=SourceQuality(data.get("quality", "unknown")),
            used_for=data.get("used_for", []),
            extracted_at=datetime.fromisoformat(data["extracted_at"]),
            relevance_score=data.get("relevance_score", 0.0),
            content_hash=data.get("content_hash", ""),
        )


@dataclass
class CachedCompanyData:
    """Cached research data for a company."""
    company_name: str
    normalized_name: str
    first_researched: datetime
    last_updated: datetime
    research_count: int = 1
    completeness: DataCompleteness = DataCompleteness.EMPTY

    # Core data sections
    overview: Dict[str, Any] = field(default_factory=dict)
    financials: Dict[str, Any] = field(default_factory=dict)
    leadership: Dict[str, Any] = field(default_factory=dict)
    products: Dict[str, Any] = field(default_factory=dict)
    competitors: Dict[str, Any] = field(default_factory=dict)
    market: Dict[str, Any] = field(default_factory=dict)
    news: Dict[str, Any] = field(default_factory=dict)
    esg: Dict[str, Any] = field(default_factory=dict)
    risks: Dict[str, Any] = field(default_factory=dict)
    contacts: Dict[str, Any] = field(default_factory=dict)
    social: Dict[str, Any] = field(default_factory=dict)

    # Section timestamps
    section_updated: Dict[str, datetime] = field(default_factory=dict)

    # Sources used
    sources: List[CachedSource] = field(default_factory=list)

    # Metadata
    ticker: Optional[str] = None
    region: Optional[str] = None
    industry: Optional[str] = None
    is_public: bool = False

    # Raw notes (for debugging/audit)
    raw_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "company_name": self.company_name,
            "normalized_name": self.normalized_name,
            "first_researched": self.first_researched.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "research_count": self.research_count,
            "completeness": self.completeness.value,
            "overview": self.overview,
            "financials": self.financials,
            "leadership": self.leadership,
            "products": self.products,
            "competitors": self.competitors,
            "market": self.market,
            "news": self.news,
            "esg": self.esg,
            "risks": self.risks,
            "contacts": self.contacts,
            "social": self.social,
            "section_updated": {k: v.isoformat() for k, v in self.section_updated.items()},
            "sources": [s.to_dict() for s in self.sources],
            "ticker": self.ticker,
            "region": self.region,
            "industry": self.industry,
            "is_public": self.is_public,
            "raw_notes": self.raw_notes[-100:],  # Keep last 100 notes
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CachedCompanyData":
        """Create from dictionary."""
        section_updated = {}
        for k, v in data.get("section_updated", {}).items():
            try:
                section_updated[k] = datetime.fromisoformat(v)
            except Exception:
                pass

        return cls(
            company_name=data["company_name"],
            normalized_name=data["normalized_name"],
            first_researched=datetime.fromisoformat(data["first_researched"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            research_count=data.get("research_count", 1),
            completeness=DataCompleteness(data.get("completeness", "empty")),
            overview=data.get("overview", {}),
            financials=data.get("financials", {}),
            leadership=data.get("leadership", {}),
            products=data.get("products", {}),
            competitors=data.get("competitors", {}),
            market=data.get("market", {}),
            news=data.get("news", {}),
            esg=data.get("esg", {}),
            risks=data.get("risks", {}),
            contacts=data.get("contacts", {}),
            social=data.get("social", {}),
            section_updated=section_updated,
            sources=[CachedSource.from_dict(s) for s in data.get("sources", [])],
            ticker=data.get("ticker"),
            region=data.get("region"),
            industry=data.get("industry"),
            is_public=data.get("is_public", False),
            raw_notes=data.get("raw_notes", []),
        )
