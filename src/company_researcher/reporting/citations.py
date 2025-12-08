"""
Citation and Source Links - Source tracking and citation formatting.

Provides:
- Source metadata enrichment
- Relevance scoring
- Citation formatting
- Source quality indicators
"""

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


class SourceType(str, Enum):
    """Types of sources."""
    OFFICIAL = "official"  # Company website, SEC filings
    NEWS = "news"  # News articles
    FINANCIAL = "financial"  # Financial data providers
    SOCIAL = "social"  # Social media
    RESEARCH = "research"  # Research reports
    ACADEMIC = "academic"  # Academic papers
    GOVERNMENT = "government"  # Government sources
    OTHER = "other"


class SourceQuality(str, Enum):
    """Quality rating of sources."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class Source:
    """A research source with metadata."""
    url: str
    title: str
    source_type: SourceType = SourceType.OTHER
    quality: SourceQuality = SourceQuality.UNKNOWN
    domain: str = ""
    accessed_at: datetime = field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    author: Optional[str] = None
    relevance_score: float = 0.0
    snippet: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.domain:
            self.domain = urlparse(self.url).netloc

    @property
    def age_days(self) -> Optional[int]:
        """Get age in days since publication."""
        if self.published_at:
            return (datetime.utcnow() - self.published_at).days
        return None

    @property
    def freshness_label(self) -> str:
        """Get freshness label."""
        age = self.age_days
        if age is None:
            return "Unknown"
        if age <= 1:
            return "Today"
        if age <= 7:
            return "This Week"
        if age <= 30:
            return "This Month"
        if age <= 90:
            return "Recent"
        if age <= 365:
            return "This Year"
        return "Older"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "domain": self.domain,
            "source_type": self.source_type.value,
            "quality": self.quality.value,
            "accessed_at": self.accessed_at.isoformat(),
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "author": self.author,
            "relevance_score": self.relevance_score,
            "freshness": self.freshness_label,
            "snippet": self.snippet[:200] if self.snippet else ""
        }


@dataclass
class Citation:
    """A citation reference."""
    id: str
    source: Source
    context: str  # Where this citation is used
    claim: str  # What claim it supports
    confidence: float = 1.0

    def to_inline(self) -> str:
        """Get inline citation marker."""
        return f"[{self.id}]"

    def to_footnote(self) -> str:
        """Get footnote format."""
        date = self.source.published_at.strftime("%Y") if self.source.published_at else "n.d."
        return f"[{self.id}] {self.source.title}. {self.source.domain}. {date}. {self.source.url}"

    def to_apa(self) -> str:
        """Get APA format citation."""
        author = self.source.author or self.source.domain
        date = self.source.published_at.strftime("%Y, %B %d") if self.source.published_at else "n.d."
        return f"{author}. ({date}). {self.source.title}. Retrieved from {self.source.url}"

    def to_markdown_link(self) -> str:
        """Get markdown link format."""
        return f"[{self.source.title}]({self.source.url})"


class SourceClassifier:
    """Classifies sources by type and quality."""

    # Domain patterns for classification
    DOMAIN_PATTERNS = {
        SourceType.OFFICIAL: [
            r"\.gov$", r"\.edu$", r"sec\.gov", r"investor\.", r"ir\.",
            r"tesla\.com", r"apple\.com", r"microsoft\.com", r"google\.com"
        ],
        SourceType.NEWS: [
            r"reuters\.", r"bloomberg\.", r"wsj\.", r"nytimes\.",
            r"ft\.com", r"cnbc\.", r"bbc\.", r"theguardian\."
        ],
        SourceType.FINANCIAL: [
            r"yahoo\.finance", r"marketwatch\.", r"morningstar\.",
            r"seekingalpha\.", r"fool\.", r"investopedia\."
        ],
        SourceType.SOCIAL: [
            r"twitter\.", r"x\.com", r"linkedin\.", r"reddit\.",
            r"facebook\.", r"instagram\."
        ],
        SourceType.RESEARCH: [
            r"mckinsey\.", r"deloitte\.", r"pwc\.", r"kpmg\.",
            r"gartner\.", r"forrester\.", r"idc\."
        ],
        SourceType.ACADEMIC: [
            r"arxiv\.", r"scholar\.google", r"researchgate\.",
            r"sciencedirect\.", r"springer\.", r"nature\."
        ]
    }

    # Quality scores by domain
    HIGH_QUALITY_DOMAINS = {
        "sec.gov", "reuters.com", "bloomberg.com", "wsj.com",
        "ft.com", "nytimes.com", "gov", "edu"
    }

    MEDIUM_QUALITY_DOMAINS = {
        "cnbc.com", "bbc.com", "yahoo.com", "morningstar.com",
        "seekingalpha.com", "marketwatch.com"
    }

    def classify_type(self, url: str) -> SourceType:
        """Classify source type from URL."""
        domain = urlparse(url).netloc.lower()

        for source_type, patterns in self.DOMAIN_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, domain):
                    return source_type

        return SourceType.OTHER

    def assess_quality(self, url: str, source_type: SourceType = None) -> SourceQuality:
        """Assess source quality from URL."""
        domain = urlparse(url).netloc.lower()

        # High quality sources
        if any(hq in domain for hq in self.HIGH_QUALITY_DOMAINS):
            return SourceQuality.HIGH

        # Medium quality sources
        if any(mq in domain for mq in self.MEDIUM_QUALITY_DOMAINS):
            return SourceQuality.MEDIUM

        # Official sources are generally high quality
        if source_type == SourceType.OFFICIAL:
            return SourceQuality.HIGH

        # Academic and government are high quality
        if source_type in [SourceType.ACADEMIC, SourceType.GOVERNMENT]:
            return SourceQuality.HIGH

        # News from major outlets is medium-high
        if source_type == SourceType.NEWS:
            return SourceQuality.MEDIUM

        return SourceQuality.UNKNOWN


class RelevanceScorer:
    """Scores relevance of sources to research queries."""

    def score(
        self,
        source: Source,
        query: str,
        company_name: str
    ) -> float:
        """
        Score source relevance.

        Args:
            source: Source to score
            query: Research query
            company_name: Company being researched

        Returns:
            Relevance score 0-1
        """
        score = 0.0
        weights = {
            "title_match": 0.3,
            "snippet_match": 0.2,
            "quality": 0.2,
            "freshness": 0.15,
            "domain_trust": 0.15
        }

        # Title match
        if self._text_match(source.title, company_name, query):
            score += weights["title_match"]

        # Snippet match
        if self._text_match(source.snippet, company_name, query):
            score += weights["snippet_match"]

        # Quality bonus
        quality_scores = {
            SourceQuality.HIGH: 1.0,
            SourceQuality.MEDIUM: 0.6,
            SourceQuality.LOW: 0.2,
            SourceQuality.UNKNOWN: 0.4
        }
        score += weights["quality"] * quality_scores.get(source.quality, 0.4)

        # Freshness bonus
        age = source.age_days
        if age is not None:
            if age <= 7:
                score += weights["freshness"]
            elif age <= 30:
                score += weights["freshness"] * 0.8
            elif age <= 90:
                score += weights["freshness"] * 0.5
            elif age <= 365:
                score += weights["freshness"] * 0.2

        # Domain trust bonus
        if source.source_type in [SourceType.OFFICIAL, SourceType.FINANCIAL, SourceType.NEWS]:
            score += weights["domain_trust"]

        return min(score, 1.0)

    def _text_match(self, text: str, company_name: str, query: str) -> bool:
        """Check if text contains relevant matches."""
        if not text:
            return False
        text_lower = text.lower()
        return (
            company_name.lower() in text_lower or
            any(word.lower() in text_lower for word in query.split() if len(word) > 3)
        )


class CitationManager:
    """
    Manages citations and source tracking.

    Usage:
        manager = CitationManager()

        # Add sources from search results
        for result in search_results:
            source = manager.add_source(
                url=result["url"],
                title=result["title"],
                snippet=result["snippet"]
            )

        # Create citation for a claim
        citation = manager.cite(
            source_url=result["url"],
            claim="Tesla's revenue grew 25% YoY",
            context="Financial analysis section"
        )

        # Get formatted citations
        bibliography = manager.get_bibliography()
        inline = citation.to_inline()
    """

    def __init__(self):
        self._sources: Dict[str, Source] = {}
        self._citations: List[Citation] = []
        self._citation_counter = 0
        self._classifier = SourceClassifier()
        self._scorer = RelevanceScorer()

    def add_source(
        self,
        url: str,
        title: str,
        snippet: str = "",
        published_at: datetime = None,
        author: str = None,
        metadata: Dict[str, Any] = None
    ) -> Source:
        """
        Add a source.

        Args:
            url: Source URL
            title: Source title
            snippet: Text snippet
            published_at: Publication date
            author: Author name
            metadata: Additional metadata

        Returns:
            Created or existing Source
        """
        # Check if already exists
        source_id = self._generate_source_id(url)
        if source_id in self._sources:
            return self._sources[source_id]

        # Classify source
        source_type = self._classifier.classify_type(url)
        quality = self._classifier.assess_quality(url, source_type)

        source = Source(
            url=url,
            title=title,
            source_type=source_type,
            quality=quality,
            published_at=published_at,
            author=author,
            snippet=snippet,
            metadata=metadata or {}
        )

        self._sources[source_id] = source
        return source

    def add_sources_from_search(
        self,
        search_results: List[Dict[str, Any]],
        company_name: str = "",
        query: str = ""
    ) -> List[Source]:
        """Add multiple sources from search results."""
        sources = []
        for result in search_results:
            source = self.add_source(
                url=result.get("url", ""),
                title=result.get("title", ""),
                snippet=result.get("snippet", result.get("content", "")),
                published_at=self._parse_date(result.get("published_date")),
                author=result.get("author"),
                metadata=result
            )

            # Score relevance
            if company_name or query:
                source.relevance_score = self._scorer.score(source, query, company_name)

            sources.append(source)

        return sources

    def cite(
        self,
        source_url: str,
        claim: str,
        context: str = "",
        confidence: float = 1.0
    ) -> Optional[Citation]:
        """
        Create a citation for a source.

        Args:
            source_url: URL of source to cite
            claim: The claim being supported
            context: Where citation is used
            confidence: Confidence in citation accuracy

        Returns:
            Citation object or None if source not found
        """
        source_id = self._generate_source_id(source_url)
        source = self._sources.get(source_id)

        if not source:
            return None

        self._citation_counter += 1
        citation = Citation(
            id=str(self._citation_counter),
            source=source,
            context=context,
            claim=claim,
            confidence=confidence
        )

        self._citations.append(citation)
        return citation

    def get_source(self, url: str) -> Optional[Source]:
        """Get source by URL."""
        source_id = self._generate_source_id(url)
        return self._sources.get(source_id)

    def get_all_sources(self) -> List[Source]:
        """Get all sources."""
        return list(self._sources.values())

    def get_citations(self) -> List[Citation]:
        """Get all citations."""
        return self._citations

    def get_bibliography(self, format: str = "markdown") -> str:
        """
        Generate bibliography.

        Args:
            format: Output format (markdown, text, apa)

        Returns:
            Formatted bibliography string
        """
        # Get unique sources that were cited
        cited_sources = {c.source.url: c.source for c in self._citations}
        sources = sorted(cited_sources.values(), key=lambda s: s.title)

        if format == "markdown":
            return self._format_markdown_bibliography(sources)
        elif format == "apa":
            return self._format_apa_bibliography(sources)
        else:
            return self._format_text_bibliography(sources)

    def get_inline_citations(self) -> Dict[str, str]:
        """Get map of claims to inline citations."""
        return {c.claim: c.to_inline() for c in self._citations}

    def get_sources_by_quality(self) -> Dict[SourceQuality, List[Source]]:
        """Group sources by quality."""
        by_quality = {q: [] for q in SourceQuality}
        for source in self._sources.values():
            by_quality[source.quality].append(source)
        return by_quality

    def get_sources_by_type(self) -> Dict[SourceType, List[Source]]:
        """Group sources by type."""
        by_type = {t: [] for t in SourceType}
        for source in self._sources.values():
            by_type[source.source_type].append(source)
        return by_type

    def get_source_statistics(self) -> Dict[str, Any]:
        """Get source statistics."""
        sources = list(self._sources.values())
        by_quality = self.get_sources_by_quality()
        by_type = self.get_sources_by_type()

        return {
            "total_sources": len(sources),
            "total_citations": len(self._citations),
            "quality_distribution": {
                q.value: len(sources) for q, sources in by_quality.items()
            },
            "type_distribution": {
                t.value: len(sources) for t, sources in by_type.items()
            },
            "average_relevance": (
                sum(s.relevance_score for s in sources) / len(sources)
                if sources else 0
            ),
            "high_quality_percentage": (
                len(by_quality[SourceQuality.HIGH]) / len(sources) * 100
                if sources else 0
            )
        }

    def _generate_source_id(self, url: str) -> str:
        """Generate unique ID for source."""
        normalized = url.lower().strip().rstrip("/")
        return hashlib.md5(normalized.encode()).hexdigest()[:12]

    def _parse_date(self, date_str: Any) -> Optional[datetime]:
        """Parse date string to datetime."""
        if not date_str:
            return None
        if isinstance(date_str, datetime):
            return date_str
        try:
            from dateutil import parser
            return parser.parse(str(date_str))
        except Exception:
            return None

    def _format_markdown_bibliography(self, sources: List[Source]) -> str:
        """Format bibliography as markdown."""
        lines = ["## Sources\n"]
        for i, source in enumerate(sources, 1):
            quality_badge = self._quality_badge(source.quality)
            freshness = f"({source.freshness_label})" if source.published_at else ""
            lines.append(
                f"{i}. [{source.title}]({source.url}) - {source.domain} "
                f"{quality_badge} {freshness}"
            )
        return "\n".join(lines)

    def _format_apa_bibliography(self, sources: List[Source]) -> str:
        """Format bibliography in APA style."""
        lines = ["References\n"]
        for source in sources:
            author = source.author or source.domain
            date = source.published_at.strftime("%Y, %B %d") if source.published_at else "n.d."
            lines.append(f"{author}. ({date}). {source.title}. Retrieved from {source.url}\n")
        return "\n".join(lines)

    def _format_text_bibliography(self, sources: List[Source]) -> str:
        """Format bibliography as plain text."""
        lines = ["SOURCES\n" + "=" * 40 + "\n"]
        for i, source in enumerate(sources, 1):
            lines.append(f"{i}. {source.title}")
            lines.append(f"   URL: {source.url}")
            lines.append(f"   Type: {source.source_type.value}")
            lines.append(f"   Quality: {source.quality.value}")
            lines.append("")
        return "\n".join(lines)

    def _quality_badge(self, quality: SourceQuality) -> str:
        """Get quality badge."""
        badges = {
            SourceQuality.HIGH: "[HIGH]",
            SourceQuality.MEDIUM: "[MED]",
            SourceQuality.LOW: "[LOW]",
            SourceQuality.UNKNOWN: "[?]"
        }
        return badges.get(quality, "")


# Convenience functions

def create_citation_manager() -> CitationManager:
    """Create a citation manager."""
    return CitationManager()


def classify_source(url: str) -> Dict[str, str]:
    """Classify a source URL."""
    classifier = SourceClassifier()
    source_type = classifier.classify_type(url)
    quality = classifier.assess_quality(url, source_type)
    return {
        "url": url,
        "type": source_type.value,
        "quality": quality.value
    }
