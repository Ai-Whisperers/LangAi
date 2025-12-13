"""
Source Utilization Tracking Module

Tracks fact extraction from sources to ensure maximum utilization:
- Which facts came from which sources
- Source quality scoring
- Extraction coverage analysis
- Recommendations for additional searches

This module addresses the issue of "sources not fully utilized" in reports
by analyzing what information is available vs. what was extracted.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import re
from collections import defaultdict
from ..utils import utc_now


class SourceType(Enum):
    """Types of information sources."""
    SEC_FILING = "sec_filing"
    ANNUAL_REPORT = "annual_report"
    QUARTERLY_REPORT = "quarterly_report"
    PRESS_RELEASE = "press_release"
    NEWS_ARTICLE = "news_article"
    ANALYST_REPORT = "analyst_report"
    COMPANY_WEBSITE = "company_website"
    STOCK_DATABASE = "stock_database"
    REGULATORY_FILING = "regulatory_filing"
    INDUSTRY_REPORT = "industry_report"
    SOCIAL_MEDIA = "social_media"
    UNKNOWN = "unknown"


class FactCategory(Enum):
    """Categories of extractable facts."""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    LEADERSHIP = "leadership"
    COMPETITIVE = "competitive"
    PRODUCT = "product"
    GEOGRAPHIC = "geographic"
    REGULATORY = "regulatory"
    ESG = "esg"
    RISK = "risk"


@dataclass
class ExtractedFact:
    """A single fact extracted from a source."""
    fact_id: str
    category: FactCategory
    fact_type: str  # e.g., "revenue", "ceo_name", "market_share"
    value: Any
    source_id: str
    source_url: str
    extraction_method: str  # e.g., "pattern", "table", "llm"
    confidence: float
    extracted_at: datetime = field(default_factory=utc_now)
    context: str = ""  # Surrounding text for verification


@dataclass
class SourceInfo:
    """Information about a source."""
    source_id: str
    url: str
    title: str
    source_type: SourceType
    content_length: int
    fetch_time: datetime
    extracted_facts: List[str] = field(default_factory=list)  # fact_ids
    potential_facts: List[str] = field(default_factory=list)  # Fact types available but not extracted
    quality_score: float = 0.0
    language: str = "en"


@dataclass
class ExtractionCoverage:
    """Coverage analysis for fact extraction."""
    total_facts_extracted: int = 0
    total_potential_facts: int = 0
    coverage_percentage: float = 0.0
    coverage_by_category: Dict[FactCategory, float] = field(default_factory=dict)
    missing_critical_facts: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class SourceUtilization:
    """Utilization metrics for a single source."""
    source_id: str
    facts_extracted: int
    facts_potential: int
    utilization_rate: float
    unique_facts: int  # Facts only from this source
    value_score: float  # Overall value of this source
    recommendations: List[str] = field(default_factory=list)


class SourceUtilizationTracker:
    """
    Tracks and analyzes source utilization for research reports.

    Ensures maximum value extraction from each source and
    identifies gaps in coverage.
    """

    # Expected fact types by source type
    SOURCE_EXPECTED_FACTS: Dict[SourceType, List[str]] = {
        SourceType.SEC_FILING: [
            "revenue", "net_income", "eps", "total_assets", "total_liabilities",
            "operating_income", "cash_flow", "shares_outstanding", "executive_compensation",
            "risk_factors", "related_party_transactions", "segment_revenue"
        ],
        SourceType.ANNUAL_REPORT: [
            "revenue", "net_income", "ebitda", "employees", "operating_margin",
            "revenue_by_segment", "revenue_by_geography", "capex", "r_and_d_expense",
            "strategy", "outlook", "competitive_position"
        ],
        SourceType.QUARTERLY_REPORT: [
            "quarterly_revenue", "quarterly_net_income", "quarterly_eps",
            "revenue_growth_yoy", "margin_trends", "guidance"
        ],
        SourceType.PRESS_RELEASE: [
            "announcements", "partnerships", "acquisitions", "product_launches",
            "executive_changes", "strategic_initiatives"
        ],
        SourceType.NEWS_ARTICLE: [
            "recent_events", "market_sentiment", "competitor_actions",
            "industry_trends", "analyst_opinions"
        ],
        SourceType.STOCK_DATABASE: [
            "market_cap", "stock_price", "pe_ratio", "dividend_yield",
            "52_week_high", "52_week_low", "trading_volume", "beta"
        ],
        SourceType.COMPANY_WEBSITE: [
            "mission", "vision", "leadership_team", "products_services",
            "locations", "history", "contact_info"
        ],
    }

    # Critical facts that should always be extracted
    CRITICAL_FACTS = [
        "revenue", "net_income", "market_cap", "employees",
        "ceo", "headquarters", "industry", "founded"
    ]

    # Fact category mappings
    FACT_CATEGORIES: Dict[str, FactCategory] = {
        "revenue": FactCategory.FINANCIAL,
        "net_income": FactCategory.FINANCIAL,
        "ebitda": FactCategory.FINANCIAL,
        "eps": FactCategory.FINANCIAL,
        "market_cap": FactCategory.FINANCIAL,
        "employees": FactCategory.OPERATIONAL,
        "ceo": FactCategory.LEADERSHIP,
        "headquarters": FactCategory.GEOGRAPHIC,
        "mission": FactCategory.STRATEGIC,
        "products": FactCategory.PRODUCT,
        "competitors": FactCategory.COMPETITIVE,
        "risk_factors": FactCategory.RISK,
        "esg_initiatives": FactCategory.ESG,
    }

    def __init__(self):
        """Initialize the tracker."""
        self.sources: Dict[str, SourceInfo] = {}
        self.facts: Dict[str, ExtractedFact] = {}
        self.fact_counter = 0

    def register_source(
        self,
        url: str,
        title: str,
        source_type: SourceType,
        content: str,
        language: str = "en"
    ) -> str:
        """
        Register a new source for tracking.

        Args:
            url: Source URL
            title: Source title
            source_type: Type classification
            content: Full content text
            language: Content language

        Returns:
            Generated source ID
        """
        source_id = f"src_{len(self.sources):04d}"

        # Analyze potential facts in content
        potential = self._analyze_potential_facts(content, source_type)

        # Calculate quality score
        quality = self._calculate_source_quality(content, source_type, potential)

        source = SourceInfo(
            source_id=source_id,
            url=url,
            title=title,
            source_type=source_type,
            content_length=len(content),
            fetch_time=utc_now(),
            potential_facts=potential,
            quality_score=quality,
            language=language
        )

        self.sources[source_id] = source
        return source_id

    def _analyze_potential_facts(
        self,
        content: str,
        source_type: SourceType
    ) -> List[str]:
        """Analyze what facts could potentially be extracted from content."""
        potential = []
        content_lower = content.lower()

        # Check for expected facts based on source type
        expected = self.SOURCE_EXPECTED_FACTS.get(source_type, [])
        for fact_type in expected:
            keywords = self._get_fact_keywords(fact_type)
            if any(kw in content_lower for kw in keywords):
                potential.append(fact_type)

        # Check for financial data patterns
        financial_patterns = [
            (r'\$[\d,]+(?:\.\d+)?(?:\s*(?:billion|million|B|M))?', ["revenue", "income", "cost"]),
            (r'\d+(?:\.\d+)?%', ["margin", "growth", "rate"]),
            (r'\d{1,3}(?:,\d{3})+\s*employees?', ["employees"]),
        ]

        for pattern, fact_types in financial_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                potential.extend([ft for ft in fact_types if ft not in potential])

        return list(set(potential))

    def _get_fact_keywords(self, fact_type: str) -> List[str]:
        """Get keywords associated with a fact type."""
        keyword_map = {
            "revenue": ["revenue", "sales", "turnover", "top line"],
            "net_income": ["net income", "net profit", "net earnings", "bottom line"],
            "ebitda": ["ebitda", "operating profit"],
            "eps": ["eps", "earnings per share"],
            "employees": ["employees", "workforce", "staff", "headcount"],
            "market_cap": ["market cap", "market value", "valuation"],
            "ceo": ["ceo", "chief executive", "president"],
            "headquarters": ["headquarter", "hq", "based in", "located in"],
            "mission": ["mission", "purpose"],
            "vision": ["vision"],
            "strategy": ["strategy", "strategic", "initiative"],
            "risk_factors": ["risk", "challenge", "threat"],
        }
        return keyword_map.get(fact_type, [fact_type])

    def _calculate_source_quality(
        self,
        content: str,
        source_type: SourceType,
        potential_facts: List[str]
    ) -> float:
        """Calculate quality score for a source."""
        score = 0.0

        # Base score by source type
        type_scores = {
            SourceType.SEC_FILING: 0.95,
            SourceType.ANNUAL_REPORT: 0.90,
            SourceType.QUARTERLY_REPORT: 0.85,
            SourceType.ANALYST_REPORT: 0.80,
            SourceType.PRESS_RELEASE: 0.75,
            SourceType.STOCK_DATABASE: 0.85,
            SourceType.COMPANY_WEBSITE: 0.70,
            SourceType.NEWS_ARTICLE: 0.65,
            SourceType.INDUSTRY_REPORT: 0.75,
            SourceType.REGULATORY_FILING: 0.90,
        }
        score = type_scores.get(source_type, 0.50)

        # Adjust for content length
        if len(content) > 10000:
            score += 0.05
        elif len(content) < 500:
            score -= 0.10

        # Adjust for potential facts
        if len(potential_facts) >= 5:
            score += 0.05
        elif len(potential_facts) <= 1:
            score -= 0.10

        # Cap score between 0 and 1
        return max(0.0, min(1.0, score))

    def register_fact(
        self,
        fact_type: str,
        value: Any,
        source_id: str,
        extraction_method: str = "pattern",
        confidence: float = 1.0,
        context: str = ""
    ) -> str:
        """
        Register an extracted fact.

        Args:
            fact_type: Type of fact (e.g., "revenue")
            value: Extracted value
            source_id: ID of the source
            extraction_method: How it was extracted
            confidence: Confidence score
            context: Surrounding text

        Returns:
            Generated fact ID
        """
        self.fact_counter += 1
        fact_id = f"fact_{self.fact_counter:05d}"

        category = self.FACT_CATEGORIES.get(
            fact_type, FactCategory.OPERATIONAL
        )

        fact = ExtractedFact(
            fact_id=fact_id,
            category=category,
            fact_type=fact_type,
            value=value,
            source_id=source_id,
            source_url=self.sources[source_id].url if source_id in self.sources else "",
            extraction_method=extraction_method,
            confidence=confidence,
            context=context
        )

        self.facts[fact_id] = fact

        # Update source
        if source_id in self.sources:
            self.sources[source_id].extracted_facts.append(fact_id)
            # Remove from potential if it was there
            if fact_type in self.sources[source_id].potential_facts:
                self.sources[source_id].potential_facts.remove(fact_type)

        return fact_id

    def get_extraction_coverage(self) -> ExtractionCoverage:
        """
        Analyze overall extraction coverage.

        Returns:
            ExtractionCoverage with analysis
        """
        coverage = ExtractionCoverage()

        # Count facts
        coverage.total_facts_extracted = len(self.facts)

        # Count potential facts
        all_potential = set()
        for source in self.sources.values():
            all_potential.update(source.potential_facts)
        all_potential.update([f.fact_type for f in self.facts.values()])
        coverage.total_potential_facts = len(all_potential)

        # Calculate coverage percentage
        if coverage.total_potential_facts > 0:
            coverage.coverage_percentage = (
                coverage.total_facts_extracted / coverage.total_potential_facts * 100
            )

        # Coverage by category
        extracted_by_category: Dict[FactCategory, Set[str]] = defaultdict(set)
        potential_by_category: Dict[FactCategory, Set[str]] = defaultdict(set)

        for fact in self.facts.values():
            extracted_by_category[fact.category].add(fact.fact_type)

        for fact_type in all_potential:
            category = self.FACT_CATEGORIES.get(fact_type, FactCategory.OPERATIONAL)
            potential_by_category[category].add(fact_type)

        for category in FactCategory:
            extracted = len(extracted_by_category[category])
            potential = len(potential_by_category[category])
            if potential > 0:
                coverage.coverage_by_category[category] = extracted / potential * 100
            else:
                coverage.coverage_by_category[category] = 0.0

        # Find missing critical facts
        extracted_types = {f.fact_type for f in self.facts.values()}
        coverage.missing_critical_facts = [
            ft for ft in self.CRITICAL_FACTS
            if ft not in extracted_types
        ]

        # Generate recommendations
        coverage.recommendations = self._generate_coverage_recommendations(coverage)

        return coverage

    def _generate_coverage_recommendations(
        self,
        coverage: ExtractionCoverage
    ) -> List[str]:
        """Generate recommendations to improve coverage."""
        recommendations = []

        # Low overall coverage
        if coverage.coverage_percentage < 50:
            recommendations.append(
                "Consider adding more diverse sources to improve data coverage"
            )

        # Missing critical facts
        if coverage.missing_critical_facts:
            missing_str = ", ".join(coverage.missing_critical_facts[:5])
            recommendations.append(
                f"Priority: Extract missing critical facts - {missing_str}"
            )

        # Low category coverage
        for category, pct in coverage.coverage_by_category.items():
            if pct < 30:
                recommendations.append(
                    f"Low {category.value} data coverage ({pct:.0f}%) - "
                    f"consider adding {category.value}-focused sources"
                )

        # Underutilized sources
        for source in self.sources.values():
            if source.potential_facts and len(source.extracted_facts) == 0:
                recommendations.append(
                    f"Source '{source.title[:50]}' has potential facts but none extracted"
                )

        return recommendations

    def get_source_utilization(self, source_id: str) -> Optional[SourceUtilization]:
        """
        Get utilization metrics for a specific source.

        Args:
            source_id: ID of the source

        Returns:
            SourceUtilization or None if source not found
        """
        if source_id not in self.sources:
            return None

        source = self.sources[source_id]

        facts_extracted = len(source.extracted_facts)
        facts_potential = facts_extracted + len(source.potential_facts)

        utilization_rate = facts_extracted / facts_potential if facts_potential > 0 else 0

        # Calculate unique facts
        other_fact_types = set()
        for other_id, other_source in self.sources.items():
            if other_id != source_id:
                for fact_id in other_source.extracted_facts:
                    if fact_id in self.facts:
                        other_fact_types.add(self.facts[fact_id].fact_type)

        unique_facts = 0
        for fact_id in source.extracted_facts:
            if fact_id in self.facts:
                if self.facts[fact_id].fact_type not in other_fact_types:
                    unique_facts += 1

        # Calculate value score
        value_score = (
            source.quality_score * 0.4 +
            utilization_rate * 0.3 +
            (unique_facts / max(1, facts_extracted)) * 0.3
        )

        # Generate recommendations
        recommendations = []
        if source.potential_facts:
            recommendations.append(
                f"Unextracted facts available: {', '.join(source.potential_facts[:5])}"
            )
        if utilization_rate < 0.3:
            recommendations.append(
                "Low utilization rate - review extraction patterns for this source type"
            )

        return SourceUtilization(
            source_id=source_id,
            facts_extracted=facts_extracted,
            facts_potential=facts_potential,
            utilization_rate=utilization_rate,
            unique_facts=unique_facts,
            value_score=value_score,
            recommendations=recommendations
        )

    def get_all_source_utilizations(self) -> List[SourceUtilization]:
        """Get utilization metrics for all sources."""
        utilizations = []
        for source_id in self.sources:
            util = self.get_source_utilization(source_id)
            if util:
                utilizations.append(util)
        return sorted(utilizations, key=lambda x: x.value_score, reverse=True)

    def generate_utilization_report(self) -> str:
        """
        Generate a markdown report of source utilization.

        Returns:
            Markdown formatted report
        """
        lines = ["### Source Utilization Report", ""]

        # Overall coverage
        coverage = self.get_extraction_coverage()
        lines.append("**Overall Coverage:**")
        lines.append(f"- Facts extracted: {coverage.total_facts_extracted}")
        lines.append(f"- Coverage rate: {coverage.coverage_percentage:.1f}%")
        lines.append("")

        # Missing critical facts
        if coverage.missing_critical_facts:
            lines.append("**Missing Critical Facts:**")
            for fact in coverage.missing_critical_facts:
                lines.append(f"- {fact}")
            lines.append("")

        # Source utilization table
        utilizations = self.get_all_source_utilizations()
        if utilizations:
            lines.append("**Source Performance:**")
            lines.append("")
            lines.append("| Source | Extracted | Potential | Utilization | Unique Facts |")
            lines.append("| --- | --- | --- | --- | --- |")

            for util in utilizations[:10]:
                source = self.sources[util.source_id]
                title = source.title[:30] + "..." if len(source.title) > 30 else source.title
                lines.append(
                    f"| {title} | {util.facts_extracted} | {util.facts_potential} | "
                    f"{util.utilization_rate:.0%} | {util.unique_facts} |"
                )
            lines.append("")

        # Recommendations
        if coverage.recommendations:
            lines.append("**Recommendations:**")
            for rec in coverage.recommendations[:5]:
                lines.append(f"- {rec}")

        return "\n".join(lines)

    def get_facts_by_source(self, source_id: str) -> List[ExtractedFact]:
        """Get all facts extracted from a specific source."""
        if source_id not in self.sources:
            return []

        return [
            self.facts[fact_id]
            for fact_id in self.sources[source_id].extracted_facts
            if fact_id in self.facts
        ]

    def get_facts_by_type(self, fact_type: str) -> List[ExtractedFact]:
        """Get all facts of a specific type across all sources."""
        return [
            fact for fact in self.facts.values()
            if fact.fact_type == fact_type
        ]

    def get_fact_attribution_markdown(self) -> str:
        """
        Generate markdown showing fact attribution to sources.

        Returns:
            Markdown formatted attribution
        """
        lines = ["### Fact Attribution", ""]

        # Group facts by type
        facts_by_type: Dict[str, List[ExtractedFact]] = defaultdict(list)
        for fact in self.facts.values():
            facts_by_type[fact.fact_type].append(fact)

        for fact_type, facts in sorted(facts_by_type.items()):
            lines.append(f"**{fact_type.replace('_', ' ').title()}:**")
            for fact in facts:
                source = self.sources.get(fact.source_id)
                source_name = source.title[:40] if source else "Unknown"
                lines.append(f"- {fact.value} (from: {source_name})")
            lines.append("")

        return "\n".join(lines)


def create_source_tracker() -> SourceUtilizationTracker:
    """Factory function to create a SourceUtilizationTracker."""
    return SourceUtilizationTracker()
