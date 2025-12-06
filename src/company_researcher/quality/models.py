"""
Quality system data models (Phase 5).

This module defines the core data structures for source tracking,
quality assessment, and fact verification.
"""

from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from enum import Enum
from typing import Optional


# ============================================================================
# Enumerations
# ============================================================================

class SourceQuality(str, Enum):
    """Source quality tiers for automatic assessment."""

    OFFICIAL = "OFFICIAL"              # .gov, .edu, investor relations
    AUTHORITATIVE = "AUTHORITATIVE"    # Bloomberg, Reuters, WSJ
    REPUTABLE = "REPUTABLE"            # Forbes, TechCrunch, CNBC
    COMMUNITY = "COMMUNITY"            # Reddit, HN, forums
    UNKNOWN = "UNKNOWN"                # Unverified sources


class ConfidenceLevel(str, Enum):
    """Confidence levels for research facts."""

    HIGH = "HIGH"        # Multiple authoritative sources
    MEDIUM = "MEDIUM"    # Single authoritative or multiple reputable
    LOW = "LOW"          # Community sources or unverified


# ============================================================================
# Core Models
# ============================================================================

class Source(BaseModel):
    """Metadata for a research source.

    Tracks URL, title, retrieval timestamp, and automatic quality assessment.
    """

    url: str
    title: str
    retrieved_at: datetime = Field(default_factory=datetime.now)
    quality: SourceQuality = SourceQuality.UNKNOWN
    quality_score: float = Field(ge=0, le=100, default=30)  # 0-100

    class Config:
        use_enum_values = True

    def __str__(self) -> str:
        """Format source for display."""
        return f"[{self.title}]({self.url}) - {self.quality} ({self.quality_score:.0f}/100)"

    def to_markdown(self) -> str:
        """Format as markdown citation."""
        timestamp = self.retrieved_at.strftime("%Y-%m-%d")
        return f"- [{self.title}]({self.url}) (Retrieved {timestamp}, Quality: {self.quality_score:.0f}/100)"


class ResearchFact(BaseModel):
    """A verified fact with source attribution.

    Represents a single piece of information extracted by an agent
    with full source tracking and confidence assessment.
    """

    content: str
    source: Source
    extracted_by: str  # Agent name (e.g., "financial", "market")
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    verified: bool = False
    verified_by: Optional[str] = None  # Agent that verified this fact
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True

    def __str__(self) -> str:
        """Format fact for display."""
        verified_marker = "✅" if self.verified else "❌"
        return f"{verified_marker} {self.content} (Confidence: {self.confidence})"

    def to_markdown(self) -> str:
        """Format as markdown."""
        verified_marker = "✅" if self.verified else "❌"
        return f"""
**Fact:** {self.content}
**Source:** {self.source}
**Confidence:** {self.confidence}
**Verified:** {verified_marker}
**Extracted by:** {self.extracted_by}
"""


class QualityReport(BaseModel):
    """Comprehensive quality assessment report.

    Contains multi-factor quality scores and detailed metrics
    for a research session.
    """

    overall_score: float = Field(ge=0, le=100)
    source_quality_score: float = Field(ge=0, le=100)
    verification_rate: float = Field(ge=0, le=100)
    recency_score: float = Field(ge=0, le=100)
    completeness_score: float = Field(ge=0, le=100)

    total_facts: int = 0
    verified_facts: int = 0
    high_quality_sources: int = 0
    medium_quality_sources: int = 0
    low_quality_sources: int = 0

    missing_information: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

    generated_at: datetime = Field(default_factory=datetime.now)

    def is_passing(self, threshold: float = 85.0) -> bool:
        """Check if quality meets threshold."""
        return self.overall_score >= threshold

    def get_grade(self) -> str:
        """Get letter grade for overall score."""
        if self.overall_score >= 90:
            return "A"
        elif self.overall_score >= 80:
            return "B"
        elif self.overall_score >= 70:
            return "C"
        elif self.overall_score >= 60:
            return "D"
        else:
            return "F"

    def to_markdown(self) -> str:
        """Format report as markdown."""
        return f"""
## Quality Report

**Overall Score**: {self.overall_score:.1f}/100 (Grade: {self.get_grade()})
**Status**: {"✅ PASS" if self.is_passing() else "❌ FAIL"}

### Score Breakdown
- Source Quality: {self.source_quality_score:.1f}/100 (40% weight)
- Verification Rate: {self.verification_rate:.1f}% (30% weight)
- Recency: {self.recency_score:.1f}/100 (20% weight)
- Completeness: {self.completeness_score:.1f}/100 (10% weight)

### Facts Summary
- Total Facts: {self.total_facts}
- Verified: {self.verified_facts} ({self.verification_rate:.0f}%)
- Unverified: {self.total_facts - self.verified_facts}

### Source Distribution
- High Quality (Official/Authoritative): {self.high_quality_sources}
- Medium Quality (Reputable): {self.medium_quality_sources}
- Low Quality (Community/Unknown): {self.low_quality_sources}

### Strengths
{chr(10).join(f"- {s}" for s in self.strengths) if self.strengths else "- None identified"}

### Missing Information
{chr(10).join(f"- {m}" for m in self.missing_information) if self.missing_information else "- None"}

### Recommendations
{chr(10).join(f"- {r}" for r in self.recommendations) if self.recommendations else "- None"}

*Generated at: {self.generated_at.strftime("%Y-%m-%d %H:%M:%S")}*
"""
