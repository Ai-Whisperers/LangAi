"""
Comparative Analysis Agent

Performs side-by-side company comparisons:
- Financial benchmarking
- Market position analysis
- Competitive strengths/weaknesses
- SWOT analysis generation
- Scoring and ranking

Usage:
    from company_researcher.agents.market.comparative_analyst import (
        ComparativeAnalystAgent,
        comparative_analyst_node,
        create_comparative_analyst
    )

    analyst = create_comparative_analyst()
    comparison = await analyst.compare_companies(companies_data)
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import statistics
from ...utils import get_logger, utc_now

logger = get_logger(__name__)


class ComparisonCategory(Enum):
    """Categories for comparison."""
    FINANCIAL = "financial"
    MARKET = "market"
    PRODUCT = "product"
    TECHNOLOGY = "technology"
    TEAM = "team"
    OPERATIONS = "operations"
    GROWTH = "growth"
    RISK = "risk"


class MetricType(Enum):
    """Type of metric (higher is better or lower is better)."""
    HIGHER_BETTER = "higher_better"   # Revenue, market share
    LOWER_BETTER = "lower_better"     # Debt ratio, churn
    NEUTRAL = "neutral"               # Size metrics


@dataclass
class CompanyProfile:
    """Profile of a company for comparison."""
    name: str
    ticker: Optional[str] = None
    industry: Optional[str] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    qualitative: Dict[str, str] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricComparison:
    """Comparison of a single metric across companies."""
    metric_name: str
    category: ComparisonCategory
    metric_type: MetricType
    values: Dict[str, float]          # company -> value
    rankings: Dict[str, int]          # company -> rank
    percentiles: Dict[str, float]     # company -> percentile
    industry_average: Optional[float] = None
    best_performer: Optional[str] = None
    worst_performer: Optional[str] = None
    gap_analysis: Dict[str, float] = field(default_factory=dict)


@dataclass
class SWOT:
    """SWOT analysis for a company."""
    company: str
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    overall_score: float = 0.0


@dataclass
class CompetitivePosition:
    """Competitive positioning analysis."""
    company: str
    market_position: str              # Leader, Challenger, Follower, Niche
    competitive_advantages: List[str]
    competitive_disadvantages: List[str]
    strategic_fit: Dict[str, str]     # Category -> position
    overall_rank: int
    score: float


@dataclass
class ComparativeAnalysis:
    """Complete comparative analysis result."""
    target_company: str
    comparison_date: datetime
    companies_analyzed: List[str]
    metric_comparisons: List[MetricComparison]
    swot_analyses: Dict[str, SWOT]
    competitive_positions: Dict[str, CompetitivePosition]
    overall_rankings: List[Tuple[str, float]]  # (company, score)
    key_insights: List[str]
    recommendations: List[str]
    confidence: float


class ComparativeAnalystAgent:
    """
    Agent for comparative company analysis.

    Compares companies across multiple dimensions and
    generates actionable competitive intelligence.
    """

    # Standard metrics and their properties
    METRIC_DEFINITIONS = {
        # Financial
        "revenue": (ComparisonCategory.FINANCIAL, MetricType.HIGHER_BETTER, "Revenue ($B)"),
        "revenue_growth": (ComparisonCategory.FINANCIAL, MetricType.HIGHER_BETTER, "Revenue Growth (%)"),
        "gross_margin": (ComparisonCategory.FINANCIAL, MetricType.HIGHER_BETTER, "Gross Margin (%)"),
        "operating_margin": (ComparisonCategory.FINANCIAL, MetricType.HIGHER_BETTER, "Operating Margin (%)"),
        "net_margin": (ComparisonCategory.FINANCIAL, MetricType.HIGHER_BETTER, "Net Margin (%)"),
        "debt_to_equity": (ComparisonCategory.FINANCIAL, MetricType.LOWER_BETTER, "Debt/Equity Ratio"),
        "current_ratio": (ComparisonCategory.FINANCIAL, MetricType.HIGHER_BETTER, "Current Ratio"),

        # Market
        "market_cap": (ComparisonCategory.MARKET, MetricType.HIGHER_BETTER, "Market Cap ($B)"),
        "market_share": (ComparisonCategory.MARKET, MetricType.HIGHER_BETTER, "Market Share (%)"),
        "pe_ratio": (ComparisonCategory.MARKET, MetricType.NEUTRAL, "P/E Ratio"),
        "ev_revenue": (ComparisonCategory.MARKET, MetricType.NEUTRAL, "EV/Revenue"),

        # Growth
        "employee_growth": (ComparisonCategory.GROWTH, MetricType.HIGHER_BETTER, "Employee Growth (%)"),
        "customer_growth": (ComparisonCategory.GROWTH, MetricType.HIGHER_BETTER, "Customer Growth (%)"),
        "geographic_expansion": (ComparisonCategory.GROWTH, MetricType.HIGHER_BETTER, "Geographic Reach"),

        # Operations
        "employee_count": (ComparisonCategory.OPERATIONS, MetricType.NEUTRAL, "Employees"),
        "revenue_per_employee": (ComparisonCategory.OPERATIONS, MetricType.HIGHER_BETTER, "Revenue/Employee ($K)"),
        "operational_efficiency": (ComparisonCategory.OPERATIONS, MetricType.HIGHER_BETTER, "Op. Efficiency Score"),

        # Technology
        "r_and_d_spend": (ComparisonCategory.TECHNOLOGY, MetricType.HIGHER_BETTER, "R&D Spending ($M)"),
        "r_and_d_ratio": (ComparisonCategory.TECHNOLOGY, MetricType.HIGHER_BETTER, "R&D as % Revenue"),
        "patent_count": (ComparisonCategory.TECHNOLOGY, MetricType.HIGHER_BETTER, "Patents"),

        # Risk
        "customer_concentration": (ComparisonCategory.RISK, MetricType.LOWER_BETTER, "Customer Concentration (%)"),
        "regulatory_risk": (ComparisonCategory.RISK, MetricType.LOWER_BETTER, "Regulatory Risk Score"),
    }

    def __init__(
        self,
        target_company: str,
        industry: Optional[str] = None
    ):
        self.target_company = target_company
        self.industry = industry
        self.companies: Dict[str, CompanyProfile] = {}
        self.industry_benchmarks: Dict[str, float] = {}

    def add_company(
        self,
        name: str,
        metrics: Dict[str, float],
        qualitative: Optional[Dict[str, str]] = None,
        ticker: Optional[str] = None,
        **kwargs
    ):
        """Add a company to the comparison set."""
        profile = CompanyProfile(
            name=name,
            ticker=ticker,
            industry=self.industry,
            metrics=metrics,
            qualitative=qualitative or {},
            metadata=kwargs
        )
        self.companies[name] = profile
        logger.info(f"Added company: {name} with {len(metrics)} metrics")

    def add_industry_benchmark(self, metric: str, value: float):
        """Add industry benchmark for a metric."""
        self.industry_benchmarks[metric] = value

    def compare_companies(
        self,
        metrics_to_compare: Optional[List[str]] = None
    ) -> ComparativeAnalysis:
        """
        Perform comprehensive comparative analysis.

        Args:
            metrics_to_compare: Specific metrics to compare (None = all available)

        Returns:
            ComparativeAnalysis with complete comparison
        """
        if not self.companies:
            raise ValueError("No companies added for comparison")

        # Determine metrics to analyze
        if metrics_to_compare:
            metrics = metrics_to_compare
        else:
            metrics = self._get_common_metrics()

        # Compare each metric
        metric_comparisons = []
        for metric in metrics:
            comparison = self._compare_metric(metric)
            if comparison:
                metric_comparisons.append(comparison)

        # Generate SWOT for each company
        swot_analyses = {
            name: self._generate_swot(name, metric_comparisons)
            for name in self.companies
        }

        # Calculate competitive positions
        competitive_positions = {
            name: self._calculate_position(name, metric_comparisons, swot)
            for name, swot in swot_analyses.items()
        }

        # Generate overall rankings
        rankings = self._calculate_rankings(metric_comparisons)

        # Generate insights
        insights = self._generate_insights(metric_comparisons, rankings)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            metric_comparisons, swot_analyses, competitive_positions
        )

        # Calculate confidence
        confidence = self._calculate_confidence(metric_comparisons)

        return ComparativeAnalysis(
            target_company=self.target_company,
            comparison_date=utc_now(),
            companies_analyzed=list(self.companies.keys()),
            metric_comparisons=metric_comparisons,
            swot_analyses=swot_analyses,
            competitive_positions=competitive_positions,
            overall_rankings=rankings,
            key_insights=insights,
            recommendations=recommendations,
            confidence=confidence
        )

    def _get_common_metrics(self) -> Set[str]:
        """Get metrics that exist for all companies."""
        if not self.companies:
            return set()

        common = None
        for profile in self.companies.values():
            company_metrics = set(profile.metrics.keys())
            if common is None:
                common = company_metrics
            else:
                common = common & company_metrics

        return common or set()

    def _compare_metric(self, metric: str) -> Optional[MetricComparison]:
        """Compare a single metric across all companies."""
        values = {}
        for name, profile in self.companies.items():
            if metric in profile.metrics:
                values[name] = profile.metrics[metric]

        if len(values) < 2:
            return None

        # Get metric definition
        if metric in self.METRIC_DEFINITIONS:
            category, metric_type, _ = self.METRIC_DEFINITIONS[metric]
        else:
            category = ComparisonCategory.FINANCIAL
            metric_type = MetricType.HIGHER_BETTER

        # Calculate rankings
        sorted_items = sorted(
            values.items(),
            key=lambda x: x[1],
            reverse=(metric_type == MetricType.HIGHER_BETTER)
        )
        rankings = {name: rank + 1 for rank, (name, _) in enumerate(sorted_items)}

        # Calculate percentiles
        all_values = list(values.values())
        min_val, max_val = min(all_values), max(all_values)
        range_val = max_val - min_val if max_val != min_val else 1

        percentiles = {}
        for name, value in values.items():
            if metric_type == MetricType.HIGHER_BETTER:
                percentiles[name] = (value - min_val) / range_val
            elif metric_type == MetricType.LOWER_BETTER:
                percentiles[name] = (max_val - value) / range_val
            else:
                percentiles[name] = 0.5

        # Gap analysis vs target company
        gap_analysis = {}
        if self.target_company in values:
            target_value = values[self.target_company]
            for name, value in values.items():
                if name != self.target_company:
                    if target_value != 0:
                        gap_analysis[name] = ((value - target_value) / abs(target_value)) * 100
                    else:
                        gap_analysis[name] = 100 if value > 0 else 0

        # Identify best/worst
        best = sorted_items[0][0] if metric_type == MetricType.HIGHER_BETTER else sorted_items[-1][0]
        worst = sorted_items[-1][0] if metric_type == MetricType.HIGHER_BETTER else sorted_items[0][0]

        return MetricComparison(
            metric_name=metric,
            category=category,
            metric_type=metric_type,
            values=values,
            rankings=rankings,
            percentiles=percentiles,
            industry_average=self.industry_benchmarks.get(metric),
            best_performer=best,
            worst_performer=worst,
            gap_analysis=gap_analysis
        )

    def _generate_swot(
        self,
        company_name: str,
        comparisons: List[MetricComparison]
    ) -> SWOT:
        """Generate SWOT analysis for a company."""
        strengths = []
        weaknesses = []
        opportunities = []
        threats = []

        profile = self.companies[company_name]

        for comparison in comparisons:
            if company_name not in comparison.values:
                continue

            rank = comparison.rankings.get(company_name, 999)
            percentile = comparison.percentiles.get(company_name, 0.5)
            num_companies = len(comparison.values)

            # Top performer = Strength
            if rank == 1 or percentile >= 0.8:
                strengths.append(
                    f"Strong {comparison.metric_name} (Rank #{rank}/{num_companies})"
                )

            # Bottom performer = Weakness
            elif rank == num_companies or percentile <= 0.2:
                weaknesses.append(
                    f"Weak {comparison.metric_name} (Rank #{rank}/{num_companies})"
                )

            # Below industry average
            if comparison.industry_average:
                value = comparison.values[company_name]
                if comparison.metric_type == MetricType.HIGHER_BETTER:
                    if value < comparison.industry_average * 0.9:
                        weaknesses.append(
                            f"{comparison.metric_name} below industry average"
                        )
                elif comparison.metric_type == MetricType.LOWER_BETTER:
                    if value > comparison.industry_average * 1.1:
                        weaknesses.append(
                            f"{comparison.metric_name} above industry average"
                        )

        # Add qualitative strengths/weaknesses
        strengths.extend(profile.strengths)
        weaknesses.extend(profile.weaknesses)

        # Generate opportunities based on weaknesses (room to improve)
        for weakness in weaknesses[:3]:
            opportunities.append(f"Improve {weakness.split()[1] if len(weakness.split()) > 1 else weakness}")

        # Generate threats based on competitors' strengths
        for comparison in comparisons:
            if comparison.best_performer and comparison.best_performer != company_name:
                threats.append(
                    f"{comparison.best_performer} leads in {comparison.metric_name}"
                )

        # Limit lists
        strengths = strengths[:5]
        weaknesses = weaknesses[:5]
        opportunities = opportunities[:5]
        threats = threats[:5]

        # Calculate overall score
        strength_score = len(strengths) * 20
        weakness_penalty = len(weaknesses) * 15
        overall_score = min(100, max(0, 50 + strength_score - weakness_penalty))

        return SWOT(
            company=company_name,
            strengths=strengths,
            weaknesses=weaknesses,
            opportunities=opportunities,
            threats=threats,
            overall_score=overall_score
        )

    def _calculate_position(
        self,
        company_name: str,
        comparisons: List[MetricComparison],
        swot: SWOT
    ) -> CompetitivePosition:
        """Calculate competitive position for a company."""
        # Calculate average ranking
        ranks = []
        category_ranks = defaultdict(list)

        for comparison in comparisons:
            if company_name in comparison.rankings:
                rank = comparison.rankings[company_name]
                ranks.append(rank)
                category_ranks[comparison.category].append(rank)

        if not ranks:
            return CompetitivePosition(
                company=company_name,
                market_position="Unknown",
                competitive_advantages=[],
                competitive_disadvantages=[],
                strategic_fit={},
                overall_rank=999,
                score=0
            )

        avg_rank = statistics.mean(ranks)
        num_companies = len(self.companies)

        # Determine market position
        if avg_rank <= num_companies * 0.25:
            position = "Leader"
        elif avg_rank <= num_companies * 0.5:
            position = "Challenger"
        elif avg_rank <= num_companies * 0.75:
            position = "Follower"
        else:
            position = "Niche"

        # Identify advantages and disadvantages
        advantages = []
        disadvantages = []

        for comparison in comparisons:
            if company_name in comparison.rankings:
                rank = comparison.rankings[company_name]
                if rank == 1:
                    advantages.append(f"Best-in-class {comparison.metric_name}")
                elif rank == len(comparison.rankings):
                    disadvantages.append(f"Lagging in {comparison.metric_name}")

        # Strategic fit by category
        strategic_fit = {}
        for category, cat_ranks in category_ranks.items():
            avg_cat_rank = statistics.mean(cat_ranks)
            if avg_cat_rank <= num_companies * 0.33:
                strategic_fit[category.value] = "Strong"
            elif avg_cat_rank <= num_companies * 0.66:
                strategic_fit[category.value] = "Average"
            else:
                strategic_fit[category.value] = "Weak"

        # Calculate composite score
        score = 100 - (avg_rank / num_companies * 100)
        score = score * 0.7 + swot.overall_score * 0.3

        return CompetitivePosition(
            company=company_name,
            market_position=position,
            competitive_advantages=advantages[:5],
            competitive_disadvantages=disadvantages[:5],
            strategic_fit=strategic_fit,
            overall_rank=int(avg_rank),
            score=score
        )

    def _calculate_rankings(
        self,
        comparisons: List[MetricComparison]
    ) -> List[Tuple[str, float]]:
        """Calculate overall company rankings."""
        scores = defaultdict(list)

        for comparison in comparisons:
            for company, percentile in comparison.percentiles.items():
                scores[company].append(percentile)

        # Average percentile = overall score
        final_scores = [
            (company, statistics.mean(percentiles) * 100)
            for company, percentiles in scores.items()
        ]

        return sorted(final_scores, key=lambda x: x[1], reverse=True)

    def _generate_insights(
        self,
        comparisons: List[MetricComparison],
        rankings: List[Tuple[str, float]]
    ) -> List[str]:
        """Generate key insights from the analysis."""
        insights = []

        # Overall leader
        if rankings:
            leader = rankings[0]
            insights.append(f"{leader[0]} leads overall with score {leader[1]:.1f}/100")

        # Target company position
        target_rank = next(
            (i + 1 for i, (name, _) in enumerate(rankings) if name == self.target_company),
            None
        )
        if target_rank:
            insights.append(
                f"{self.target_company} ranks #{target_rank} out of {len(rankings)} companies"
            )

        # Category leaders
        category_leaders = defaultdict(list)
        for comparison in comparisons:
            if comparison.best_performer:
                category_leaders[comparison.category].append(comparison.best_performer)

        for category, leaders in category_leaders.items():
            top_leader = max(set(leaders), key=leaders.count)
            insights.append(f"{top_leader} leads in {category.value} metrics")

        # Biggest gaps
        for comparison in comparisons:
            if comparison.gap_analysis:
                max_gap = max(comparison.gap_analysis.items(), key=lambda x: abs(x[1]))
                if abs(max_gap[1]) > 50:
                    insights.append(
                        f"Large {comparison.metric_name} gap: {max_gap[0]} is {max_gap[1]:+.1f}% vs {self.target_company}"
                    )

        return insights[:10]

    def _generate_recommendations(
        self,
        comparisons: List[MetricComparison],
        swots: Dict[str, SWOT],
        positions: Dict[str, CompetitivePosition]
    ) -> List[str]:
        """Generate strategic recommendations."""
        recommendations = []

        if self.target_company not in swots:
            return ["Insufficient data for recommendations"]

        target_swot = swots[self.target_company]
        target_position = positions[self.target_company]

        # Address weaknesses
        for weakness in target_swot.weaknesses[:2]:
            recommendations.append(f"Priority: Address {weakness}")

        # Leverage strengths
        for strength in target_swot.strengths[:2]:
            recommendations.append(f"Capitalize on {strength}")

        # Position-based recommendations
        if target_position.market_position == "Leader":
            recommendations.append("Defend market position through innovation and customer retention")
        elif target_position.market_position == "Challenger":
            recommendations.append("Target leader's weaknesses to gain market share")
        elif target_position.market_position == "Follower":
            recommendations.append("Identify niche opportunities or differentiation strategies")
        else:
            recommendations.append("Focus on specific market segments for competitive advantage")

        # Metric-specific recommendations
        for comparison in comparisons:
            if self.target_company in comparison.rankings:
                rank = comparison.rankings[self.target_company]
                if rank > len(comparison.rankings) / 2:
                    recommendations.append(
                        f"Improve {comparison.metric_name} to reach industry median"
                    )

        return recommendations[:8]

    def _calculate_confidence(self, comparisons: List[MetricComparison]) -> float:
        """Calculate confidence in the analysis."""
        if not comparisons:
            return 0.0

        # More metrics = higher confidence
        metric_factor = min(len(comparisons) / 10, 1.0)

        # More companies = higher confidence
        company_factor = min(len(self.companies) / 5, 1.0)

        # Industry benchmarks available = higher confidence
        benchmark_factor = 0.5
        for comparison in comparisons:
            if comparison.industry_average:
                benchmark_factor = 1.0
                break

        return (metric_factor * 0.4 + company_factor * 0.4 + benchmark_factor * 0.2)


async def comparative_analyst_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node for comparative analysis."""
    target_company = state.get("company_name", "Unknown")
    competitors = state.get("competitors", [])
    company_data = state.get("company_data", {})

    analyst = ComparativeAnalystAgent(
        target_company=target_company,
        industry=state.get("industry")
    )

    # Add target company
    analyst.add_company(target_company, company_data.get("metrics", {}))

    # Add competitors
    for competitor in competitors:
        if isinstance(competitor, dict):
            analyst.add_company(
                competitor.get("name", "Unknown"),
                competitor.get("metrics", {})
            )

    # Perform analysis
    try:
        analysis = analyst.compare_companies()

        return {
            "comparative_analysis": {
                "target": target_company,
                "companies_compared": analysis.companies_analyzed,
                "rankings": [
                    {"company": name, "score": score}
                    for name, score in analysis.overall_rankings
                ],
                "key_insights": analysis.key_insights,
                "recommendations": analysis.recommendations,
                "confidence": analysis.confidence,
                "swot": {
                    name: {
                        "strengths": swot.strengths,
                        "weaknesses": swot.weaknesses,
                        "opportunities": swot.opportunities,
                        "threats": swot.threats
                    }
                    for name, swot in analysis.swot_analyses.items()
                }
            }
        }
    except ValueError as e:
        return {"comparative_analysis": {"error": str(e)}}


def create_comparative_analyst(
    target_company: str,
    industry: Optional[str] = None
) -> ComparativeAnalystAgent:
    """Factory function to create a comparative analyst."""
    return ComparativeAnalystAgent(
        target_company=target_company,
        industry=industry
    )
