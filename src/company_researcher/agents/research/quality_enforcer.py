"""
Quality Enforcer - Blocks report generation for insufficient data.

This module provides:
- Final quality gate before report generation
- Blocking mechanism for empty/low-quality reports
- User notification for data issues
- Suggestions for improvement
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
from ...utils import get_logger

logger = get_logger(__name__)


class ReportStatus(Enum):
    """Status of report generation."""
    APPROVED = "approved"
    BLOCKED = "blocked"
    WARNING = "warning"


class BlockReason(Enum):
    """Reasons for blocking report generation."""
    INSUFFICIENT_DATA = "insufficient_data"
    EMPTY_SECTIONS = "empty_sections"
    NO_FINANCIAL_DATA = "no_financial_data"
    NO_COMPANY_INFO = "no_company_info"
    CRITICAL_GAPS = "critical_gaps"
    LOW_CONFIDENCE = "low_confidence"


@dataclass
class QualityGateResult:
    """Result of quality gate check."""
    status: ReportStatus
    can_generate: bool
    block_reasons: List[BlockReason]
    quality_score: float
    section_scores: Dict[str, float]
    warnings: List[str]
    improvements: List[str]
    summary: str


class QualityEnforcer:
    """
    Enforces minimum quality standards for reports.

    Blocks report generation when critical data is missing.
    """

    # Minimum acceptable scores per section (0-100)
    SECTION_THRESHOLDS = {
        "company_overview": 30,
        "key_metrics": 25,
        "products": 20,
        "competitors": 15,
        "insights": 20,
    }

    # Patterns indicating missing/empty data
    EMPTY_PATTERNS = [
        r"not\s*available\s*(?:in\s*research)?",
        r"no\s*(?:data|information)\s*(?:available|found)?",
        r"data\s*not\s*(?:found|available)",
        r"information\s*(?:not\s*)?unavailable",
        r"N/?A",
        r"unknown",
        r"could\s*not\s*(?:be\s*)?(?:found|determined)",
        r"no\s*(?:research\s*)?sources?\s*(?:provided|found)",
    ]

    # Required sections for a valid report
    REQUIRED_SECTIONS = ["company_overview", "key_metrics"]

    def __init__(
        self,
        min_overall_score: float = 30.0,
        block_on_empty_required: bool = True,
        strict_mode: bool = False,
    ):
        """
        Initialize the quality enforcer.

        Args:
            min_overall_score: Minimum overall score to generate report
            block_on_empty_required: Block if required sections are empty
            strict_mode: Apply stricter quality standards
        """
        self.min_overall_score = min_overall_score
        self.block_on_empty_required = block_on_empty_required
        self.strict_mode = strict_mode

        if strict_mode:
            self.min_overall_score = max(50.0, min_overall_score)
            self.SECTION_THRESHOLDS = {k: v + 15 for k, v in self.SECTION_THRESHOLDS.items()}

    def check_quality(
        self,
        report_content: str,
        company_name: str,
        validation_score: Optional[float] = None,
    ) -> QualityGateResult:
        """
        Check if report meets quality standards.

        Args:
            report_content: The generated report content
            company_name: Name of the company
            validation_score: Optional pre-computed validation score

        Returns:
            QualityGateResult with decision and details
        """
        logger.info(f"Quality check for {company_name} report")

        block_reasons = []
        warnings = []
        improvements = []

        # Parse sections from report
        sections = self._parse_sections(report_content)

        # Score each section
        section_scores = {}
        for section_name, content in sections.items():
            score = self._score_section(section_name, content)
            section_scores[section_name] = score

            if score < self.SECTION_THRESHOLDS.get(section_name, 20):
                if section_name in self.REQUIRED_SECTIONS:
                    block_reasons.append(BlockReason.EMPTY_SECTIONS)
                    warnings.append(f"Critical section '{section_name}' has low quality (score: {score:.0f})")
                else:
                    warnings.append(f"Section '{section_name}' has low quality (score: {score:.0f})")

        # Calculate overall quality score
        if section_scores:
            overall_score = sum(section_scores.values()) / len(section_scores)
        else:
            overall_score = 0

        # Use validation score if provided
        if validation_score is not None:
            overall_score = (overall_score + validation_score) / 2

        # Check for specific issues
        issues = self._check_specific_issues(report_content, sections)
        block_reasons.extend(issues["blocks"])
        warnings.extend(issues["warnings"])
        improvements.extend(issues["improvements"])

        # Check overall score threshold
        if overall_score < self.min_overall_score:
            if BlockReason.INSUFFICIENT_DATA not in block_reasons:
                block_reasons.append(BlockReason.INSUFFICIENT_DATA)

        # Determine final status
        if block_reasons and self.block_on_empty_required:
            status = ReportStatus.BLOCKED
            can_generate = False
        elif warnings:
            status = ReportStatus.WARNING
            can_generate = True
        else:
            status = ReportStatus.APPROVED
            can_generate = True

        # Generate summary
        summary = self._generate_summary(
            company_name=company_name,
            status=status,
            overall_score=overall_score,
            block_reasons=block_reasons,
            warnings=warnings
        )

        logger.info(f"Quality gate result: {status.value}, score={overall_score:.1f}")

        return QualityGateResult(
            status=status,
            can_generate=can_generate,
            block_reasons=list(set(block_reasons)),
            quality_score=overall_score,
            section_scores=section_scores,
            warnings=warnings,
            improvements=improvements,
            summary=summary
        )

    def _parse_sections(self, content: str) -> Dict[str, str]:
        """Parse report content into sections."""
        sections = {}

        # Common section patterns
        section_patterns = [
            (r"##?\s*(?:Company\s*)?Overview", "company_overview"),
            (r"##?\s*(?:Key\s*)?Metrics", "key_metrics"),
            (r"##?\s*(?:Main\s*)?Products?\s*(?:&\s*)?(?:Services?)?", "products"),
            (r"##?\s*Competitors?", "competitors"),
            (r"##?\s*(?:Key\s*)?Insights?", "insights"),
            (r"##?\s*(?:Financial\s*)?Analysis", "financial"),
            (r"##?\s*(?:Market\s*)?(?:Position|Analysis)", "market"),
            (r"##?\s*Executive\s*Summary", "executive_summary"),
        ]

        # Split content by headers
        lines = content.split("\n")
        current_section = None
        current_content = []

        for line in lines:
            is_header = False
            for pattern, section_name in section_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    # Save previous section
                    if current_section:
                        sections[current_section] = "\n".join(current_content)

                    current_section = section_name
                    current_content = []
                    is_header = True
                    break

            if not is_header and current_section:
                current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = "\n".join(current_content)

        return sections

    def _score_section(self, section_name: str, content: str) -> float:
        """Score a section's quality from 0-100."""
        if not content or not content.strip():
            return 0

        score = 100.0
        content_lower = content.lower()

        # Penalty for empty patterns
        empty_count = 0
        for pattern in self.EMPTY_PATTERNS:
            matches = len(re.findall(pattern, content_lower))
            empty_count += matches

        # Heavy penalty for multiple "not available" mentions
        score -= min(60, empty_count * 15)

        # Check content length
        content_length = len(content.strip())
        if content_length < 50:
            score -= 40
        elif content_length < 100:
            score -= 25
        elif content_length < 200:
            score -= 10

        # Check for actual data points
        data_indicators = [
            r"[\$€£R]\s*[\d.,]+",  # Currency amounts
            r"\d+[\d,]*\s*(?:employees?|people)",  # Employee counts
            r"(?:19|20)\d{2}",  # Years
            r"\d+(?:\.\d+)?%",  # Percentages
            r"(?:billion|million|B|M|bn|mn)",  # Scale indicators
        ]

        data_points = 0
        for indicator in data_indicators:
            data_points += len(re.findall(indicator, content, re.IGNORECASE))

        # Bonus for actual data
        score += min(20, data_points * 5)

        # Penalty for very short bullet points
        bullets = re.findall(r"^[-•*]\s*.{1,20}$", content, re.MULTILINE)
        if len(bullets) > 3:
            score -= len(bullets) * 2

        return max(0, min(100, score))

    def _check_specific_issues(
        self,
        content: str,
        sections: Dict[str, str]
    ) -> Dict[str, List]:
        """Check for specific quality issues."""
        issues = {
            "blocks": [],
            "warnings": [],
            "improvements": []
        }

        content_lower = content.lower()

        # Check for critical empty indicators
        critical_empty_patterns = [
            r"no\s*research\s*sources?\s*(?:provided|found|available)",
            r"research\s*(?:not\s*)?unavailable",
            r"no\s*(?:data|information)\s*(?:was\s*)?found\s*for",
        ]

        for pattern in critical_empty_patterns:
            if re.search(pattern, content_lower):
                issues["blocks"].append(BlockReason.CRITICAL_GAPS)
                issues["warnings"].append("Critical: Research data appears to be missing entirely")
                break

        # Check company overview
        overview = sections.get("company_overview", "")
        if overview:
            # Check if overview is mostly "not available"
            not_available_ratio = len(re.findall(r"not\s*available", overview.lower())) / max(1, len(overview.split()))
            if not_available_ratio > 0.1:
                issues["blocks"].append(BlockReason.NO_COMPANY_INFO)
                issues["improvements"].append("Retry search with multilingual queries for company overview")

        # Check key metrics
        metrics = sections.get("key_metrics", "")
        if metrics:
            # Count actual metrics vs "not available"
            metric_lines = [l for l in metrics.split("\n") if l.strip().startswith("-")]
            empty_metrics = sum(1 for l in metric_lines if re.search(r"not\s*available|N/?A|unknown", l.lower()))

            if metric_lines and empty_metrics / len(metric_lines) > 0.7:
                issues["blocks"].append(BlockReason.NO_FINANCIAL_DATA)
                issues["improvements"].append("Search for financial data using stock ticker or annual reports")

        # Check for low-effort content
        word_count = len(content.split())
        if word_count < 200:
            issues["warnings"].append(f"Report appears too short ({word_count} words)")
            issues["improvements"].append("Expand search to gather more comprehensive data")

        # Suggest improvements based on missing data
        if not re.search(r"revenue|ingresos|receita", content_lower):
            issues["improvements"].append("Search for annual revenue/financial reports")

        if not re.search(r"competitors?|competidores", content_lower):
            issues["improvements"].append("Search for competitive analysis/industry comparison")

        if not re.search(r"products?|services?|productos|servicios", content_lower):
            issues["improvements"].append("Search for product/service offerings")

        return issues

    def _generate_summary(
        self,
        company_name: str,
        status: ReportStatus,
        overall_score: float,
        block_reasons: List[BlockReason],
        warnings: List[str]
    ) -> str:
        """Generate quality gate summary."""
        if status == ReportStatus.BLOCKED:
            emoji = "🚫"
            status_text = "BLOCKED"
        elif status == ReportStatus.WARNING:
            emoji = "⚠️"
            status_text = "WARNING"
        else:
            emoji = "✅"
            status_text = "APPROVED"

        lines = [
            f"{emoji} Quality Gate: {status_text}",
            f"Company: {company_name}",
            f"Quality Score: {overall_score:.1f}/100",
        ]

        if block_reasons:
            lines.append(f"Block Reasons: {', '.join(r.value for r in block_reasons)}")

        if warnings:
            lines.append(f"Warnings: {len(warnings)}")

        return "\n".join(lines)

    def generate_blocked_report(
        self,
        company_name: str,
        result: QualityGateResult
    ) -> str:
        """Generate a placeholder report when blocked."""
        return f"""# {company_name} - Research Report

**Status:** Report Generation Blocked

**Quality Score:** {result.quality_score:.1f}/100

## Reason for Blocking

The research data gathered for {company_name} does not meet minimum quality standards
for generating a reliable report.

### Issues Found:
{chr(10).join(f'- {w}' for w in result.warnings)}

### Suggested Actions:
{chr(10).join(f'- {i}' for i in result.improvements)}

### Recommendations:

1. **Retry with different queries**: The company may be better known by a different name
   or in a different language.

2. **Check parent company**: If this is a subsidiary, search for the parent company instead.

3. **Verify company name**: Ensure the company name is spelled correctly and is the
   official registered name.

4. **Try regional sources**: For Latin American companies, search in Spanish or Portuguese.

---

*This placeholder report was generated because the research quality threshold was not met.*
*Please retry the research with the suggested improvements.*
"""


def create_quality_enforcer(
    min_score: float = 30.0,
    block_on_empty: bool = True,
    strict: bool = False
) -> QualityEnforcer:
    """Factory function to create QualityEnforcer."""
    return QualityEnforcer(
        min_overall_score=min_score,
        block_on_empty_required=block_on_empty,
        strict_mode=strict
    )
