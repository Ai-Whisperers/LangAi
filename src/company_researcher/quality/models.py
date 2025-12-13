"""
Quality system data models (Phase 5).

This module defines the core data structures for source tracking,
quality assessment, and fact verification.

Enhanced with:
- MarketShareValidator: Validates competitor market shares sum to ~100%
"""

from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple
from ..utils import utc_now


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
    retrieved_at: datetime = Field(default_factory=utc_now)
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
    created_at: datetime = Field(default_factory=utc_now)

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

    generated_at: datetime = Field(default_factory=utc_now)

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


# ============================================================================
# Market Share Validator
# ============================================================================

class MarketShareValidationResult(BaseModel):
    """Result of market share validation."""

    is_valid: bool = False
    total_percentage: float = 0.0
    deviation_from_100: float = 0.0
    competitors: List[Dict[str, Any]] = Field(default_factory=list)
    issues: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    corrected_shares: Optional[Dict[str, float]] = None


class MarketShareValidator:
    """
    Validates that competitor market shares sum to approximately 100%.

    This addresses the issue where extracted market share data contained
    mathematical errors (e.g., Tigo=51.4% + Personal=44.6% + Claro=4% > 100%).

    Usage:
        validator = MarketShareValidator()
        result = validator.validate([
            {"name": "Tigo", "share": 51.4},
            {"name": "Personal", "share": 44.6},
            {"name": "Claro", "share": 4.0}
        ])
        if not result.is_valid:
            print(f"Issues: {result.issues}")
    """

    # Acceptable deviation from 100% (accounts for rounding, "others" category)
    DEFAULT_TOLERANCE = 5.0  # ±5%

    def __init__(self, tolerance: float = DEFAULT_TOLERANCE):
        """
        Initialize validator.

        Args:
            tolerance: Acceptable deviation from 100% (default ±5%)
        """
        self.tolerance = tolerance

    def validate(
        self,
        market_shares: List[Dict[str, Any]],
        country: Optional[str] = None,
        year: Optional[int] = None
    ) -> MarketShareValidationResult:
        """
        Validate that market shares sum to approximately 100%.

        Args:
            market_shares: List of dicts with 'name' and 'share' keys
                          e.g., [{"name": "Tigo", "share": 51.4}, ...]
            country: Country context for validation messages
            year: Year of data for validation messages

        Returns:
            MarketShareValidationResult with validation details
        """
        result = MarketShareValidationResult(
            competitors=market_shares
        )

        if not market_shares:
            result.issues.append("No market share data provided")
            return result

        # Extract percentages
        total = 0.0
        valid_entries = []

        for entry in market_shares:
            name = entry.get('name', 'Unknown')
            share = entry.get('share', entry.get('market_share', 0))

            # Handle string percentages like "51.4%"
            if isinstance(share, str):
                share = share.replace('%', '').strip()
                try:
                    share = float(share)
                except ValueError:
                    result.warnings.append(f"Could not parse share for {name}: {share}")
                    continue

            if share < 0:
                result.issues.append(f"Negative market share for {name}: {share}%")
                continue

            if share > 100:
                result.issues.append(f"Market share exceeds 100% for {name}: {share}%")
                continue

            total += share
            valid_entries.append({"name": name, "share": share})

        result.total_percentage = total
        result.deviation_from_100 = abs(100 - total)

        # Check if sum is valid
        if total < (100 - self.tolerance):
            context = f" for {country}" if country else ""
            year_str = f" ({year})" if year else ""
            result.warnings.append(
                f"Market shares sum to {total:.1f}%{context}{year_str} - "
                f"missing {100 - total:.1f}% (likely 'others' category)"
            )
            result.is_valid = True  # Still valid, just incomplete

        elif total > (100 + self.tolerance):
            result.is_valid = False
            result.issues.append(
                f"Market shares sum to {total:.1f}% (exceeds 100% by {total - 100:.1f}%) - "
                "data likely contains errors or overlapping categories"
            )

            # Attempt to normalize
            if total > 0:
                result.corrected_shares = {
                    e['name']: round((e['share'] / total) * 100, 1)
                    for e in valid_entries
                }
                result.warnings.append(
                    f"Suggested normalized shares: {result.corrected_shares}"
                )

        else:
            result.is_valid = True

        # Additional sanity checks
        if len(valid_entries) >= 2:
            # Check for suspiciously round numbers that might be estimates
            round_count = sum(1 for e in valid_entries if e['share'] == int(e['share']))
            if round_count == len(valid_entries):
                result.warnings.append(
                    "All market shares are round numbers - may be estimates rather than actual data"
                )

            # Check for duplicate values
            shares_only = [e['share'] for e in valid_entries]
            if len(shares_only) != len(set(shares_only)):
                result.warnings.append(
                    "Some competitors have identical market shares - verify data accuracy"
                )

        return result

    def validate_from_text(
        self,
        text: str,
        company_name: str
    ) -> Tuple[MarketShareValidationResult, List[Dict[str, float]]]:
        """
        Extract and validate market shares from report text.

        Args:
            text: Report text containing market share information
            company_name: Company being researched

        Returns:
            Tuple of (validation_result, extracted_shares)
        """
        import re

        # Pattern to extract market share mentions
        # Matches: "Company X has 45.2% market share" or "Company X (45.2%)"
        patterns = [
            r'(\w+(?:\s+\w+)?)\s+(?:has|holds|with|at)?\s*(\d+\.?\d*)\s*%\s*(?:market share|share|of the market)',
            r'(\w+(?:\s+\w+)?)\s*[\(\[](\d+\.?\d*)\s*%[\)\]]',
            r'market share[:\s]+(\w+(?:\s+\w+)?)\s*[\(\[]?(\d+\.?\d*)\s*%',
        ]

        extracted = []
        seen_names = set()

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                name, share = match
                name = name.strip()
                if name.lower() not in seen_names:
                    seen_names.add(name.lower())
                    try:
                        extracted.append({
                            "name": name,
                            "share": float(share)
                        })
                    except ValueError:
                        continue

        result = self.validate(extracted)
        return result, extracted


def validate_market_shares(
    shares: List[Dict[str, Any]],
    tolerance: float = 5.0
) -> MarketShareValidationResult:
    """
    Convenience function to validate market shares.

    Args:
        shares: List of dicts with 'name' and 'share' keys
        tolerance: Acceptable deviation from 100%

    Returns:
        MarketShareValidationResult
    """
    validator = MarketShareValidator(tolerance=tolerance)
    return validator.validate(shares)
