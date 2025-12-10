"""
Data Threshold Checker - Validates search results quality before analysis.

This module provides:
- Minimum data coverage requirements
- Source quality scoring
- Content richness assessment
- Early abort/retry decisions
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """Strategies for retrying when data is insufficient."""
    MULTILINGUAL = "multilingual"
    PARENT_COMPANY = "parent_company"
    ALTERNATIVE_NAMES = "alternative_names"
    BROADER_QUERIES = "broader_queries"
    INDUSTRY_FOCUS = "industry_focus"


@dataclass
class ThresholdResult:
    """Result of threshold checking."""
    passes_threshold: bool
    coverage_score: float  # 0-100
    source_count: int
    unique_domains: int
    content_richness: float  # 0-100
    has_financial_data: bool
    has_company_info: bool
    has_product_data: bool
    retry_strategies: List[RetryStrategy]
    issues: List[str]
    summary: str


class DataThresholdChecker:
    """Checks if search results meet minimum data thresholds."""

    # Thresholds by company type
    THRESHOLDS = {
        "public": {
            "min_sources": 5,
            "min_unique_domains": 3,
            "min_content_chars": 2000,
            "required_categories": ["financial", "company_info"],
            "min_coverage_score": 40,
        },
        "private": {
            "min_sources": 3,
            "min_unique_domains": 2,
            "min_content_chars": 1000,
            "required_categories": ["company_info"],
            "min_coverage_score": 30,
        },
        "startup": {
            "min_sources": 3,
            "min_unique_domains": 2,
            "min_content_chars": 800,
            "required_categories": ["company_info"],
            "min_coverage_score": 25,
        },
        "subsidiary": {
            "min_sources": 2,
            "min_unique_domains": 1,
            "min_content_chars": 500,
            "required_categories": [],
            "min_coverage_score": 20,
        },
    }

    # Patterns for detecting data categories
    CATEGORY_PATTERNS = {
        "financial": [
            r"revenue|ingresos|receita|faturamento",
            r"(?:market\s*)?cap(?:italization)?|valorização",
            r"profit|lucro|beneficio|ganancia",
            r"(?:\$|€|£|R\$|MXN)\s*[\d.,]+\s*(?:billion|million|B|M|bn|mn|milhões|millones)",
            r"earnings|EBITDA|EPS",
            r"funding|raised|levantou|recaudó",
        ],
        "company_info": [
            r"founded|established|fundada|fundado|establecida",
            r"headquarter|based\s+in|sede|ubicada",
            r"employees?|empleados|funcionários|colaboradores",
            r"CEO|founder|fundador|director",
            r"company\s+(?:overview|profile|description)",
        ],
        "product": [
            r"products?|services?|productos|servicios|produtos|serviços",
            r"offers?|provides?|ofrece|oferece",
            r"platform|solution|solución|solução",
            r"technology|tecnología|tecnologia",
        ],
        "market": [
            r"market\s*share|participación|participação",
            r"competitors?|competidores|concorrentes",
            r"industry|sector|industria|setor",
            r"leader|líder",
        ],
    }

    def __init__(self, custom_thresholds: Optional[Dict[str, Any]] = None):
        """
        Initialize the threshold checker.

        Args:
            custom_thresholds: Optional custom threshold overrides
        """
        self.thresholds = self.THRESHOLDS.copy()
        if custom_thresholds:
            for company_type, values in custom_thresholds.items():
                if company_type in self.thresholds:
                    self.thresholds[company_type].update(values)

    def check_threshold(
        self,
        results: List[Dict[str, Any]],
        company_name: str,
        company_type: str = "public"
    ) -> ThresholdResult:
        """
        Check if search results meet minimum data thresholds.

        Args:
            results: List of search result dictionaries
            company_name: Name of the company being researched
            company_type: Type of company (public, private, startup, subsidiary)

        Returns:
            ThresholdResult with coverage assessment
        """
        logger.info(f"Checking data threshold for {company_name} ({company_type})")

        threshold = self.thresholds.get(company_type, self.thresholds["public"])
        issues = []
        retry_strategies = []

        # Count sources and unique domains
        source_count = len(results)
        unique_domains = self._count_unique_domains(results)

        # Calculate content richness
        total_content = self._aggregate_content(results)
        content_length = len(total_content)
        content_richness = min(100, (content_length / threshold["min_content_chars"]) * 50)

        # Check for data categories
        categories_found = self._detect_categories(total_content)
        has_financial = "financial" in categories_found
        has_company_info = "company_info" in categories_found
        has_product = "product" in categories_found

        # Calculate coverage score
        coverage_score = self._calculate_coverage_score(
            source_count=source_count,
            unique_domains=unique_domains,
            content_length=content_length,
            categories_found=categories_found,
            threshold=threshold
        )

        # Check against thresholds
        if source_count < threshold["min_sources"]:
            issues.append(f"Insufficient sources: {source_count} < {threshold['min_sources']}")
            retry_strategies.append(RetryStrategy.BROADER_QUERIES)

        if unique_domains < threshold["min_unique_domains"]:
            issues.append(f"Limited source diversity: {unique_domains} unique domains")
            retry_strategies.append(RetryStrategy.ALTERNATIVE_NAMES)

        if content_length < threshold["min_content_chars"]:
            issues.append(f"Insufficient content: {content_length} chars < {threshold['min_content_chars']}")
            retry_strategies.append(RetryStrategy.MULTILINGUAL)

        # Check required categories
        for required_cat in threshold["required_categories"]:
            if required_cat not in categories_found:
                issues.append(f"Missing required data: {required_cat}")
                if required_cat == "financial":
                    retry_strategies.append(RetryStrategy.INDUSTRY_FOCUS)
                retry_strategies.append(RetryStrategy.MULTILINGUAL)

        # Determine if threshold is passed
        passes_threshold = (
            coverage_score >= threshold["min_coverage_score"]
            and source_count >= threshold["min_sources"] // 2  # Allow some flexibility
        )

        # Add parent company strategy if content seems to be about a subsidiary
        if self._looks_like_subsidiary(total_content, company_name):
            retry_strategies.append(RetryStrategy.PARENT_COMPANY)

        # Remove duplicates from retry strategies
        retry_strategies = list(dict.fromkeys(retry_strategies))

        # Generate summary
        summary = self._generate_summary(
            company_name=company_name,
            passes_threshold=passes_threshold,
            coverage_score=coverage_score,
            source_count=source_count,
            issues=issues
        )

        logger.info(
            f"Threshold check complete: passes={passes_threshold}, "
            f"score={coverage_score:.1f}, sources={source_count}"
        )

        return ThresholdResult(
            passes_threshold=passes_threshold,
            coverage_score=coverage_score,
            source_count=source_count,
            unique_domains=unique_domains,
            content_richness=content_richness,
            has_financial_data=has_financial,
            has_company_info=has_company_info,
            has_product_data=has_product,
            retry_strategies=retry_strategies,
            issues=issues,
            summary=summary
        )

    def _count_unique_domains(self, results: List[Dict]) -> int:
        """Count unique domains in search results."""
        domains = set()
        for result in results:
            url = result.get("url", "")
            if url:
                # Extract domain from URL
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    domain = parsed.netloc.replace("www.", "")
                    if domain:
                        domains.add(domain)
                except Exception:
                    pass
        return len(domains)

    def _aggregate_content(self, results: List[Dict]) -> str:
        """Aggregate content from all search results."""
        content_parts = []
        for result in results:
            content = result.get("content", "")
            if content:
                content_parts.append(content)
        return " ".join(content_parts)

    def _detect_categories(self, content: str) -> List[str]:
        """Detect which data categories are present in content."""
        content_lower = content.lower()
        categories_found = []

        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    categories_found.append(category)
                    break

        return categories_found

    def _calculate_coverage_score(
        self,
        source_count: int,
        unique_domains: int,
        content_length: int,
        categories_found: List[str],
        threshold: Dict
    ) -> float:
        """Calculate overall coverage score."""
        # Source score (max 30 points)
        source_score = min(30, (source_count / threshold["min_sources"]) * 30)

        # Diversity score (max 20 points)
        diversity_score = min(20, (unique_domains / threshold["min_unique_domains"]) * 20)

        # Content score (max 30 points)
        content_score = min(30, (content_length / threshold["min_content_chars"]) * 30)

        # Category score (max 20 points)
        total_categories = len(self.CATEGORY_PATTERNS)
        category_score = (len(categories_found) / total_categories) * 20

        return source_score + diversity_score + content_score + category_score

    def _looks_like_subsidiary(self, content: str, company_name: str) -> bool:
        """Check if content suggests the company is a subsidiary."""
        subsidiary_patterns = [
            r"subsidiary\s+of",
            r"owned\s+by",
            r"part\s+of",
            r"division\s+of",
            r"filial\s+de",  # Spanish
            r"subsidiária\s+de",  # Portuguese
        ]
        content_lower = content.lower()
        return any(re.search(p, content_lower) for p in subsidiary_patterns)

    def _generate_summary(
        self,
        company_name: str,
        passes_threshold: bool,
        coverage_score: float,
        source_count: int,
        issues: List[str]
    ) -> str:
        """Generate a summary of the threshold check."""
        status = "✅ PASS" if passes_threshold else "❌ FAIL"

        summary_lines = [
            f"Data Threshold Check: {status}",
            f"Company: {company_name}",
            f"Coverage Score: {coverage_score:.1f}/100",
            f"Sources Found: {source_count}",
        ]

        if issues:
            summary_lines.append(f"Issues: {len(issues)}")
            for issue in issues[:3]:
                summary_lines.append(f"  - {issue}")

        return "\n".join(summary_lines)


def create_threshold_checker(
    custom_thresholds: Optional[Dict] = None
) -> DataThresholdChecker:
    """Factory function to create DataThresholdChecker."""
    return DataThresholdChecker(custom_thresholds=custom_thresholds)
