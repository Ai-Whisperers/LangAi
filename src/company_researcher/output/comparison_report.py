"""
Comparison Report Generator (OUT-003).

Generate side-by-side company comparison reports:
- Financial metrics comparison
- Market position analysis
- SWOT comparison matrix
- Competitive positioning
- Trend analysis across companies

Output formats:
- Markdown (default)
- HTML with charts
- JSON for API responses
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from ..utils import get_logger, utc_now

logger = get_logger(__name__)


class ComparisonMetric(str, Enum):
    """Metrics for company comparison."""

    REVENUE = "revenue"
    REVENUE_GROWTH = "revenue_growth"
    MARKET_CAP = "market_cap"
    EMPLOYEES = "employees"
    MARKET_SHARE = "market_share"
    FUNDING_TOTAL = "funding_total"
    FOUNDING_YEAR = "founding_year"
    PROFIT_MARGIN = "profit_margin"
    DEBT_RATIO = "debt_ratio"


class ComparisonCategory(str, Enum):
    """Categories for comparison."""

    FINANCIAL = "financial"
    MARKET = "market"
    OPERATIONS = "operations"
    GROWTH = "growth"
    RISK = "risk"


@dataclass
class CompanyData:
    """Structured data for a company in comparison."""

    name: str
    ticker: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    threats: List[str] = field(default_factory=list)
    key_products: List[str] = field(default_factory=list)
    recent_news: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricComparison:
    """Comparison result for a single metric."""

    metric_name: str
    category: ComparisonCategory
    values: Dict[str, Any]  # company_name -> value
    best_performer: Optional[str] = None
    worst_performer: Optional[str] = None
    average: Optional[float] = None
    notes: str = ""


@dataclass
class ComparisonReport:
    """Complete comparison report."""

    title: str
    companies: List[str]
    generated_at: datetime
    metric_comparisons: List[MetricComparison]
    swot_matrix: Dict[str, Dict[str, List[str]]]  # company -> {strengths, weaknesses, etc.}
    winner_summary: Dict[str, str]  # category -> winner
    key_insights: List[str]
    recommendations: List[str]
    raw_data: Dict[str, CompanyData] = field(default_factory=dict)


class ComparisonReportGenerator:
    """
    Generate comparison reports for multiple companies.

    Usage:
        generator = ComparisonReportGenerator()

        # Add company data
        generator.add_company("Apple", apple_research_data)
        generator.add_company("Microsoft", msft_research_data)

        # Generate report
        report = generator.generate_report()

        # Export
        markdown = generator.to_markdown(report)
        html = generator.to_html(report)
    """

    # Metric definitions with comparison logic
    METRIC_CONFIGS = {
        ComparisonMetric.REVENUE: {
            "name": "Revenue",
            "category": ComparisonCategory.FINANCIAL,
            "higher_is_better": True,
            "format": "${:,.0f}",
            "extract_path": ["financial", "revenue"],
        },
        ComparisonMetric.REVENUE_GROWTH: {
            "name": "Revenue Growth",
            "category": ComparisonCategory.GROWTH,
            "higher_is_better": True,
            "format": "{:.1f}%",
            "extract_path": ["financial", "revenue_growth"],
        },
        ComparisonMetric.MARKET_CAP: {
            "name": "Market Cap",
            "category": ComparisonCategory.MARKET,
            "higher_is_better": True,
            "format": "${:,.0f}",
            "extract_path": ["financial", "market_cap"],
        },
        ComparisonMetric.EMPLOYEES: {
            "name": "Employees",
            "category": ComparisonCategory.OPERATIONS,
            "higher_is_better": None,  # Neutral
            "format": "{:,}",
            "extract_path": ["overview", "employees"],
        },
        ComparisonMetric.MARKET_SHARE: {
            "name": "Market Share",
            "category": ComparisonCategory.MARKET,
            "higher_is_better": True,
            "format": "{:.1f}%",
            "extract_path": ["market", "market_share"],
        },
    }

    def __init__(self):
        self._companies: Dict[str, CompanyData] = {}

    def add_company(self, name: str, research_data: Dict[str, Any]) -> None:
        """
        Add company research data for comparison.

        Args:
            name: Company name
            research_data: Research output from company researcher
        """
        company = self._extract_company_data(name, research_data)
        self._companies[name] = company
        logger.info(f"Added company for comparison: {name}")

    def _extract_company_data(self, name: str, data: Dict[str, Any]) -> CompanyData:
        """Extract structured data from research output."""
        company = CompanyData(name=name, raw_data=data)

        # Extract metrics from various paths
        agent_outputs = data.get("agent_outputs", {})

        # Financial metrics
        financial = agent_outputs.get("financial", {})
        if isinstance(financial, dict):
            company.metrics["revenue"] = self._safe_get(financial, "revenue")
            company.metrics["revenue_growth"] = self._safe_get(financial, "revenue_growth")
            company.metrics["market_cap"] = self._safe_get(financial, "market_cap")
            company.metrics["profit_margin"] = self._safe_get(financial, "profit_margin")

        # Market metrics
        market = agent_outputs.get("market", {})
        if isinstance(market, dict):
            company.metrics["market_share"] = self._safe_get(market, "market_share")
            competitors = self._safe_get(market, "competitors", [])
            if competitors:
                company.metrics["competitor_count"] = len(competitors)

        # Overview metrics
        overview = agent_outputs.get("analyst", {})
        if isinstance(overview, dict):
            company.metrics["employees"] = self._safe_get(overview, "employees")
            company.metrics["founded"] = self._safe_get(overview, "founded")

        # SWOT analysis
        company.strengths = self._extract_list(data, "strengths")
        company.weaknesses = self._extract_list(data, "weaknesses")
        company.opportunities = self._extract_list(data, "opportunities")
        company.threats = self._extract_list(data, "threats")

        # Products
        product = agent_outputs.get("product", {})
        if isinstance(product, dict):
            company.key_products = self._extract_list(product, "products", max_items=5)

        return company

    def _safe_get(self, data: Dict, key: str, default: Any = None) -> Any:
        """Safely get value from dict."""
        if not isinstance(data, dict):
            return default
        return data.get(key, default)

    def _extract_list(self, data: Dict, key: str, max_items: int = 10) -> List[str]:
        """Extract list from nested data."""
        result = []
        if isinstance(data, dict):
            value = data.get(key, [])
            if isinstance(value, list):
                result = [str(v) for v in value[:max_items]]
        return result

    def generate_report(self, title: Optional[str] = None) -> ComparisonReport:
        """
        Generate comparison report for all added companies.

        Args:
            title: Optional report title

        Returns:
            ComparisonReport with full analysis
        """
        if len(self._companies) < 2:
            raise ValueError("Need at least 2 companies for comparison")

        company_names = list(self._companies.keys())

        if not title:
            title = f"Company Comparison: {' vs '.join(company_names)}"

        # Generate metric comparisons
        metric_comparisons = self._compare_metrics()

        # Build SWOT matrix
        swot_matrix = self._build_swot_matrix()

        # Determine winners by category
        winner_summary = self._determine_winners(metric_comparisons)

        # Generate insights
        key_insights = self._generate_insights(metric_comparisons, swot_matrix)

        # Generate recommendations
        recommendations = self._generate_recommendations(metric_comparisons)

        return ComparisonReport(
            title=title,
            companies=company_names,
            generated_at=utc_now(),
            metric_comparisons=metric_comparisons,
            swot_matrix=swot_matrix,
            winner_summary=winner_summary,
            key_insights=key_insights,
            recommendations=recommendations,
            raw_data=self._companies.copy(),
        )

    def _compare_metrics(self) -> List[MetricComparison]:
        """Compare all metrics across companies."""
        comparisons = []

        for metric, config in self.METRIC_CONFIGS.items():
            values = {}
            for name, company in self._companies.items():
                value = company.metrics.get(metric.value)
                if value is not None:
                    values[name] = value

            if not values:
                continue

            # Determine best/worst
            best = worst = None
            if config["higher_is_better"] is not None:
                numeric_values = {k: v for k, v in values.items() if isinstance(v, (int, float))}
                if numeric_values:
                    if config["higher_is_better"]:
                        best = max(numeric_values, key=numeric_values.get)
                        worst = min(numeric_values, key=numeric_values.get)
                    else:
                        best = min(numeric_values, key=numeric_values.get)
                        worst = max(numeric_values, key=numeric_values.get)

            # Calculate average
            numeric_vals = [v for v in values.values() if isinstance(v, (int, float))]
            average = sum(numeric_vals) / len(numeric_vals) if numeric_vals else None

            comparisons.append(
                MetricComparison(
                    metric_name=config["name"],
                    category=config["category"],
                    values=values,
                    best_performer=best,
                    worst_performer=worst,
                    average=average,
                )
            )

        return comparisons

    def _build_swot_matrix(self) -> Dict[str, Dict[str, List[str]]]:
        """Build SWOT matrix for all companies."""
        matrix = {}
        for name, company in self._companies.items():
            matrix[name] = {
                "strengths": company.strengths[:5],
                "weaknesses": company.weaknesses[:5],
                "opportunities": company.opportunities[:5],
                "threats": company.threats[:5],
            }
        return matrix

    def _determine_winners(self, comparisons: List[MetricComparison]) -> Dict[str, str]:
        """Determine winner for each category."""
        category_scores: Dict[str, Dict[str, int]] = {}

        for comp in comparisons:
            cat = comp.category.value
            if cat not in category_scores:
                category_scores[cat] = {name: 0 for name in self._companies}

            if comp.best_performer:
                category_scores[cat][comp.best_performer] += 1

        winners = {}
        for cat, scores in category_scores.items():
            if scores:
                winners[cat] = max(scores, key=scores.get)

        return winners

    def _generate_insights(
        self, comparisons: List[MetricComparison], swot: Dict[str, Dict[str, List[str]]]
    ) -> List[str]:
        """Generate key insights from comparison."""
        insights = []

        # Find overall leader
        company_wins = {name: 0 for name in self._companies}
        for comp in comparisons:
            if comp.best_performer:
                company_wins[comp.best_performer] += 1

        if company_wins:
            leader = max(company_wins, key=company_wins.get)
            insights.append(
                f"{leader} leads in {company_wins[leader]} out of {len(comparisons)} metrics compared."
            )

        # Note significant gaps
        for comp in comparisons:
            if comp.average and comp.best_performer and comp.worst_performer:
                best_val = comp.values.get(comp.best_performer, 0)
                worst_val = comp.values.get(comp.worst_performer, 0)
                if isinstance(best_val, (int, float)) and isinstance(worst_val, (int, float)):
                    if worst_val > 0:
                        gap = (best_val - worst_val) / worst_val * 100
                        if gap > 50:
                            insights.append(
                                f"Significant {comp.metric_name} gap: {comp.best_performer} "
                                f"leads {comp.worst_performer} by {gap:.0f}%"
                            )

        return insights[:10]  # Limit to 10 insights

    def _generate_recommendations(self, comparisons: List[MetricComparison]) -> List[str]:
        """Generate recommendations based on comparison."""
        recommendations = []

        for comp in comparisons:
            if comp.worst_performer and comp.best_performer:
                recommendations.append(
                    f"Consider {comp.best_performer}'s approach to {comp.metric_name.lower()} - "
                    f"they outperform {comp.worst_performer}"
                )

        return recommendations[:5]

    def to_markdown(self, report: ComparisonReport) -> str:
        """
        Export report to Markdown format.

        Args:
            report: ComparisonReport to export

        Returns:
            Markdown string
        """
        lines = [
            f"# {report.title}",
            f"",
            f"*Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}*",
            f"",
            f"## Companies Compared",
            f"",
        ]

        for company in report.companies:
            lines.append(f"- {company}")

        lines.extend(
            [
                "",
                "## Metric Comparison",
                "",
                "| Metric | " + " | ".join(report.companies) + " | Leader |",
                "|--------|" + "|".join(["--------"] * len(report.companies)) + "|--------|",
            ]
        )

        for comp in report.metric_comparisons:
            row = f"| {comp.metric_name} |"
            for company in report.companies:
                val = comp.values.get(company, "N/A")
                if isinstance(val, (int, float)):
                    val = f"{val:,.2f}" if isinstance(val, float) else f"{val:,}"
                row += f" {val} |"
            row += f" {comp.best_performer or 'N/A'} |"
            lines.append(row)

        # SWOT Matrix
        lines.extend(
            [
                "",
                "## SWOT Analysis",
                "",
            ]
        )

        for company, swot in report.swot_matrix.items():
            lines.extend(
                [
                    f"### {company}",
                    "",
                    "**Strengths:**",
                ]
            )
            for s in swot.get("strengths", []):
                lines.append(f"- {s}")

            lines.append("")
            lines.append("**Weaknesses:**")
            for w in swot.get("weaknesses", []):
                lines.append(f"- {w}")

            lines.append("")

        # Key Insights
        lines.extend(
            [
                "## Key Insights",
                "",
            ]
        )
        for insight in report.key_insights:
            lines.append(f"- {insight}")

        # Recommendations
        lines.extend(
            [
                "",
                "## Recommendations",
                "",
            ]
        )
        for rec in report.recommendations:
            lines.append(f"- {rec}")

        return "\n".join(lines)

    def to_json(self, report: ComparisonReport) -> str:
        """Export report to JSON format."""
        data = {
            "title": report.title,
            "companies": report.companies,
            "generated_at": report.generated_at.isoformat(),
            "metrics": [
                {
                    "name": m.metric_name,
                    "category": m.category.value,
                    "values": m.values,
                    "best_performer": m.best_performer,
                    "worst_performer": m.worst_performer,
                    "average": m.average,
                }
                for m in report.metric_comparisons
            ],
            "swot_matrix": report.swot_matrix,
            "winners": report.winner_summary,
            "insights": report.key_insights,
            "recommendations": report.recommendations,
        }
        return json.dumps(data, indent=2)

    def to_html(self, report: ComparisonReport) -> str:
        """Export report to HTML format with basic styling."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{report.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .winner {{ color: #4CAF50; font-weight: bold; }}
        .insight {{ background-color: #e7f3ff; padding: 10px; margin: 5px 0; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>{report.title}</h1>
    <p><em>Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}</em></p>

    <h2>Metric Comparison</h2>
    <table>
        <tr>
            <th>Metric</th>
            {"".join(f'<th>{c}</th>' for c in report.companies)}
            <th>Leader</th>
        </tr>
"""
        for comp in report.metric_comparisons:
            html += "        <tr>\n"
            html += f"            <td>{comp.metric_name}</td>\n"
            for company in report.companies:
                val = comp.values.get(company, "N/A")
                if isinstance(val, (int, float)):
                    val = f"{val:,.2f}" if isinstance(val, float) else f"{val:,}"
                css = ' class="winner"' if company == comp.best_performer else ""
                html += f"            <td{css}>{val}</td>\n"
            html += f'            <td class="winner">{comp.best_performer or "N/A"}</td>\n'
            html += "        </tr>\n"

        html += """    </table>

    <h2>Key Insights</h2>
"""
        for insight in report.key_insights:
            html += f'    <div class="insight">{insight}</div>\n'

        html += """
</body>
</html>"""
        return html


def create_comparison_generator() -> ComparisonReportGenerator:
    """Create a new comparison report generator."""
    return ComparisonReportGenerator()


async def compare_companies(
    company_data: Dict[str, Dict[str, Any]], output_format: str = "markdown"
) -> str:
    """
    Quick comparison of multiple companies.

    Args:
        company_data: Dict of company_name -> research_data
        output_format: "markdown", "json", or "html"

    Returns:
        Formatted comparison report
    """
    generator = ComparisonReportGenerator()

    for name, data in company_data.items():
        generator.add_company(name, data)

    report = generator.generate_report()

    if output_format == "json":
        return generator.to_json(report)
    elif output_format == "html":
        return generator.to_html(report)
    else:
        return generator.to_markdown(report)
