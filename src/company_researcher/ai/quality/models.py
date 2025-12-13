"""Pydantic models for AI quality assessment."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Tuple
from enum import Enum


class QualityLevel(str, Enum):
    """Quality level classification."""
    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"  # 75-89
    ACCEPTABLE = "acceptable"  # 60-74
    POOR = "poor"  # 40-59
    INSUFFICIENT = "insufficient"  # 0-39

    @classmethod
    def from_score(cls, score: float) -> "QualityLevel":
        """Convert a 0-100 score to quality level.

        Scores are clamped to 0-100 range for classification.
        """
        # Clamp score to valid range
        score = max(0.0, min(100.0, score))

        if score >= 90:
            return cls.EXCELLENT
        elif score >= 75:
            return cls.GOOD
        elif score >= 60:
            return cls.ACCEPTABLE
        elif score >= 40:
            return cls.POOR
        else:
            return cls.INSUFFICIENT

    def to_score_range(self) -> Tuple[int, int]:
        """Get score range for this level."""
        ranges: Dict[QualityLevel, Tuple[int, int]] = {
            QualityLevel.EXCELLENT: (90, 100),
            QualityLevel.GOOD: (75, 89),
            QualityLevel.ACCEPTABLE: (60, 74),
            QualityLevel.POOR: (40, 59),
            QualityLevel.INSUFFICIENT: (0, 39)
        }
        return ranges[self]  # All enum values covered, safe to index directly

    def is_passing(self, threshold: float = 75.0) -> bool:
        """Check if this level meets threshold."""
        min_score, _ = self.to_score_range()
        return min_score >= threshold


class SourceType(str, Enum):
    """Type of information source."""
    OFFICIAL = "official"  # Company website, IR
    REGULATORY = "regulatory"  # SEC, government filings
    NEWS_MAJOR = "news_major"  # Reuters, Bloomberg
    NEWS_TRADE = "news_trade"  # Industry publications
    NEWS_LOCAL = "news_local"  # Local/regional news
    ACADEMIC = "academic"  # Research papers
    ANALYST = "analyst"  # Analyst reports
    BLOG = "blog"  # Blogs, opinion pieces
    SOCIAL = "social"  # Social media
    UNKNOWN = "unknown"


class ContentQualityAssessment(BaseModel):
    """Quality assessment for a content section."""

    section_name: str = Field(description="Name of the section assessed")
    quality_level: QualityLevel = Field(description="Overall quality level")
    score: float = Field(ge=0.0, le=100.0, description="Numeric quality score")

    # Quality dimensions
    factual_density: float = Field(
        ge=0.0, le=1.0,
        description="Ratio of concrete facts to total content"
    )
    specificity: float = Field(
        ge=0.0, le=1.0,
        description="How specific vs vague the content is"
    )
    completeness: float = Field(
        ge=0.0, le=1.0,
        description="Coverage of expected topics"
    )
    accuracy_indicators: float = Field(
        ge=0.0, le=1.0,
        default=0.5,
        description="Indicators of accuracy (sources cited, dates, etc.)"
    )
    recency: float = Field(
        ge=0.0, le=1.0,
        default=0.5,
        description="How recent the information is"
    )

    # Issues and strengths
    issues: List[str] = Field(
        default_factory=list,
        description="Identified quality issues"
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Content strengths"
    )
    improvement_suggestions: List[str] = Field(
        default_factory=list,
        description="Suggestions for improvement"
    )

    # Missing information
    missing_topics: List[str] = Field(
        default_factory=list,
        description="Expected topics not covered"
    )

    class Config:
        use_enum_values = True


class SourceQualityAssessment(BaseModel):
    """Quality assessment for a source."""

    url: str = Field(description="Source URL")
    domain: str = Field(description="Domain name")
    title: str = Field(default="", description="Source title")

    quality_level: QualityLevel = Field(description="Overall quality level")
    source_type: SourceType = Field(description="Type of source")

    # Quality scores
    authority_score: float = Field(
        ge=0.0, le=1.0,
        description="Source authority/trustworthiness"
    )
    recency_score: float = Field(
        ge=0.0, le=1.0,
        description="How recent the source is"
    )
    relevance_score: float = Field(
        ge=0.0, le=1.0,
        description="Relevance to the research topic"
    )
    depth_score: float = Field(
        ge=0.0, le=1.0,
        default=0.5,
        description="Depth of information provided"
    )

    # Classification
    is_primary_source: bool = Field(
        description="Whether this is a primary/official source"
    )
    is_paywalled: bool = Field(
        default=False,
        description="Whether content is behind paywall"
    )

    # Reasoning
    reasoning: str = Field(
        default="",
        description="Explanation for the assessment"
    )

    class Config:
        use_enum_values = True


class ConfidenceAssessment(BaseModel):
    """Confidence assessment for a claim/fact."""

    claim: str = Field(description="The claim being assessed")
    confidence_level: QualityLevel = Field(description="Confidence level")
    confidence_score: float = Field(ge=0.0, le=1.0)

    # Supporting evidence
    supporting_sources: int = Field(
        default=0,
        description="Number of sources supporting this claim"
    )
    contradicting_sources: int = Field(
        default=0,
        description="Number of sources contradicting this claim"
    )
    source_quality_avg: float = Field(
        ge=0.0, le=1.0,
        default=0.5,
        description="Average quality of supporting sources"
    )

    # Uncertainty analysis
    uncertainty_indicators: List[str] = Field(
        default_factory=list,
        description="Words/phrases indicating uncertainty"
    )
    verification_status: str = Field(
        default="unverified",
        description="verified, unverified, conflicting, or uncertain"
    )

    reasoning: str = Field(default="", description="Explanation")

    class Config:
        use_enum_values = True


class SectionRequirements(BaseModel):
    """Requirements for a specific section by company type."""

    section_name: str
    required: bool = True
    min_score: float = 60.0
    expected_topics: List[str] = Field(default_factory=list)
    weight: float = 1.0  # Weight in overall score


class OverallQualityReport(BaseModel):
    """Complete quality assessment report."""

    # Overall scores
    overall_score: float = Field(ge=0.0, le=100.0)
    overall_level: QualityLevel

    # Component assessments
    section_assessments: List[ContentQualityAssessment] = Field(default_factory=list)
    source_assessments: List[SourceQualityAssessment] = Field(default_factory=list)

    # Summary metrics
    section_scores: Dict[str, float] = Field(default_factory=dict)
    avg_source_quality: float = Field(ge=0.0, le=1.0, default=0.5)
    primary_source_count: int = Field(default=0)
    total_source_count: int = Field(default=0)

    # Issues and recommendations
    key_gaps: List[str] = Field(
        default_factory=list,
        description="Major information gaps"
    )
    critical_issues: List[str] = Field(
        default_factory=list,
        description="Critical quality issues"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommendations for improvement"
    )

    # Decision support
    ready_for_delivery: bool = Field(description="Whether report meets quality bar")
    iteration_needed: bool = Field(description="Whether more research is needed")
    focus_areas_for_iteration: List[str] = Field(
        default_factory=list,
        description="Areas to focus on if iterating"
    )

    # Metadata
    company_type: str = Field(default="unknown")
    quality_threshold: float = Field(default=75.0)

    class Config:
        use_enum_values = True

    def get_failing_sections(self) -> List[str]:
        """Get sections below acceptable quality."""
        return [
            s.section_name for s in self.section_assessments
            if s.score < 60
        ]

    def get_section_score(self, section_name: str) -> Optional[float]:
        """Get score for a specific section."""
        for s in self.section_assessments:
            if s.section_name == section_name:
                return s.score
        return None
