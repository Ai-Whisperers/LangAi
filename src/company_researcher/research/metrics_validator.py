"""
Required Metrics Validation System.

Addresses Issue #2: Vague Financial Statements Without Exact Figures.

Validates that research outputs contain required metrics with:
1. Actual numeric values (not just percentages or vague statements)
2. Time period specification (FY2024, Q4 2024, etc.)
3. Source attribution
4. Currency specification for financial values

Different validation profiles for:
- Public companies (strict requirements)
- Private companies (relaxed requirements)
- Subsidiaries (different expectations)
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from ..utils import get_logger

logger = get_logger(__name__)


class CompanyType(Enum):
    """Types of companies with different validation requirements."""

    PUBLIC = "public"
    PRIVATE = "private"
    SUBSIDIARY = "subsidiary"
    STARTUP = "startup"
    GOVERNMENT = "government"
    NONPROFIT = "nonprofit"

    # Aliases for backward compatibility with agents/research/ version
    PUBLIC_COMPANY = "public"
    PRIVATE_COMPANY = "private"
    UNKNOWN = "unknown"


class DataCategory(Enum):
    """Categories of company data for validation."""

    COMPANY_BASICS = "company_basics"
    FINANCIAL = "financial"
    PRODUCTS = "products"
    MARKET = "market"
    COMPETITIVE = "competitive"
    LEADERSHIP = "leadership"


class MetricStatus(Enum):
    """Status of a metric validation."""

    PRESENT = "present"  # Metric found with valid value
    PARTIAL = "partial"  # Metric found but missing required attributes
    MISSING = "missing"  # Metric not found
    INVALID = "invalid"  # Metric found but value is invalid


class MetricPriority(Enum):
    """Priority level for metrics."""

    CRITICAL = "critical"  # Must have
    HIGH = "high"  # Should have
    MEDIUM = "medium"  # Nice to have
    LOW = "low"  # Optional


@dataclass
class MetricDefinition:
    """Definition of a required metric."""

    name: str
    display_name: str
    priority: MetricPriority
    requires_value: bool = True  # Must have numeric value
    requires_period: bool = True  # Must specify time period
    requires_source: bool = True  # Must cite source
    requires_currency: bool = False  # Must specify currency
    value_patterns: List[str] = field(default_factory=list)  # Regex patterns to find value
    keywords: List[str] = field(default_factory=list)  # Keywords to identify this metric


@dataclass
class MetricValidation:
    """Result of validating a single metric."""

    metric: MetricDefinition
    status: MetricStatus
    found_value: Optional[Any] = None
    found_period: Optional[str] = None
    found_source: Optional[str] = None
    found_currency: Optional[str] = None
    raw_text: Optional[str] = None
    issues: List[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        """Check if metric validation is complete."""
        return self.status == MetricStatus.PRESENT

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric": self.metric.name,
            "display_name": self.metric.display_name,
            "status": self.status.value,
            "priority": self.metric.priority.value,
            "value": self.found_value,
            "period": self.found_period,
            "source": self.found_source,
            "currency": self.found_currency,
            "issues": self.issues,
        }


@dataclass
class ValidationReport:
    """Complete validation report for a research output."""

    company_name: str
    company_type: CompanyType
    validations: List[MetricValidation]
    overall_score: float  # 0-100
    critical_missing: List[str]  # Critical metrics that are missing
    recommendations: List[str]
    is_publishable: bool  # Meets minimum threshold
    # New fields from agents/research/ consolidation
    retry_recommended: bool = False  # Whether retry with more queries is recommended
    recommended_queries: List[str] = field(default_factory=list)  # Queries to fill gaps

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_name": self.company_name,
            "company_type": self.company_type.value,
            "overall_score": round(self.overall_score, 1),
            "is_publishable": self.is_publishable,
            "critical_missing": self.critical_missing,
            "recommendations": self.recommendations,
            "retry_recommended": self.retry_recommended,
            "recommended_queries": self.recommended_queries,
            "metrics": [v.to_dict() for v in self.validations],
            "summary": {
                "total_metrics": len(self.validations),
                "present": sum(1 for v in self.validations if v.status == MetricStatus.PRESENT),
                "partial": sum(1 for v in self.validations if v.status == MetricStatus.PARTIAL),
                "missing": sum(1 for v in self.validations if v.status == MetricStatus.MISSING),
            },
        }

    # Alias properties for backward compatibility with agents/research/ ValidationResult
    @property
    def is_valid(self) -> bool:
        """Alias for is_publishable (backward compatibility)."""
        return self.is_publishable

    @property
    def score(self) -> float:
        """Alias for overall_score (backward compatibility)."""
        return self.overall_score

    @property
    def can_generate_report(self) -> bool:
        """Alias for is_publishable (backward compatibility)."""
        return self.is_publishable

    @property
    def metrics_found(self) -> Dict[str, Any]:
        """Get found metrics as dict (backward compatibility)."""
        return {
            v.metric.name: v.found_value
            for v in self.validations
            if v.status == MetricStatus.PRESENT
        }

    @property
    def metrics_missing(self) -> List[str]:
        """Get missing metric names (backward compatibility)."""
        return [v.metric.name for v in self.validations if v.status == MetricStatus.MISSING]

    @property
    def warnings(self) -> List[str]:
        """Get all issues as warnings (backward compatibility)."""
        warnings = []
        for v in self.validations:
            if v.issues:
                for issue in v.issues:
                    warnings.append(f"{v.metric.display_name}: {issue}")
        return warnings


class MetricsValidator:
    """
    Validate research outputs for required metrics.

    Usage:
        validator = MetricsValidator()

        # Validate a research output
        report = validator.validate(
            research_output,
            company_name="Apple Inc.",
            company_type=CompanyType.PUBLIC
        )

        if not report.is_publishable:
            print(f"Missing critical metrics: {report.critical_missing}")
    """

    # Metric definitions by company type
    METRIC_DEFINITIONS: Dict[CompanyType, List[MetricDefinition]] = {
        CompanyType.PUBLIC: [
            # Critical - Must have
            MetricDefinition(
                name="revenue",
                display_name="Annual Revenue",
                priority=MetricPriority.CRITICAL,
                requires_currency=True,
                value_patterns=[
                    r"\$\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?",
                    r"revenue\s+(?:of|was|is|:)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?",
                    r"([\d,]+(?:\.\d+)?)\s*(trillion|billion|million)\s+(?:in\s+)?(?:revenue|sales)",
                ],
                keywords=["revenue", "sales", "turnover", "top line"],
            ),
            MetricDefinition(
                name="net_income",
                display_name="Net Income",
                priority=MetricPriority.CRITICAL,
                requires_currency=True,
                value_patterns=[
                    r"net\s+income\s+(?:of|was|is|:)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?",
                    r"profit\s+(?:of|was|is|:)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?",
                    r"earnings\s+(?:of|was|is|:)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?",
                ],
                keywords=["net income", "profit", "earnings", "bottom line"],
            ),
            MetricDefinition(
                name="market_cap",
                display_name="Market Capitalization",
                priority=MetricPriority.CRITICAL,
                requires_currency=True,
                requires_period=False,  # Point-in-time
                value_patterns=[
                    r"market\s+cap(?:italization)?\s+(?:of|is|:)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?",
                    r"\$\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?\s+market\s+cap",
                ],
                keywords=["market cap", "market capitalization", "valuation"],
            ),
            # High priority
            MetricDefinition(
                name="employees",
                display_name="Employee Count",
                priority=MetricPriority.HIGH,
                requires_currency=False,
                value_patterns=[
                    r"([\d,]+)\s+employees",
                    r"employees?\s*:?\s*([\d,]+)",
                    r"workforce\s+(?:of|:)?\s*([\d,]+)",
                    r"headcount\s+(?:of|:)?\s*([\d,]+)",
                ],
                keywords=["employees", "workforce", "headcount", "staff"],
            ),
            MetricDefinition(
                name="eps",
                display_name="Earnings Per Share",
                priority=MetricPriority.HIGH,
                requires_currency=True,
                value_patterns=[
                    r"(?:EPS|earnings\s+per\s+share)\s*(?:of|is|was|:)?\s*\$?\s*([\d,]+(?:\.\d+)?)",
                    r"\$\s*([\d]+(?:\.\d+)?)\s+(?:per\s+share|EPS)",
                ],
                keywords=["eps", "earnings per share", "per share"],
            ),
            MetricDefinition(
                name="pe_ratio",
                display_name="P/E Ratio",
                priority=MetricPriority.HIGH,
                requires_currency=False,
                requires_period=False,
                value_patterns=[
                    r"(?:P/?E|price.to.earnings)\s*(?:ratio)?\s*(?:of|is|:)?\s*([\d,]+(?:\.\d+)?)",
                    r"([\d,]+(?:\.\d+)?)\s*(?:x|times)?\s*(?:P/?E|earnings)",
                ],
                keywords=["p/e", "pe ratio", "price to earnings"],
            ),
            # Medium priority
            MetricDefinition(
                name="profit_margin",
                display_name="Profit Margin",
                priority=MetricPriority.MEDIUM,
                requires_currency=False,
                value_patterns=[
                    r"(?:profit|net)\s+margin\s*(?:of|is|was|:)?\s*([\d,]+(?:\.\d+)?)\s*%",
                    r"([\d,]+(?:\.\d+)?)\s*%\s+(?:profit|net)\s+margin",
                ],
                keywords=["profit margin", "net margin", "margin"],
            ),
            MetricDefinition(
                name="revenue_growth",
                display_name="Revenue Growth",
                priority=MetricPriority.MEDIUM,
                requires_currency=False,
                value_patterns=[
                    r"(?:revenue|sales)\s+(?:grew|growth|increased)\s*(?:by)?\s*([\d,]+(?:\.\d+)?)\s*%",
                    r"([\d,]+(?:\.\d+)?)\s*%\s+(?:revenue|sales)\s+growth",
                ],
                keywords=["revenue growth", "sales growth", "yoy growth"],
            ),
            MetricDefinition(
                name="market_share",
                display_name="Market Share",
                priority=MetricPriority.MEDIUM,
                requires_currency=False,
                value_patterns=[
                    r"market\s+share\s*(?:of|is|:)?\s*([\d,]+(?:\.\d+)?)\s*%",
                    r"([\d,]+(?:\.\d+)?)\s*%\s+(?:of\s+the\s+)?market",
                ],
                keywords=["market share", "share of market"],
            ),
            # Company info
            MetricDefinition(
                name="headquarters",
                display_name="Headquarters Location",
                priority=MetricPriority.HIGH,
                requires_value=False,
                requires_period=False,
                requires_currency=False,
                value_patterns=[
                    r"headquartered?\s+(?:in|at)\s+([A-Z][a-zA-Z\s,]+)",
                    r"based\s+(?:in|at)\s+([A-Z][a-zA-Z\s,]+)",
                    r"headquarters?\s*(?:is|are|:)\s*(?:in|at)?\s*([A-Z][a-zA-Z\s,]+)",
                ],
                keywords=["headquarters", "based in", "located in", "hq"],
            ),
            MetricDefinition(
                name="ceo",
                display_name="CEO Name",
                priority=MetricPriority.HIGH,
                requires_value=False,
                requires_period=False,
                requires_currency=False,
                value_patterns=[
                    r"(?:CEO|chief\s+executive)\s*(?:is|:)?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)",
                    r"([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:is|serves\s+as)\s+(?:the\s+)?CEO",
                ],
                keywords=["ceo", "chief executive", "leader"],
            ),
            MetricDefinition(
                name="founded",
                display_name="Year Founded",
                priority=MetricPriority.MEDIUM,
                requires_value=False,
                requires_period=False,
                requires_currency=False,
                value_patterns=[
                    r"founded\s+(?:in\s+)?(\d{4})",
                    r"established\s+(?:in\s+)?(\d{4})",
                    r"since\s+(\d{4})",
                ],
                keywords=["founded", "established", "since"],
            ),
        ],
        CompanyType.PRIVATE: [
            # Relaxed requirements for private companies
            MetricDefinition(
                name="estimated_revenue",
                display_name="Estimated Revenue",
                priority=MetricPriority.HIGH,
                requires_currency=True,
                requires_source=True,
                value_patterns=[
                    r"(?:estimated\s+)?revenue\s+(?:of|was|is|:)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?",
                ],
                keywords=["revenue", "estimated revenue", "sales"],
            ),
            MetricDefinition(
                name="employees",
                display_name="Employee Count",
                priority=MetricPriority.CRITICAL,
                requires_currency=False,
                value_patterns=[
                    r"([\d,]+)\s+employees",
                    r"employees?\s*:?\s*([\d,]+)",
                ],
                keywords=["employees", "workforce", "headcount"],
            ),
            MetricDefinition(
                name="funding",
                display_name="Total Funding",
                priority=MetricPriority.HIGH,
                requires_currency=True,
                value_patterns=[
                    r"(?:raised|funding\s+of)\s+\$?\s*([\d,]+(?:\.\d+)?)\s*(million|billion|[MB])?",
                    r"\$\s*([\d,]+(?:\.\d+)?)\s*(million|billion|[MB])?\s+(?:in\s+)?funding",
                ],
                keywords=["funding", "raised", "investment"],
            ),
            MetricDefinition(
                name="headquarters",
                display_name="Headquarters",
                priority=MetricPriority.CRITICAL,
                requires_value=False,
                requires_period=False,
                requires_currency=False,
                value_patterns=[
                    r"headquartered?\s+(?:in|at)\s+([A-Z][a-zA-Z\s,]+)",
                    r"based\s+(?:in|at)\s+([A-Z][a-zA-Z\s,]+)",
                ],
                keywords=["headquarters", "based", "located"],
            ),
        ],
        CompanyType.SUBSIDIARY: [
            # For subsidiaries, we need different metrics
            MetricDefinition(
                name="parent_company",
                display_name="Parent Company",
                priority=MetricPriority.CRITICAL,
                requires_value=False,
                requires_period=False,
                requires_currency=False,
                value_patterns=[
                    r"(?:subsidiary|owned\s+by|part\s+of)\s+([A-Z][a-zA-Z\s]+)",
                    r"parent\s+company\s*(?:is|:)?\s*([A-Z][a-zA-Z\s]+)",
                ],
                keywords=["parent company", "subsidiary", "owned by"],
            ),
            MetricDefinition(
                name="employees",
                display_name="Employee Count",
                priority=MetricPriority.HIGH,
                requires_currency=False,
                value_patterns=[
                    r"([\d,]+)\s+employees",
                ],
                keywords=["employees", "workforce"],
            ),
            MetricDefinition(
                name="segment_revenue",
                display_name="Segment Revenue Contribution",
                priority=MetricPriority.HIGH,
                requires_currency=False,
                value_patterns=[
                    r"([\d,]+(?:\.\d+)?)\s*%\s+(?:of\s+)?(?:revenue|sales)",
                    r"contributes?\s+([\d,]+(?:\.\d+)?)\s*%",
                ],
                keywords=["segment", "contribution", "percentage of revenue"],
            ),
        ],
    }

    # Minimum thresholds for publishability by company type
    PUBLISHABILITY_THRESHOLDS: Dict[CompanyType, Dict[str, Any]] = {
        CompanyType.PUBLIC: {
            "min_score": 60,
            "max_critical_missing": 0,
            "min_high_present": 3,
        },
        CompanyType.PRIVATE: {
            "min_score": 40,
            "max_critical_missing": 1,
            "min_high_present": 2,
        },
        CompanyType.SUBSIDIARY: {
            "min_score": 35,
            "max_critical_missing": 1,
            "min_high_present": 1,
        },
    }

    def __init__(
        self, min_score: Optional[float] = None, critical_threshold: Optional[float] = None
    ):
        """
        Initialize MetricsValidator with optional custom thresholds.

        Args:
            min_score: Override minimum score for publishability (0-100).
                      If None, uses company-type specific defaults.
            critical_threshold: Fraction of critical metrics allowed to be missing (0-1).
                              If None, uses company-type specific defaults.
        """
        self._patterns_compiled = {}
        self._custom_min_score = min_score
        self._custom_critical_threshold = critical_threshold

    def validate(
        self,
        research_output: Dict[str, Any],
        company_name: str,
        company_type: CompanyType = CompanyType.PUBLIC,
    ) -> ValidationReport:
        """
        Validate research output for required metrics.

        Args:
            research_output: The research data to validate
            company_name: Name of the company
            company_type: Type of company (affects requirements)

        Returns:
            ValidationReport with detailed results
        """
        # Get text content from research output
        text_content = self._extract_text(research_output)

        # Get metric definitions for this company type
        metrics = self.METRIC_DEFINITIONS.get(
            company_type, self.METRIC_DEFINITIONS[CompanyType.PUBLIC]
        )

        # Validate each metric
        validations = []
        for metric in metrics:
            validation = self._validate_metric(metric, text_content)
            validations.append(validation)

        # Calculate overall score
        score = self._calculate_score(validations)

        # Check publishability
        critical_missing = [
            v.metric.display_name
            for v in validations
            if v.status == MetricStatus.MISSING and v.metric.priority == MetricPriority.CRITICAL
        ]

        thresholds = self.PUBLISHABILITY_THRESHOLDS.get(
            company_type, self.PUBLISHABILITY_THRESHOLDS[CompanyType.PUBLIC]
        )

        # Apply custom thresholds if set
        effective_min_score = (
            self._custom_min_score
            if self._custom_min_score is not None
            else thresholds["min_score"]
        )
        effective_max_critical_missing = thresholds["max_critical_missing"]
        if self._custom_critical_threshold is not None:
            # Convert threshold fraction to max missing count
            total_critical = sum(
                1 for v in validations if v.metric.priority == MetricPriority.CRITICAL
            )
            effective_max_critical_missing = int(total_critical * self._custom_critical_threshold)

        high_present = sum(
            1
            for v in validations
            if v.status == MetricStatus.PRESENT and v.metric.priority == MetricPriority.HIGH
        )

        is_publishable = (
            score >= effective_min_score
            and len(critical_missing) <= effective_max_critical_missing
            and high_present >= thresholds["min_high_present"]
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(validations)

        # Determine if retry is recommended (from agents/research/ consolidation)
        retry_recommended = not is_publishable and score < 60

        # Generate retry queries for missing data (from agents/research/ consolidation)
        missing_metric_names = [
            v.metric.name for v in validations if v.status == MetricStatus.MISSING
        ]
        recommended_queries = self._generate_retry_queries(
            company_name, missing_metric_names, company_type
        )

        return ValidationReport(
            company_name=company_name,
            company_type=company_type,
            validations=validations,
            overall_score=score,
            critical_missing=critical_missing,
            recommendations=recommendations,
            is_publishable=is_publishable,
            retry_recommended=retry_recommended,
            recommended_queries=recommended_queries,
        )

    def _extract_text(self, research_output: Dict) -> str:
        """Extract all text content from research output."""
        parts = []

        # Direct text fields
        for key in [
            "company_overview",
            "executive_summary",
            "financial_analysis",
            "market_position",
            "strategy",
            "report",
        ]:
            if key in research_output:
                parts.append(str(research_output[key]))

        # Agent outputs
        agent_outputs = research_output.get("agent_outputs", {})
        for agent_name, output in agent_outputs.items():
            if isinstance(output, dict):
                parts.append(str(output.get("summary", "")))
                parts.append(str(output.get("analysis", "")))
                parts.append(str(output.get("findings", "")))
            elif isinstance(output, str):
                parts.append(output)

        # Key metrics
        if "key_metrics" in research_output:
            parts.append(str(research_output["key_metrics"]))

        return "\n".join(parts)

    def _validate_metric(self, metric: MetricDefinition, text: str) -> MetricValidation:
        """Validate a single metric against the text."""
        validation = MetricValidation(metric=metric, status=MetricStatus.MISSING)

        # Check if any keywords are present
        text_lower = text.lower()
        keyword_found = any(kw in text_lower for kw in metric.keywords)

        if not keyword_found:
            return validation

        # Try to extract value using patterns
        for pattern in metric.value_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Found a match
                match = matches[0]
                if isinstance(match, tuple):
                    validation.found_value = match[0]
                else:
                    validation.found_value = match

                validation.status = MetricStatus.PARTIAL
                break

        # Check for period
        if metric.requires_period:
            period_patterns = [
                r"(?:FY|fiscal\s+year)\s*(\d{4})",
                r"Q[1-4]\s*(\d{4})",
                r"(?:in|for)\s+(\d{4})",
                r"(\d{4})\s+(?:annual|results)",
            ]
            for pattern in period_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    validation.found_period = match.group(0)
                    break

            if not validation.found_period:
                validation.issues.append("Missing time period specification")

        # Check for currency (for financial values)
        if metric.requires_currency:
            currency_patterns = [
                r"\$",  # USD
                r"USD",
                r"€|EUR",
                r"£|GBP",
                r"MX\$|MXN",  # Mexican Peso
                r"R\$|BRL",  # Brazilian Real
            ]
            currency_found = any(re.search(p, text) for p in currency_patterns)
            if currency_found:
                validation.found_currency = "detected"
            elif validation.found_value:
                validation.issues.append("Missing currency specification")

        # Determine final status
        if validation.found_value:
            issues_count = len(validation.issues)
            if issues_count == 0:
                validation.status = MetricStatus.PRESENT
            elif issues_count <= 1:
                validation.status = MetricStatus.PARTIAL
            else:
                validation.status = MetricStatus.PARTIAL
        elif keyword_found:
            validation.status = MetricStatus.PARTIAL
            validation.issues.append(f"Keyword found but no specific value extracted")

        return validation

    def _calculate_score(self, validations: List[MetricValidation]) -> float:
        """Calculate overall validation score."""
        if not validations:
            return 0.0

        # Weight by priority
        weights = {
            MetricPriority.CRITICAL: 4.0,
            MetricPriority.HIGH: 2.0,
            MetricPriority.MEDIUM: 1.0,
            MetricPriority.LOW: 0.5,
        }

        # Status scores
        status_scores = {
            MetricStatus.PRESENT: 1.0,
            MetricStatus.PARTIAL: 0.5,
            MetricStatus.MISSING: 0.0,
            MetricStatus.INVALID: 0.0,
        }

        total_weight = 0.0
        weighted_score = 0.0

        for v in validations:
            weight = weights.get(v.metric.priority, 1.0)
            score = status_scores.get(v.status, 0.0)

            total_weight += weight
            weighted_score += weight * score

        if total_weight == 0:
            return 0.0

        return (weighted_score / total_weight) * 100

    def detect_company_type(self, content: str, company_name: str) -> CompanyType:
        """
        Auto-detect the type of company from content.
        Ported from agents/research/metrics_validator.py for consolidation.

        Args:
            content: Extracted content to analyze
            company_name: Name of the company

        Returns:
            Detected CompanyType
        """
        content_lower = content.lower()

        # Check for public company indicators
        public_indicators = [
            r"ticker[:\s]+[A-Z]+",
            r"stock\s*(?:price|symbol)",
            r"market\s*cap",
            r"NYSE|NASDAQ|B3|BOVESPA|BMV|BCS|BYMA",
            r"publicly\s*traded",
            r"shares?\s*outstanding",
            r"SEC\s+filings?",
        ]
        for pattern in public_indicators:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return CompanyType.PUBLIC

        # Check for startup indicators
        startup_indicators = [
            r"series\s*[A-Z]",
            r"seed\s*(?:round|funding)",
            r"venture\s*capital",
            r"startup",
            r"unicorn",
            r"pre-seed|pre-series",
        ]
        for pattern in startup_indicators:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return CompanyType.STARTUP

        # Check for subsidiary indicators
        subsidiary_indicators = [
            r"subsidiary\s*of",
            r"owned\s*by",
            r"parent\s*company",
            r"division\s*of",
            r"part\s*of\s+[A-Z]",
        ]
        for pattern in subsidiary_indicators:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return CompanyType.SUBSIDIARY

        # Check for government indicators
        government_indicators = [
            r"government\s*(?:agency|owned|entity)",
            r"state-owned",
            r"public\s*sector",
        ]
        for pattern in government_indicators:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return CompanyType.GOVERNMENT

        # Default to private company
        return CompanyType.PRIVATE

    def _generate_retry_queries(
        self,
        company_name: str,
        missing_metrics: List[str],
        company_type: CompanyType,
    ) -> List[str]:
        """
        Generate targeted queries to fill data gaps.
        Ported from agents/research/metrics_validator.py for consolidation.

        Args:
            company_name: Name of the company
            missing_metrics: List of missing metric names
            company_type: Type of company

        Returns:
            List of recommended search queries
        """
        queries = []

        metric_query_map = {
            "revenue": [
                f"{company_name} annual revenue 2024",
                f"{company_name} financial results earnings",
                f"{company_name} ingresos anuales",  # Spanish
                f"{company_name} receita anual",  # Portuguese
            ],
            "net_income": [
                f"{company_name} net income profit 2024",
                f"{company_name} EBITDA earnings",
            ],
            "market_cap": [
                f"{company_name} stock price market cap",
                f"{company_name} market capitalization valuation",
            ],
            "employees": [
                f"{company_name} employees workforce size",
                f"{company_name} number of employees",
            ],
            "headquarters": [
                f"{company_name} headquarters location",
                f"{company_name} based where office",
            ],
            "ceo": [
                f"{company_name} CEO leadership executives",
                f"{company_name} who runs company founder",
            ],
            "founded": [
                f"{company_name} founded history when",
                f"{company_name} company history background",
            ],
            "market_share": [
                f"{company_name} market share position",
                f"{company_name} industry leadership ranking",
            ],
        }

        for metric in missing_metrics[:5]:  # Limit to top 5 gaps
            metric_key = metric.lower().replace(" ", "_")
            if metric_key in metric_query_map:
                queries.extend(metric_query_map[metric_key][:2])
            elif metric in metric_query_map:
                queries.extend(metric_query_map[metric][:2])

        return queries[:7]  # Return max 7 queries

    def get_data_quality_summary(self, report: ValidationReport) -> str:
        """
        Generate a human-readable data quality summary.
        Ported from agents/research/metrics_validator.py for consolidation.

        Args:
            report: ValidationReport to summarize

        Returns:
            Markdown-formatted summary string
        """
        lines = [
            f"## Data Quality Assessment",
            f"",
            f"**Score:** {report.overall_score:.1f}/100",
            f"**Company Type:** {report.company_type.value}",
            f"**Can Generate Report:** {'Yes' if report.is_publishable else 'No'}",
            f"**Retry Recommended:** {'Yes' if report.retry_recommended else 'No'}",
            f"",
        ]

        # Metrics found
        present_metrics = [v for v in report.validations if v.status == MetricStatus.PRESENT]
        if present_metrics:
            lines.append(f"### Metrics Found ({len(present_metrics)})")
            for v in present_metrics:
                value_str = (
                    str(v.found_value)[:50] + "..."
                    if v.found_value and len(str(v.found_value)) > 50
                    else str(v.found_value)
                )
                lines.append(f"- {v.metric.display_name}: {value_str}")
            lines.append("")

        # Missing metrics
        missing_metrics = [v for v in report.validations if v.status == MetricStatus.MISSING]
        if missing_metrics:
            lines.append(f"### Metrics Missing ({len(missing_metrics)})")
            for v in missing_metrics:
                prefix = "⚠️ CRITICAL: " if v.metric.priority == MetricPriority.CRITICAL else "- "
                lines.append(f"{prefix}{v.metric.display_name}")
            lines.append("")

        # Recommendations
        if report.recommendations:
            lines.append(f"### Recommendations")
            for rec in report.recommendations[:5]:
                lines.append(f"- {rec}")
            lines.append("")

        # Retry queries
        if report.recommended_queries:
            lines.append(f"### Suggested Queries for Missing Data")
            for query in report.recommended_queries[:5]:
                lines.append(f"- `{query}`")

        return "\n".join(lines)

    def _generate_recommendations(self, validations: List[MetricValidation]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []

        for v in validations:
            if v.status == MetricStatus.MISSING:
                if v.metric.priority == MetricPriority.CRITICAL:
                    recommendations.append(
                        f"CRITICAL: Add {v.metric.display_name} with specific value and source"
                    )
                elif v.metric.priority == MetricPriority.HIGH:
                    recommendations.append(f"HIGH: Include {v.metric.display_name} data")

            elif v.status == MetricStatus.PARTIAL:
                if v.issues:
                    for issue in v.issues:
                        recommendations.append(f"FIX {v.metric.display_name}: {issue}")

        return recommendations[:10]  # Limit to top 10


# Convenience function
def validate_research_metrics(
    research_output: Dict[str, Any], company_name: str, company_type: str = "public"
) -> ValidationReport:
    """
    Validate research output metrics.

    Args:
        research_output: Research data to validate
        company_name: Name of company
        company_type: "public", "private", or "subsidiary"

    Returns:
        ValidationReport with results
    """
    type_map = {
        "public": CompanyType.PUBLIC,
        "private": CompanyType.PRIVATE,
        "subsidiary": CompanyType.SUBSIDIARY,
    }

    validator = MetricsValidator()
    return validator.validate(
        research_output, company_name, type_map.get(company_type.lower(), CompanyType.PUBLIC)
    )


def create_metrics_validator(
    min_score: float = 60.0, critical_threshold: float = 0.5
) -> MetricsValidator:
    """
    Factory function to create MetricsValidator.
    Ported from agents/research/metrics_validator.py for consolidation.

    Args:
        min_score: Minimum score (0-100) to generate report (default 60)
        critical_threshold: Fraction of critical metrics allowed to be missing (default 0.5)
                          e.g., 0.5 means up to 50% of critical metrics can be missing

    Returns:
        Configured MetricsValidator instance
    """
    return MetricsValidator(min_score=min_score, critical_threshold=critical_threshold)


# Alias for backward compatibility with agents/research/ version
ValidationResult = ValidationReport
