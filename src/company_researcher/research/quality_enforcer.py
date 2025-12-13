"""
Report Quality Enforcer Module

Ensures consistent quality across all generated reports:
- Minimum coverage thresholds
- Required section validation
- Data completeness checks
- Format consistency verification
- Publishability determination

This module addresses the issue of "inconsistent report quality"
by enforcing standards before report finalization.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import re
from datetime import datetime
from ..utils import utc_now


class QualityLevel(Enum):
    """Quality level classifications."""
    EXCELLENT = "excellent"  # Score 90-100
    GOOD = "good"  # Score 75-89
    ACCEPTABLE = "acceptable"  # Score 60-74
    POOR = "poor"  # Score 40-59
    UNACCEPTABLE = "unacceptable"  # Score 0-39


class SectionType(Enum):
    """Types of report sections."""
    EXECUTIVE_SUMMARY = "executive_summary"
    COMPANY_OVERVIEW = "company_overview"
    FINANCIAL_ANALYSIS = "financial_analysis"
    MARKET_POSITION = "market_position"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    STRATEGY_OUTLOOK = "strategy_outlook"
    RISK_ASSESSMENT = "risk_assessment"
    INVESTMENT_THESIS = "investment_thesis"
    SOURCES = "sources"


class IssueType(Enum):
    """Types of quality issues."""
    MISSING_DATA = "missing_data"
    VAGUE_STATEMENT = "vague_statement"
    MISSING_SECTION = "missing_section"
    INCOMPLETE_SECTION = "incomplete_section"
    FORMAT_ERROR = "format_error"
    OUTDATED_DATA = "outdated_data"
    INCONSISTENCY = "inconsistency"
    MISSING_SOURCE = "missing_source"


class IssueSeverity(Enum):
    """Severity of quality issues."""
    CRITICAL = "critical"  # Blocks publication
    MAJOR = "major"  # Should be fixed
    MINOR = "minor"  # Nice to fix
    INFO = "info"  # Informational


@dataclass
class QualityIssue:
    """A single quality issue found in a report."""
    issue_type: IssueType
    severity: IssueSeverity
    section: Optional[SectionType]
    description: str
    location: str = ""  # Line number or section name
    suggestion: str = ""  # How to fix


@dataclass
class SectionAnalysis:
    """Analysis of a single report section."""
    section_type: SectionType
    present: bool = False
    word_count: int = 0
    data_points: int = 0  # Number of specific facts/figures
    has_metrics: bool = False  # Contains numerical data
    has_sources: bool = False  # References sources
    completeness: float = 0.0  # 0-100%
    issues: List[QualityIssue] = field(default_factory=list)


@dataclass
class QualityReport:
    """Complete quality assessment report."""
    overall_score: float = 0.0
    quality_level: QualityLevel = QualityLevel.POOR
    publishable: bool = False
    section_analyses: Dict[SectionType, SectionAnalysis] = field(default_factory=dict)
    issues: List[QualityIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metrics_coverage: float = 0.0
    source_coverage: float = 0.0
    assessment_date: datetime = field(default_factory=utc_now)


class ReportQualityEnforcer:
    """
    Enforces quality standards for research reports.

    Validates completeness, consistency, and accuracy
    before allowing report publication.
    """

    # Required sections and their minimum requirements
    SECTION_REQUIREMENTS: Dict[SectionType, Dict[str, Any]] = {
        SectionType.EXECUTIVE_SUMMARY: {
            "required": True,
            "min_words": 100,
            "min_data_points": 3,
            "keywords": ["summary", "overview", "key findings"],
        },
        SectionType.COMPANY_OVERVIEW: {
            "required": True,
            "min_words": 150,
            "min_data_points": 5,
            "required_fields": ["founded", "headquarters", "employees", "industry"],
        },
        SectionType.FINANCIAL_ANALYSIS: {
            "required": True,
            "min_words": 200,
            "min_data_points": 8,
            "required_fields": ["revenue", "net_income", "growth"],
        },
        SectionType.MARKET_POSITION: {
            "required": True,
            "min_words": 100,
            "min_data_points": 3,
            "required_fields": ["market_cap"],
        },
        SectionType.COMPETITIVE_ANALYSIS: {
            "required": True,
            "min_words": 100,
            "min_data_points": 2,
            "keywords": ["competitor", "market share", "competitive"],
        },
        SectionType.STRATEGY_OUTLOOK: {
            "required": True,
            "min_words": 100,
            "min_data_points": 2,
            "keywords": ["strategy", "outlook", "growth", "initiative"],
        },
        SectionType.RISK_ASSESSMENT: {
            "required": True,
            "min_words": 80,
            "min_data_points": 3,
            "keywords": ["risk", "concern", "challenge"],
        },
        SectionType.INVESTMENT_THESIS: {
            "required": False,  # Only for investment reports
            "min_words": 150,
            "min_data_points": 4,
            "keywords": ["thesis", "rating", "recommendation", "target"],
        },
        SectionType.SOURCES: {
            "required": True,
            "min_words": 0,
            "min_data_points": 5,  # Minimum sources
            "keywords": ["source", "reference"],
        },
    }

    # Patterns indicating vague or incomplete content
    VAGUE_PATTERNS = [
        r'data\s+not\s+available',
        r'n/?a\b',
        r'not\s+(?:yet\s+)?available',
        r'information\s+not\s+(?:yet\s+)?(?:available|disclosed)',
        r'to\s+be\s+(?:determined|announced)',
        r'no\s+data\s+(?:found|available)',
        r'could\s+not\s+(?:be\s+)?(?:determined|found|verified)',
        r'(?:exact|specific)\s+(?:figure|number|data)\s+not',
        r'—',  # Placeholder dash
    ]

    # Patterns indicating good content (with specific data)
    SPECIFIC_DATA_PATTERNS = [
        r'\$[\d,]+(?:\.\d+)?(?:\s*(?:billion|million|trillion|B|M|T))?',  # Currency
        r'\d+(?:\.\d+)?%',  # Percentages
        r'(?:FY|Q[1-4])\s*20\d{2}',  # Fiscal periods
        r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
        r'\d{1,3}(?:,\d{3})+\s*(?:employees|stores|locations)',  # Counts
        r'(?:CEO|CFO|CTO|COO):\s*\w+\s+\w+',  # Named executives
    ]

    # Section header patterns
    SECTION_PATTERNS: Dict[SectionType, List[str]] = {
        SectionType.EXECUTIVE_SUMMARY: [
            r'#+\s*executive\s+summary',
            r'#+\s*summary',
            r'#+\s*overview',
        ],
        SectionType.COMPANY_OVERVIEW: [
            r'#+\s*company\s+overview',
            r'#+\s*about\s+(?:the\s+)?company',
            r'#+\s*(?:\d+[\.\)]\s*)?company\s+(?:overview|profile|background)',
        ],
        SectionType.FINANCIAL_ANALYSIS: [
            r'#+\s*financial\s+(?:analysis|performance|results)',
            r'#+\s*financials',
            r'#+\s*(?:\d+[\.\)]\s*)?financial\s+(?:analysis|performance)',
        ],
        SectionType.MARKET_POSITION: [
            r'#+\s*market\s+position',
            r'#+\s*(?:\d+[\.\)]\s*)?market\s+(?:position|capitalization)',
            r'#+\s*valuation',
        ],
        SectionType.COMPETITIVE_ANALYSIS: [
            r'#+\s*competi(?:tive|tion)\s*(?:analysis|landscape)?',
            r'#+\s*(?:\d+[\.\)]\s*)?competi(?:tive|tion)',
        ],
        SectionType.STRATEGY_OUTLOOK: [
            r'#+\s*strategy',
            r'#+\s*(?:growth\s+)?outlook',
            r'#+\s*strategic\s+initiatives',
        ],
        SectionType.RISK_ASSESSMENT: [
            r'#+\s*risks?\s*(?:assessment|factors|analysis)?',
            r'#+\s*(?:\d+[\.\)]\s*)?risks?\s*(?:&|and)?\s*concerns?',
        ],
        SectionType.INVESTMENT_THESIS: [
            r'#+\s*investment\s+thesis',
            r'#+\s*(?:\d+[\.\)]\s*)?investment\s+(?:thesis|recommendation)',
            r'#+\s*conclusion\s*(?:with\s+)?rating',
        ],
        SectionType.SOURCES: [
            r'#+\s*sources?',
            r'#+\s*references?',
            r'\*\*sources?\*\*',
        ],
    }

    # Minimum thresholds for publishability
    PUBLISHABILITY_THRESHOLDS = {
        "min_overall_score": 55,  # Minimum score to publish
        "max_critical_issues": 0,  # No critical issues allowed
        "max_major_issues": 3,  # Maximum major issues
        "min_sections_present": 6,  # Minimum required sections
        "min_metrics_coverage": 40,  # Minimum % of key metrics present
        "min_source_count": 3,  # Minimum sources required
    }

    def __init__(self, strict_mode: bool = False):
        """
        Initialize the enforcer.

        Args:
            strict_mode: If True, applies stricter quality requirements
        """
        self.strict_mode = strict_mode
        if strict_mode:
            self.PUBLISHABILITY_THRESHOLDS["min_overall_score"] = 70
            self.PUBLISHABILITY_THRESHOLDS["max_major_issues"] = 1
            self.PUBLISHABILITY_THRESHOLDS["min_metrics_coverage"] = 60

    def analyze_report(self, content: str) -> QualityReport:
        """
        Analyze a report's quality.

        Args:
            content: Full report content as markdown

        Returns:
            QualityReport with complete analysis
        """
        report = QualityReport()

        # Analyze each section
        for section_type in SectionType:
            analysis = self._analyze_section(content, section_type)
            report.section_analyses[section_type] = analysis
            report.issues.extend(analysis.issues)

        # Check for global issues
        global_issues = self._check_global_issues(content, report.section_analyses)
        report.issues.extend(global_issues)

        # Calculate metrics coverage
        report.metrics_coverage = self._calculate_metrics_coverage(content)

        # Calculate source coverage
        report.source_coverage = self._calculate_source_coverage(content)

        # Calculate overall score
        report.overall_score = self._calculate_overall_score(report)

        # Determine quality level
        report.quality_level = self._determine_quality_level(report.overall_score)

        # Determine publishability
        report.publishable = self._check_publishability(report)

        # Generate recommendations
        report.recommendations = self._generate_recommendations(report)

        return report

    def _analyze_section(
        self,
        content: str,
        section_type: SectionType
    ) -> SectionAnalysis:
        """Analyze a specific section of the report."""
        analysis = SectionAnalysis(section_type=section_type)
        requirements = self.SECTION_REQUIREMENTS.get(section_type, {})

        # Find section
        section_text = self._extract_section(content, section_type)

        if not section_text:
            analysis.present = False
            if requirements.get("required", False):
                analysis.issues.append(QualityIssue(
                    issue_type=IssueType.MISSING_SECTION,
                    severity=IssueSeverity.CRITICAL if section_type in [
                        SectionType.FINANCIAL_ANALYSIS,
                        SectionType.COMPANY_OVERVIEW
                    ] else IssueSeverity.MAJOR,
                    section=section_type,
                    description=f"Required section '{section_type.value}' is missing",
                    suggestion=f"Add a {section_type.value.replace('_', ' ')} section"
                ))
            return analysis

        analysis.present = True

        # Count words
        analysis.word_count = len(section_text.split())

        # Count data points (specific facts/figures)
        analysis.data_points = self._count_data_points(section_text)
        analysis.has_metrics = analysis.data_points > 0

        # Check for source references
        analysis.has_sources = bool(re.search(r'\[[^\]]+\]\([^\)]+\)|source:|from:', section_text, re.IGNORECASE))

        # Check minimum requirements
        min_words = requirements.get("min_words", 50)
        if analysis.word_count < min_words:
            analysis.issues.append(QualityIssue(
                issue_type=IssueType.INCOMPLETE_SECTION,
                severity=IssueSeverity.MAJOR,
                section=section_type,
                description=f"Section has {analysis.word_count} words, minimum is {min_words}",
                suggestion=f"Expand section with more detailed analysis"
            ))

        min_data = requirements.get("min_data_points", 0)
        if analysis.data_points < min_data:
            analysis.issues.append(QualityIssue(
                issue_type=IssueType.MISSING_DATA,
                severity=IssueSeverity.MAJOR if min_data > 3 else IssueSeverity.MINOR,
                section=section_type,
                description=f"Section has {analysis.data_points} data points, minimum is {min_data}",
                suggestion=f"Add specific metrics and figures"
            ))

        # Check for vague statements
        vague_count = self._count_vague_statements(section_text)
        if vague_count > 2:
            analysis.issues.append(QualityIssue(
                issue_type=IssueType.VAGUE_STATEMENT,
                severity=IssueSeverity.MAJOR,
                section=section_type,
                description=f"Section contains {vague_count} vague or 'data not available' statements",
                suggestion="Replace vague statements with specific data or research further"
            ))

        # Calculate completeness
        max_score = 100
        penalties = 0
        if analysis.word_count < min_words:
            penalties += 30 * (1 - analysis.word_count / min_words)
        if analysis.data_points < min_data:
            penalties += 30 * (1 - analysis.data_points / max(1, min_data))
        penalties += vague_count * 5

        analysis.completeness = max(0, max_score - penalties)

        return analysis

    def _extract_section(
        self,
        content: str,
        section_type: SectionType
    ) -> str:
        """Extract a section's text from the full content."""
        patterns = self.SECTION_PATTERNS.get(section_type, [])

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                start = match.end()

                # Find next section header
                next_header = re.search(r'\n#+\s', content[start:])
                if next_header:
                    end = start + next_header.start()
                else:
                    end = len(content)

                return content[start:end].strip()

        return ""

    def _count_data_points(self, text: str) -> int:
        """Count specific data points in text."""
        count = 0
        for pattern in self.SPECIFIC_DATA_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            count += len(matches)
        return count

    def _count_vague_statements(self, text: str) -> int:
        """Count vague or incomplete statements."""
        count = 0
        for pattern in self.VAGUE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            count += len(matches)
        return count

    def _check_global_issues(
        self,
        content: str,
        section_analyses: Dict[SectionType, SectionAnalysis]
    ) -> List[QualityIssue]:
        """Check for issues across the entire report."""
        issues = []

        # Check for inconsistent data
        revenue_mentions = re.findall(
            r'revenue\s+(?:of\s+)?\$?([\d,]+(?:\.\d+)?)\s*(billion|million|B|M)?',
            content, re.IGNORECASE
        )
        if len(set(revenue_mentions)) > 2:
            issues.append(QualityIssue(
                issue_type=IssueType.INCONSISTENCY,
                severity=IssueSeverity.MAJOR,
                section=None,
                description="Multiple different revenue figures mentioned",
                suggestion="Verify and use consistent revenue figures throughout"
            ))

        # Check for outdated data
        current_year = utc_now().year
        if f"20{current_year - 3}" in content or f"20{current_year - 4}" in content:
            issues.append(QualityIssue(
                issue_type=IssueType.OUTDATED_DATA,
                severity=IssueSeverity.MINOR,
                section=None,
                description="Report contains data from 3+ years ago without recent updates",
                suggestion="Update with more recent data where available"
            ))

        # Check for missing sources
        source_analysis = section_analyses.get(SectionType.SOURCES)
        if source_analysis and source_analysis.present:
            if source_analysis.data_points < 3:
                issues.append(QualityIssue(
                    issue_type=IssueType.MISSING_SOURCE,
                    severity=IssueSeverity.MAJOR,
                    section=SectionType.SOURCES,
                    description="Insufficient sources cited",
                    suggestion="Add more authoritative sources"
                ))

        return issues

    def _calculate_metrics_coverage(self, content: str) -> float:
        """Calculate percentage of key metrics present."""
        key_metrics = [
            "revenue", "net income", "eps", "market cap",
            "employees", "margin", "growth", "ebitda"
        ]

        found = sum(
            1 for metric in key_metrics
            if re.search(rf'{metric}.*\$?[\d,]+', content, re.IGNORECASE)
        )

        return (found / len(key_metrics)) * 100

    def _calculate_source_coverage(self, content: str) -> float:
        """Calculate source coverage score."""
        # Count linked sources
        sources = re.findall(r'\[[^\]]+\]\([^\)]+\)', content)
        source_count = len(sources)

        # Ideal is 10+ sources
        return min(100, source_count * 10)

    def _calculate_overall_score(self, report: QualityReport) -> float:
        """Calculate overall quality score."""
        score = 0

        # Section scores (60% of total)
        section_scores = []
        for analysis in report.section_analyses.values():
            if analysis.present:
                section_scores.append(analysis.completeness)

        if section_scores:
            score += (sum(section_scores) / len(section_scores)) * 0.6

        # Metrics coverage (20%)
        score += report.metrics_coverage * 0.2

        # Source coverage (10%)
        score += report.source_coverage * 0.1

        # Issue penalties (10%)
        critical_count = sum(1 for i in report.issues if i.severity == IssueSeverity.CRITICAL)
        major_count = sum(1 for i in report.issues if i.severity == IssueSeverity.MAJOR)

        issue_penalty = critical_count * 5 + major_count * 2
        score += max(0, 10 - issue_penalty)

        return min(100, max(0, score))

    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level from score."""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 75:
            return QualityLevel.GOOD
        elif score >= 60:
            return QualityLevel.ACCEPTABLE
        elif score >= 40:
            return QualityLevel.POOR
        else:
            return QualityLevel.UNACCEPTABLE

    def _check_publishability(self, report: QualityReport) -> bool:
        """Check if report meets publishability thresholds."""
        thresholds = self.PUBLISHABILITY_THRESHOLDS

        # Check overall score
        if report.overall_score < thresholds["min_overall_score"]:
            return False

        # Check critical issues
        critical_count = sum(1 for i in report.issues if i.severity == IssueSeverity.CRITICAL)
        if critical_count > thresholds["max_critical_issues"]:
            return False

        # Check major issues
        major_count = sum(1 for i in report.issues if i.severity == IssueSeverity.MAJOR)
        if major_count > thresholds["max_major_issues"]:
            return False

        # Check section presence
        present_sections = sum(1 for a in report.section_analyses.values() if a.present)
        if present_sections < thresholds["min_sections_present"]:
            return False

        # Check metrics coverage
        if report.metrics_coverage < thresholds["min_metrics_coverage"]:
            return False

        return True

    def _generate_recommendations(self, report: QualityReport) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Critical issues first
        for issue in report.issues:
            if issue.severity == IssueSeverity.CRITICAL:
                recommendations.append(f"🔴 CRITICAL: {issue.suggestion}")

        # Missing sections
        missing_sections = [
            s for s, a in report.section_analyses.items()
            if not a.present and self.SECTION_REQUIREMENTS.get(s, {}).get("required", False)
        ]
        if missing_sections:
            section_names = [s.value.replace("_", " ").title() for s in missing_sections]
            recommendations.append(f"Add missing sections: {', '.join(section_names)}")

        # Low completeness sections
        for section_type, analysis in report.section_analyses.items():
            if analysis.present and analysis.completeness < 50:
                recommendations.append(
                    f"Expand {section_type.value.replace('_', ' ')} section (currently {analysis.completeness:.0f}% complete)"
                )

        # Metrics coverage
        if report.metrics_coverage < 50:
            recommendations.append(
                f"Add more specific metrics - currently only {report.metrics_coverage:.0f}% coverage"
            )

        # Source coverage
        if report.source_coverage < 50:
            recommendations.append(
                f"Add more sources - currently {int(report.source_coverage / 10)} sources cited"
            )

        return recommendations

    def generate_quality_report(self, report: QualityReport) -> str:
        """
        Generate a markdown quality report.

        Args:
            report: QualityReport to format

        Returns:
            Markdown formatted report
        """
        lines = ["### Quality Assessment Report", ""]

        # Overall status
        status_emoji = {
            QualityLevel.EXCELLENT: "🟢",
            QualityLevel.GOOD: "🟢",
            QualityLevel.ACCEPTABLE: "🟡",
            QualityLevel.POOR: "🟠",
            QualityLevel.UNACCEPTABLE: "🔴",
        }
        emoji = status_emoji.get(report.quality_level, "🟡")

        lines.append(f"**Overall Score:** {emoji} {report.overall_score:.1f}/100 ({report.quality_level.value.title()})")
        lines.append(f"**Publishable:** {'✅ Yes' if report.publishable else '❌ No'}")
        lines.append("")

        # Section breakdown
        lines.append("**Section Analysis:**")
        lines.append("")
        lines.append("| Section | Status | Words | Data Points | Score |")
        lines.append("| --- | --- | --- | --- | --- |")

        for section_type, analysis in report.section_analyses.items():
            status = "✓" if analysis.present else "✗"
            score = f"{analysis.completeness:.0f}%" if analysis.present else "—"
            lines.append(
                f"| {section_type.value.replace('_', ' ').title()} | {status} | "
                f"{analysis.word_count if analysis.present else '—'} | "
                f"{analysis.data_points if analysis.present else '—'} | {score} |"
            )
        lines.append("")

        # Coverage metrics
        lines.append("**Coverage Metrics:**")
        lines.append(f"- Metrics Coverage: {report.metrics_coverage:.1f}%")
        lines.append(f"- Source Coverage: {report.source_coverage:.1f}%")
        lines.append("")

        # Issues
        if report.issues:
            lines.append("**Issues Found:**")
            for issue in sorted(report.issues, key=lambda x: x.severity.value):
                severity_marker = {
                    IssueSeverity.CRITICAL: "🔴",
                    IssueSeverity.MAJOR: "🟠",
                    IssueSeverity.MINOR: "🟡",
                    IssueSeverity.INFO: "ℹ️",
                }
                marker = severity_marker.get(issue.severity, "•")
                lines.append(f"- {marker} {issue.description}")
            lines.append("")

        # Recommendations
        if report.recommendations:
            lines.append("**Recommendations:**")
            for rec in report.recommendations:
                lines.append(f"- {rec}")

        return "\n".join(lines)


def create_quality_enforcer(strict_mode: bool = False) -> ReportQualityEnforcer:
    """Factory function to create a ReportQualityEnforcer."""
    return ReportQualityEnforcer(strict_mode=strict_mode)
