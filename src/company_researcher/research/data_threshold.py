"""
Minimum Data Threshold Checker.

Addresses Issue #3: Don't Generate Empty Reports.

Checks if research output has sufficient data before generating a report.
Prevents publishing reports that are mostly "Data not available".

Features:
1. Pre-generation check (before spending resources on report)
2. Post-research check (after gathering data)
3. Retry logic with alternative strategies
4. Quality gates at different stages
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Any, Tuple
from enum import Enum
from ..utils import get_logger

logger = get_logger(__name__)


class DataSufficiency(Enum):
    """Overall data sufficiency levels."""
    EXCELLENT = "excellent"  # 80%+ coverage
    GOOD = "good"  # 60-80% coverage
    ADEQUATE = "adequate"  # 40-60% coverage
    POOR = "poor"  # 20-40% coverage
    INSUFFICIENT = "insufficient"  # <20% coverage


class RetryStrategy(Enum):
    """Strategies for retrying data collection."""
    MULTILINGUAL = "multilingual"  # Add queries in other languages
    PARENT_COMPANY = "parent_company"  # Search parent company data
    ALTERNATIVE_SOURCES = "alternative_sources"  # Try different data sources
    RELAXED_QUERIES = "relaxed_queries"  # Broader search terms
    REGIONAL_SOURCES = "regional_sources"  # Country-specific sources
    ARCHIVED_DATA = "archived_data"  # Search web archive
    PRESS_RELEASES = "press_releases"  # Company announcements
    NONE = "none"  # No retry possible


@dataclass
class SectionCoverage:
    """Coverage assessment for a report section."""
    section_name: str
    expected_fields: int
    found_fields: int
    missing_fields: List[str]
    coverage_pct: float
    has_specific_data: bool  # Has actual numbers, not just text

    @property
    def is_adequate(self) -> bool:
        return self.coverage_pct >= 40.0 and self.has_specific_data


@dataclass
class ThresholdResult:
    """Result of threshold checking."""
    passes_threshold: bool
    sufficiency: DataSufficiency
    overall_coverage: float
    section_coverages: List[SectionCoverage]
    missing_critical: List[str]
    recommended_strategies: List[RetryStrategy]
    can_proceed: bool
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passes_threshold": self.passes_threshold,
            "sufficiency": self.sufficiency.value,
            "overall_coverage": round(self.overall_coverage, 1),
            "can_proceed": self.can_proceed,
            "explanation": self.explanation,
            "missing_critical": self.missing_critical,
            "recommended_strategies": [s.value for s in self.recommended_strategies],
            "sections": [
                {
                    "name": s.section_name,
                    "coverage": round(s.coverage_pct, 1),
                    "missing": s.missing_fields
                }
                for s in self.section_coverages
            ]
        }


class DataThresholdChecker:
    """
    Check if research data meets minimum thresholds.

    Usage:
        checker = DataThresholdChecker()

        # Check before report generation
        result = checker.check(research_data)

        if not result.passes_threshold:
            print(f"Insufficient data: {result.explanation}")
            print(f"Recommended strategies: {result.recommended_strategies}")

            # Implement retry strategies
            for strategy in result.recommended_strategies:
                additional_data = retry_with_strategy(strategy)
                research_data.update(additional_data)

            # Check again
            result = checker.check(research_data)
    """

    # Section definitions with expected fields
    SECTION_REQUIREMENTS: Dict[str, Dict[str, Any]] = {
        "financial": {
            "weight": 30,  # Importance weight
            "min_coverage": 40,  # Minimum coverage percentage
            "expected_fields": [
                "revenue",
                "net_income",
                "profit_margin",
                "revenue_growth",
                "ebitda",
                "eps",
            ],
            "critical_fields": ["revenue"],
            "value_patterns": [
                r'\$[\d,]+(?:\.\d+)?(?:\s*(?:billion|million|B|M))?',
                r'[\d,]+(?:\.\d+)?\s*%',
            ],
        },
        "market": {
            "weight": 20,
            "min_coverage": 30,
            "expected_fields": [
                "market_cap",
                "market_share",
                "pe_ratio",
                "stock_price",
                "52_week_range",
            ],
            "critical_fields": ["market_cap"],
            "value_patterns": [
                r'\$[\d,]+(?:\.\d+)?(?:\s*(?:trillion|billion|million|T|B|M))?',
                r'[\d,]+(?:\.\d+)?\s*%',
            ],
        },
        "company_info": {
            "weight": 15,
            "min_coverage": 50,
            "expected_fields": [
                "headquarters",
                "employees",
                "founded",
                "ceo",
                "description",
            ],
            "critical_fields": ["headquarters", "employees"],
            "value_patterns": [],  # Text fields OK
        },
        "competitive": {
            "weight": 15,
            "min_coverage": 25,
            "expected_fields": [
                "competitors",
                "competitive_advantages",
                "market_position",
            ],
            "critical_fields": [],
            "value_patterns": [],
        },
        "products": {
            "weight": 10,
            "min_coverage": 25,
            "expected_fields": [
                "main_products",
                "services",
                "revenue_breakdown",
            ],
            "critical_fields": [],
            "value_patterns": [],
        },
        "strategy": {
            "weight": 10,
            "min_coverage": 20,
            "expected_fields": [
                "growth_strategy",
                "recent_developments",
                "future_outlook",
            ],
            "critical_fields": [],
            "value_patterns": [],
        },
    }

    # Patterns indicating missing data
    MISSING_DATA_PATTERNS = [
        r'data\s+not\s+available',
        r'not\s+available',
        r'n/?a\b',
        r'information\s+not\s+found',
        r'no\s+data',
        r'unable\s+to\s+find',
        r'could\s+not\s+be\s+determined',
        r'not\s+disclosed',
        r'not\s+provided',
        r'unavailable',
        r'\-\s*$',  # Just a dash
        r'^\s*\?\s*$',  # Just a question mark
    ]

    # Minimum thresholds
    THRESHOLDS = {
        "minimum_overall": 25.0,  # Must have at least 25% coverage
        "minimum_sections_ok": 2,  # At least 2 sections must be adequate
        "critical_must_have": True,  # Must have critical fields
    }

    def __init__(self):
        self._missing_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.MISSING_DATA_PATTERNS
        ]

    def check(
        self,
        research_data: Dict[str, Any],
        strict_mode: bool = False
    ) -> ThresholdResult:
        """
        Check if research data meets minimum thresholds.

        Args:
            research_data: The gathered research data
            strict_mode: If True, applies stricter thresholds

        Returns:
            ThresholdResult with detailed assessment
        """
        # Analyze each section
        section_coverages = []
        missing_critical = []

        for section_name, requirements in self.SECTION_REQUIREMENTS.items():
            coverage = self._analyze_section(
                research_data,
                section_name,
                requirements
            )
            section_coverages.append(coverage)

            # Track missing critical fields
            for field in requirements.get("critical_fields", []):
                if field in coverage.missing_fields:
                    missing_critical.append(f"{section_name}.{field}")

        # Calculate overall coverage (weighted)
        total_weight = sum(r["weight"] for r in self.SECTION_REQUIREMENTS.values())
        weighted_coverage = sum(
            c.coverage_pct * self.SECTION_REQUIREMENTS[c.section_name]["weight"]
            for c in section_coverages
        ) / total_weight

        # Determine sufficiency level
        sufficiency = self._determine_sufficiency(weighted_coverage)

        # Count adequate sections
        adequate_sections = sum(1 for c in section_coverages if c.is_adequate)

        # Check thresholds
        passes = (
            weighted_coverage >= self.THRESHOLDS["minimum_overall"]
            and adequate_sections >= self.THRESHOLDS["minimum_sections_ok"]
        )

        if strict_mode:
            passes = passes and len(missing_critical) == 0

        # Determine recommended retry strategies
        strategies = self._recommend_strategies(
            section_coverages,
            missing_critical,
            research_data
        )

        # Can we proceed even if threshold not met?
        can_proceed = (
            weighted_coverage >= 15.0
            and adequate_sections >= 1
        )

        # Generate explanation
        explanation = self._generate_explanation(
            weighted_coverage,
            adequate_sections,
            len(section_coverages),
            missing_critical
        )

        return ThresholdResult(
            passes_threshold=passes,
            sufficiency=sufficiency,
            overall_coverage=weighted_coverage,
            section_coverages=section_coverages,
            missing_critical=missing_critical,
            recommended_strategies=strategies,
            can_proceed=can_proceed,
            explanation=explanation
        )

    def _analyze_section(
        self,
        research_data: Dict,
        section_name: str,
        requirements: Dict
    ) -> SectionCoverage:
        """Analyze coverage for a specific section."""
        expected_fields = requirements["expected_fields"]
        found_fields = []
        missing_fields = []

        # Get section content
        content = self._get_section_content(research_data, section_name)
        content_lower = content.lower()

        # Check each expected field
        for field in expected_fields:
            if self._field_has_data(content_lower, field):
                found_fields.append(field)
            else:
                missing_fields.append(field)

        # Check for specific data values
        value_patterns = requirements.get("value_patterns", [])
        has_specific_data = any(
            re.search(p, content) for p in value_patterns
        ) if value_patterns else len(found_fields) > 0

        # Calculate coverage
        coverage_pct = (len(found_fields) / len(expected_fields) * 100) if expected_fields else 0

        return SectionCoverage(
            section_name=section_name,
            expected_fields=len(expected_fields),
            found_fields=len(found_fields),
            missing_fields=missing_fields,
            coverage_pct=coverage_pct,
            has_specific_data=has_specific_data
        )

    def _get_section_content(
        self,
        research_data: Dict,
        section_name: str
    ) -> str:
        """Extract content for a specific section."""
        # Map section names to potential data keys
        section_keys = {
            "financial": ["financial", "financials", "financial_analysis",
                         "agent_outputs.financial"],
            "market": ["market", "market_position", "market_analysis",
                      "agent_outputs.market"],
            "company_info": ["company_overview", "overview", "company_info",
                           "profile"],
            "competitive": ["competitive", "competitors", "competitive_analysis",
                          "agent_outputs.competitor"],
            "products": ["products", "services", "products_services",
                        "agent_outputs.product"],
            "strategy": ["strategy", "growth", "outlook", "strategic"],
        }

        content_parts = []

        for key in section_keys.get(section_name, []):
            value = self._get_nested_value(research_data, key)
            if value:
                content_parts.append(str(value))

        return "\n".join(content_parts)

    def _get_nested_value(self, data: Dict, key: str) -> Any:
        """Get a nested value from a dictionary using dot notation."""
        keys = key.split(".")
        value = data

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None

        return value

    def _field_has_data(self, content: str, field: str) -> bool:
        """Check if a field has actual data (not missing)."""
        # Convert field name to searchable terms
        field_terms = field.replace("_", " ").split()

        # Check if field is mentioned
        field_mentioned = all(term in content for term in field_terms)

        if not field_mentioned:
            return False

        # Check for "not available" patterns near the field
        for pattern in self._missing_patterns:
            # Look for field mention followed by missing indicator
            context_pattern = f"{'|'.join(field_terms)}.*?{pattern.pattern}"
            if re.search(context_pattern, content, re.IGNORECASE | re.DOTALL):
                return False

        return True

    def _determine_sufficiency(self, coverage: float) -> DataSufficiency:
        """Determine sufficiency level from coverage percentage."""
        if coverage >= 80:
            return DataSufficiency.EXCELLENT
        elif coverage >= 60:
            return DataSufficiency.GOOD
        elif coverage >= 40:
            return DataSufficiency.ADEQUATE
        elif coverage >= 20:
            return DataSufficiency.POOR
        else:
            return DataSufficiency.INSUFFICIENT

    def _recommend_strategies(
        self,
        section_coverages: List[SectionCoverage],
        missing_critical: List[str],
        research_data: Dict
    ) -> List[RetryStrategy]:
        """Recommend retry strategies based on gaps."""
        strategies = []

        # Check if any section has very low coverage
        low_coverage_sections = [
            c for c in section_coverages if c.coverage_pct < 20
        ]

        if low_coverage_sections:
            # Regional company likely - try multilingual
            strategies.append(RetryStrategy.MULTILINGUAL)
            strategies.append(RetryStrategy.REGIONAL_SOURCES)

        # Check for subsidiary indicators
        company_name = research_data.get("company_name", "").lower()
        subsidiary_indicators = ["subsidiary", "division", "unit", "claro", "oxxo"]
        if any(ind in company_name for ind in subsidiary_indicators):
            strategies.append(RetryStrategy.PARENT_COMPANY)

        # If financial data is missing
        financial_coverage = next(
            (c for c in section_coverages if c.section_name == "financial"),
            None
        )
        if financial_coverage and financial_coverage.coverage_pct < 30:
            strategies.append(RetryStrategy.PRESS_RELEASES)
            strategies.append(RetryStrategy.ALTERNATIVE_SOURCES)

        # If everything is low, try broader searches
        overall_low = sum(c.coverage_pct for c in section_coverages) / len(section_coverages) < 30
        if overall_low:
            strategies.append(RetryStrategy.RELAXED_QUERIES)

        # Deduplicate while preserving order
        seen = set()
        unique_strategies = []
        for s in strategies:
            if s not in seen:
                seen.add(s)
                unique_strategies.append(s)

        return unique_strategies[:5]  # Return top 5 strategies

    def _generate_explanation(
        self,
        coverage: float,
        adequate_sections: int,
        total_sections: int,
        missing_critical: List[str]
    ) -> str:
        """Generate human-readable explanation."""
        parts = []

        parts.append(f"Overall data coverage: {coverage:.1f}%")
        parts.append(f"Adequate sections: {adequate_sections}/{total_sections}")

        if missing_critical:
            parts.append(f"Missing critical data: {', '.join(missing_critical)}")

        if coverage < 25:
            parts.append("INSUFFICIENT DATA for report generation. Recommend retry with alternative strategies.")
        elif coverage < 40:
            parts.append("POOR coverage. Report would have significant gaps.")
        elif coverage < 60:
            parts.append("ADEQUATE coverage. Report can be generated with noted limitations.")
        else:
            parts.append("GOOD coverage. Report quality should be acceptable.")

        return " | ".join(parts)

    def check_source_count(
        self,
        sources: List[Dict],
        minimum: int = 5
    ) -> Tuple[bool, str]:
        """
        Quick check on source count.

        Args:
            sources: List of sources
            minimum: Minimum required sources

        Returns:
            Tuple of (passes, explanation)
        """
        count = len(sources) if sources else 0

        if count >= minimum:
            return True, f"Source count OK: {count} sources"
        else:
            return False, f"Insufficient sources: {count} (need {minimum})"


# Convenience functions

def check_data_threshold(
    research_data: Dict[str, Any],
    strict: bool = False
) -> ThresholdResult:
    """
    Check if research data meets minimum thresholds.

    Args:
        research_data: The research data to check
        strict: Whether to use strict mode

    Returns:
        ThresholdResult with assessment
    """
    checker = DataThresholdChecker()
    return checker.check(research_data, strict_mode=strict)


def should_generate_report(
    research_data: Dict[str, Any]
) -> Tuple[bool, str]:
    """
    Quick check if report should be generated.

    Returns:
        Tuple of (should_generate, reason)
    """
    result = check_data_threshold(research_data)

    if result.passes_threshold:
        return True, "Data threshold met"
    elif result.can_proceed:
        return True, f"Below threshold but can proceed: {result.explanation}"
    else:
        return False, f"Cannot generate report: {result.explanation}"
