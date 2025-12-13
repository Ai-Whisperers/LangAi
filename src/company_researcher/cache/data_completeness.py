"""
Data Completeness Checker.

Determines what research data is complete vs missing for a company:
- Checks each section (financials, leadership, products, etc.)
- Identifies specific gaps
- Recommends data sources for missing items
- Tracks freshness of existing data
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from ..utils import get_logger

logger = get_logger(__name__)


class DataSection(str, Enum):
    """Research data sections."""
    OVERVIEW = "overview"
    FINANCIALS = "financials"
    LEADERSHIP = "leadership"
    PRODUCTS = "products"
    COMPETITORS = "competitors"
    MARKET = "market"
    NEWS = "news"
    ESG = "esg"
    RISKS = "risks"
    CONTACTS = "contacts"
    SOCIAL = "social"
    PATENTS = "patents"
    LEGAL = "legal"
    LOCATIONS = "locations"


class SectionStatus(str, Enum):
    """Status of a data section."""
    COMPLETE = "complete"       # All required fields present
    PARTIAL = "partial"         # Some data but missing fields
    MISSING = "missing"         # No data at all
    STALE = "stale"             # Data exists but too old
    UNKNOWN = "unknown"         # Cannot determine


@dataclass
class SectionRequirements:
    """Requirements for a data section."""
    section: DataSection
    required_fields: List[str]
    optional_fields: List[str] = field(default_factory=list)
    min_sources: int = 1
    max_age_days: int = 90
    recommended_sources: List[str] = field(default_factory=list)


# Default requirements for each section
SECTION_REQUIREMENTS = {
    DataSection.OVERVIEW: SectionRequirements(
        section=DataSection.OVERVIEW,
        required_fields=["company_name", "description", "industry", "founded"],
        optional_fields=["headquarters", "website", "employees"],
        min_sources=2,
        max_age_days=180,
        recommended_sources=["tavily", "company_website", "crunchbase"],
    ),
    DataSection.FINANCIALS: SectionRequirements(
        section=DataSection.FINANCIALS,
        required_fields=["revenue", "revenue_year"],
        optional_fields=["net_income", "market_cap", "stock_price", "employees", "growth_rate"],
        min_sources=1,
        max_age_days=30,
        recommended_sources=["sec_edgar", "fmp", "finnhub", "yfinance"],
    ),
    DataSection.LEADERSHIP: SectionRequirements(
        section=DataSection.LEADERSHIP,
        required_fields=["ceo"],
        optional_fields=["cfo", "cto", "board_members", "founders"],
        min_sources=1,
        max_age_days=90,
        recommended_sources=["company_website", "linkedin", "tavily"],
    ),
    DataSection.PRODUCTS: SectionRequirements(
        section=DataSection.PRODUCTS,
        required_fields=["main_products"],
        optional_fields=["product_categories", "flagship_products", "recent_launches"],
        min_sources=1,
        max_age_days=90,
        recommended_sources=["company_website", "tavily"],
    ),
    DataSection.COMPETITORS: SectionRequirements(
        section=DataSection.COMPETITORS,
        required_fields=["competitor_names"],
        optional_fields=["competitive_position", "market_share"],
        min_sources=2,
        max_age_days=90,
        recommended_sources=["tavily", "industry_reports"],
    ),
    DataSection.MARKET: SectionRequirements(
        section=DataSection.MARKET,
        required_fields=["market_size", "market_position"],
        optional_fields=["market_growth", "target_market", "geographic_presence"],
        min_sources=2,
        max_age_days=90,
        recommended_sources=["tavily", "industry_reports"],
    ),
    DataSection.NEWS: SectionRequirements(
        section=DataSection.NEWS,
        required_fields=["recent_news"],
        optional_fields=["sentiment", "key_events"],
        min_sources=3,
        max_age_days=7,
        recommended_sources=["newsapi", "gnews", "tavily"],
    ),
    DataSection.ESG: SectionRequirements(
        section=DataSection.ESG,
        required_fields=[],
        optional_fields=["environmental", "social", "governance", "esg_score"],
        min_sources=1,
        max_age_days=180,
        recommended_sources=["finnhub", "tavily", "company_website"],
    ),
    DataSection.RISKS: SectionRequirements(
        section=DataSection.RISKS,
        required_fields=["key_risks"],
        optional_fields=["risk_score", "risk_factors"],
        min_sources=2,
        max_age_days=90,
        recommended_sources=["sec_edgar", "tavily", "news"],
    ),
    DataSection.CONTACTS: SectionRequirements(
        section=DataSection.CONTACTS,
        required_fields=[],
        optional_fields=["email", "phone", "ir_contact", "press_contact"],
        min_sources=1,
        max_age_days=90,
        recommended_sources=["hunter_io", "company_website"],
    ),
    DataSection.SOCIAL: SectionRequirements(
        section=DataSection.SOCIAL,
        required_fields=[],
        optional_fields=["twitter", "linkedin", "sentiment"],
        min_sources=1,
        max_age_days=30,
        recommended_sources=["reddit", "twitter", "company_website"],
    ),
}


@dataclass
class ResearchGap:
    """A specific gap in research data."""
    section: DataSection
    field: str
    importance: str  # "critical", "high", "medium", "low"
    recommended_sources: List[str]
    reason: str


@dataclass
class CompletenessReport:
    """Report on data completeness for a company."""
    company_name: str
    overall_completeness: float  # 0-100
    section_status: Dict[DataSection, SectionStatus]
    section_completeness: Dict[DataSection, float]
    gaps: List[ResearchGap]
    stale_sections: List[DataSection]
    recommendations: List[str]
    needs_research: bool
    priority_sections: List[DataSection]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "company_name": self.company_name,
            "overall_completeness": self.overall_completeness,
            "section_status": {k.value: v.value for k, v in self.section_status.items()},
            "section_completeness": {k.value: v for k, v in self.section_completeness.items()},
            "gaps": [
                {
                    "section": g.section.value,
                    "field": g.field,
                    "importance": g.importance,
                    "recommended_sources": g.recommended_sources,
                    "reason": g.reason,
                }
                for g in self.gaps
            ],
            "stale_sections": [s.value for s in self.stale_sections],
            "recommendations": self.recommendations,
            "needs_research": self.needs_research,
            "priority_sections": [s.value for s in self.priority_sections],
            "generated_at": self.generated_at.isoformat(),
        }


class CompletenessChecker:
    """
    Check data completeness for research.

    Analyzes cached data to determine:
    - What sections are complete
    - What's missing
    - What's stale
    - What to prioritize
    """

    def __init__(self, requirements: Optional[Dict[DataSection, SectionRequirements]] = None):
        """
        Initialize completeness checker.

        Args:
            requirements: Custom requirements per section
        """
        self.requirements = requirements or SECTION_REQUIREMENTS

    def check_completeness(
        self,
        company_name: str,
        cached_data: Dict[str, Any],
    ) -> CompletenessReport:
        """
        Check completeness of cached data for a company.

        Args:
            company_name: Company name
            cached_data: Existing cached data

        Returns:
            CompletenessReport with gaps and recommendations
        """
        section_status: Dict[DataSection, SectionStatus] = {}
        section_completeness: Dict[DataSection, float] = {}
        gaps: List[ResearchGap] = []
        stale_sections: List[DataSection] = []
        recommendations: List[str] = []
        priority_sections: List[DataSection] = []

        now = datetime.now(timezone.utc)

        for section, reqs in self.requirements.items():
            section_data = cached_data.get(section.value, {})
            last_updated = cached_data.get(f"{section.value}_updated")

            # Check staleness
            if last_updated:
                try:
                    if isinstance(last_updated, str):
                        updated_dt = datetime.fromisoformat(last_updated)
                    else:
                        updated_dt = last_updated

                    age_days = (now - updated_dt).days
                    if age_days > reqs.max_age_days:
                        stale_sections.append(section)
                except Exception as e:
                    logger.debug(f"Failed to check section staleness: {e}")

            # Calculate completeness for this section
            status, completeness, section_gaps = self._check_section(
                section, section_data, reqs
            )

            section_status[section] = status
            section_completeness[section] = completeness
            gaps.extend(section_gaps)

            # Mark stale as needing refresh
            if section in stale_sections and status != SectionStatus.MISSING:
                section_status[section] = SectionStatus.STALE

        # Calculate overall completeness
        weights = {
            DataSection.OVERVIEW: 15,
            DataSection.FINANCIALS: 20,
            DataSection.LEADERSHIP: 10,
            DataSection.PRODUCTS: 15,
            DataSection.COMPETITORS: 15,
            DataSection.MARKET: 10,
            DataSection.NEWS: 5,
            DataSection.ESG: 5,
            DataSection.RISKS: 5,
        }

        total_weight = sum(weights.get(s, 0) for s in section_completeness)
        if total_weight > 0:
            overall = sum(
                section_completeness.get(s, 0) * weights.get(s, 0)
                for s in section_completeness
            ) / total_weight
        else:
            overall = 0

        # Determine priority sections
        critical_sections = [DataSection.OVERVIEW, DataSection.FINANCIALS, DataSection.PRODUCTS]
        for section in critical_sections:
            if section_status.get(section) in [SectionStatus.MISSING, SectionStatus.STALE]:
                priority_sections.append(section)

        # Add missing high-value sections
        for section, status in section_status.items():
            if status == SectionStatus.MISSING and section not in priority_sections:
                priority_sections.append(section)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            section_status, gaps, stale_sections
        )

        needs_research = (
            overall < 70
            or len(priority_sections) > 0
            or len(stale_sections) > 2
        )

        return CompletenessReport(
            company_name=company_name,
            overall_completeness=overall,
            section_status=section_status,
            section_completeness=section_completeness,
            gaps=gaps,
            stale_sections=stale_sections,
            recommendations=recommendations,
            needs_research=needs_research,
            priority_sections=priority_sections,
        )

    def _check_section(
        self,
        section: DataSection,
        data: Dict[str, Any],
        reqs: SectionRequirements,
    ) -> tuple:
        """Check completeness of a single section."""
        gaps = []

        if not data:
            # Section completely missing
            for field in reqs.required_fields:
                gaps.append(ResearchGap(
                    section=section,
                    field=field,
                    importance="critical" if field in reqs.required_fields[:2] else "high",
                    recommended_sources=reqs.recommended_sources,
                    reason="Field not present in cached data",
                ))
            return SectionStatus.MISSING, 0.0, gaps

        # Count fields present
        required_present = sum(1 for f in reqs.required_fields if data.get(f))
        optional_present = sum(1 for f in reqs.optional_fields if data.get(f))

        total_required = len(reqs.required_fields)
        total_optional = len(reqs.optional_fields)

        # Check required fields
        for field in reqs.required_fields:
            if not data.get(field):
                gaps.append(ResearchGap(
                    section=section,
                    field=field,
                    importance="critical",
                    recommended_sources=reqs.recommended_sources,
                    reason="Required field missing",
                ))

        # Calculate completeness
        if total_required == 0:
            # No required fields - section is optional
            completeness = 100.0 if optional_present > 0 else 50.0
            status = SectionStatus.COMPLETE if optional_present > 0 else SectionStatus.PARTIAL
        else:
            required_pct = (required_present / total_required) * 100 if total_required > 0 else 100
            optional_pct = (optional_present / total_optional) * 100 if total_optional > 0 else 100

            # Weight: 70% required, 30% optional
            completeness = required_pct * 0.7 + optional_pct * 0.3

            if required_present == total_required:
                status = SectionStatus.COMPLETE if completeness >= 80 else SectionStatus.PARTIAL
            elif required_present > 0:
                status = SectionStatus.PARTIAL
            else:
                status = SectionStatus.MISSING

        return status, completeness, gaps

    def _generate_recommendations(
        self,
        section_status: Dict[DataSection, SectionStatus],
        gaps: List[ResearchGap],
        stale_sections: List[DataSection],
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Missing sections
        missing = [s for s, st in section_status.items() if st == SectionStatus.MISSING]
        if missing:
            recommendations.append(
                f"Missing data for: {', '.join(s.value for s in missing)}"
            )

        # Stale sections
        if stale_sections:
            recommendations.append(
                f"Refresh stale data for: {', '.join(s.value for s in stale_sections)}"
            )

        # Specific source recommendations
        sources_needed: Set[str] = set()
        for gap in gaps:
            if gap.importance == "critical":
                sources_needed.update(gap.recommended_sources)

        if sources_needed:
            recommendations.append(
                f"Recommended data sources: {', '.join(sources_needed)}"
            )

        # Financial-specific
        if DataSection.FINANCIALS in missing:
            recommendations.append(
                "For US public companies: Use SEC EDGAR (FREE) for accurate financials"
            )

        return recommendations

    def get_research_priority(
        self,
        report: CompletenessReport,
    ) -> Dict[str, Any]:
        """
        Get prioritized research tasks based on completeness report.

        Returns dict with:
        - high_priority: Sections to research immediately
        - medium_priority: Sections to research if time permits
        - skip: Sections that are complete
        - sources_to_use: Recommended data sources
        """
        high_priority = []
        medium_priority = []
        skip = []
        sources_to_use = set()

        for section, status in report.section_status.items():
            reqs = self.requirements.get(section)
            if not reqs:
                continue

            if status in [SectionStatus.MISSING, SectionStatus.STALE]:
                if section in [DataSection.OVERVIEW, DataSection.FINANCIALS,
                               DataSection.PRODUCTS, DataSection.COMPETITORS]:
                    high_priority.append(section.value)
                else:
                    medium_priority.append(section.value)
                sources_to_use.update(reqs.recommended_sources)
            elif status == SectionStatus.PARTIAL:
                medium_priority.append(section.value)
                sources_to_use.update(reqs.recommended_sources)
            else:
                skip.append(section.value)

        return {
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "skip": skip,
            "sources_to_use": list(sources_to_use),
            "overall_completeness": report.overall_completeness,
            "needs_research": report.needs_research,
        }
