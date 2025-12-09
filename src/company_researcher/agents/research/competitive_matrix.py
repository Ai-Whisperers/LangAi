"""
Competitive Matrix Generator - Creates structured competitor comparison matrices.

This module provides:
- Competitive matrix generation from extracted data
- Feature comparison tables
- Market position mapping
- Strategic group analysis
- Integration with market analysis

Usage:
    from company_researcher.agents.research.competitive_matrix import (
        CompetitiveMatrixGenerator,
        create_competitive_matrix,
        MatrixDimension,
    )

    generator = CompetitiveMatrixGenerator()
    matrix = generator.generate_matrix(company_name, competitors, dimensions)
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class MatrixDimension(Enum):
    """Dimensions for competitive comparison."""
    MARKET_SHARE = "market_share"
    REVENUE = "revenue"
    PRICING = "pricing"
    PRODUCT_RANGE = "product_range"
    GEOGRAPHIC_REACH = "geographic_reach"
    TECHNOLOGY = "technology"
    BRAND_STRENGTH = "brand_strength"
    CUSTOMER_SERVICE = "customer_service"
    INNOVATION = "innovation"
    FINANCIAL_STRENGTH = "financial_strength"


class CompetitivePosition(Enum):
    """Strategic positioning categories."""
    LEADER = "leader"
    CHALLENGER = "challenger"
    FOLLOWER = "follower"
    NICHE = "niche"


@dataclass
class CompetitorProfile:
    """Profile of a competitor for matrix comparison."""
    name: str
    market_share: Optional[float] = None
    revenue: Optional[float] = None
    employees: Optional[int] = None
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    products: List[str] = field(default_factory=list)
    position: Optional[CompetitivePosition] = None
    threat_level: str = "moderate"
    scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class CompetitiveMatrix:
    """Complete competitive matrix result."""
    company_name: str
    competitors: List[CompetitorProfile]
    dimensions: List[MatrixDimension]
    matrix_data: Dict[str, Dict[str, float]]  # {company: {dimension: score}}
    strategic_groups: Dict[str, List[str]]  # {group_name: [companies]}
    market_map: Dict[str, Tuple[float, float]]  # {company: (x_pos, y_pos)}
    insights: List[str]
    recommendations: List[str]
    summary: str


class CompetitiveMatrixGenerator:
    """Generates competitive comparison matrices."""

    # Default scoring criteria for each dimension
    SCORING_CRITERIA = {
        MatrixDimension.MARKET_SHARE: {
            "weight": 0.15,
            "scale": "percentage",
            "higher_is_better": True
        },
        MatrixDimension.REVENUE: {
            "weight": 0.12,
            "scale": "billions",
            "higher_is_better": True
        },
        MatrixDimension.PRICING: {
            "weight": 0.10,
            "scale": "1-10",
            "higher_is_better": False  # Lower price often better for customers
        },
        MatrixDimension.PRODUCT_RANGE: {
            "weight": 0.12,
            "scale": "1-10",
            "higher_is_better": True
        },
        MatrixDimension.GEOGRAPHIC_REACH: {
            "weight": 0.10,
            "scale": "1-10",
            "higher_is_better": True
        },
        MatrixDimension.TECHNOLOGY: {
            "weight": 0.12,
            "scale": "1-10",
            "higher_is_better": True
        },
        MatrixDimension.BRAND_STRENGTH: {
            "weight": 0.10,
            "scale": "1-10",
            "higher_is_better": True
        },
        MatrixDimension.CUSTOMER_SERVICE: {
            "weight": 0.08,
            "scale": "1-10",
            "higher_is_better": True
        },
        MatrixDimension.INNOVATION: {
            "weight": 0.06,
            "scale": "1-10",
            "higher_is_better": True
        },
        MatrixDimension.FINANCIAL_STRENGTH: {
            "weight": 0.05,
            "scale": "1-10",
            "higher_is_better": True
        },
    }

    def __init__(self, custom_weights: Optional[Dict[str, float]] = None):
        """Initialize the matrix generator."""
        self.custom_weights = custom_weights or {}

    def generate_matrix(
        self,
        company_name: str,
        company_data: Dict[str, Any],
        competitors_data: List[Dict[str, Any]],
        dimensions: Optional[List[MatrixDimension]] = None
    ) -> CompetitiveMatrix:
        """
        Generate a competitive comparison matrix.

        Args:
            company_name: Name of the target company
            company_data: Data about the target company
            competitors_data: List of competitor data dictionaries
            dimensions: Dimensions to compare (default: all)

        Returns:
            CompetitiveMatrix with comparison data
        """
        logger.info(f"Generating competitive matrix for {company_name}")

        if dimensions is None:
            dimensions = list(MatrixDimension)

        # Build competitor profiles
        competitors = self._build_competitor_profiles(competitors_data)

        # Generate matrix scores
        matrix_data = self._generate_matrix_scores(
            company_name, company_data, competitors, dimensions
        )

        # Identify strategic groups
        strategic_groups = self._identify_strategic_groups(
            company_name, company_data, competitors
        )

        # Generate market position map
        market_map = self._generate_market_map(
            company_name, company_data, competitors
        )

        # Generate insights
        insights = self._generate_insights(
            company_name, company_data, competitors, matrix_data
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            company_name, company_data, competitors, matrix_data
        )

        # Generate summary
        summary = self._generate_summary(
            company_name, competitors, insights
        )

        return CompetitiveMatrix(
            company_name=company_name,
            competitors=competitors,
            dimensions=dimensions,
            matrix_data=matrix_data,
            strategic_groups=strategic_groups,
            market_map=market_map,
            insights=insights,
            recommendations=recommendations,
            summary=summary
        )

    def _build_competitor_profiles(
        self,
        competitors_data: List[Dict[str, Any]]
    ) -> List[CompetitorProfile]:
        """Build competitor profile objects from raw data."""
        profiles = []

        for comp_data in competitors_data:
            profile = CompetitorProfile(
                name=comp_data.get("name", "Unknown"),
                market_share=comp_data.get("market_share"),
                revenue=comp_data.get("revenue"),
                employees=comp_data.get("employees"),
                strengths=comp_data.get("strengths", []),
                weaknesses=comp_data.get("weaknesses", []),
                products=comp_data.get("products", []),
                threat_level=comp_data.get("threat_level", "moderate"),
                scores=comp_data.get("scores", {})
            )

            # Determine position
            profile.position = self._determine_position(profile)
            profiles.append(profile)

        return profiles

    def _determine_position(self, competitor: CompetitorProfile) -> CompetitivePosition:
        """Determine strategic position of competitor."""
        if competitor.market_share:
            if competitor.market_share >= 30:
                return CompetitivePosition.LEADER
            elif competitor.market_share >= 15:
                return CompetitivePosition.CHALLENGER
            elif competitor.market_share >= 5:
                return CompetitivePosition.FOLLOWER
            else:
                return CompetitivePosition.NICHE
        return CompetitivePosition.FOLLOWER

    def _generate_matrix_scores(
        self,
        company_name: str,
        company_data: Dict[str, Any],
        competitors: List[CompetitorProfile],
        dimensions: List[MatrixDimension]
    ) -> Dict[str, Dict[str, float]]:
        """Generate normalized scores for matrix comparison."""
        matrix = {}

        # Add company scores
        matrix[company_name] = self._score_company(company_data, dimensions)

        # Add competitor scores
        for competitor in competitors:
            matrix[competitor.name] = self._score_competitor(competitor, dimensions)

        # Normalize scores to 0-100 scale
        matrix = self._normalize_scores(matrix, dimensions)

        return matrix

    def _score_company(
        self,
        company_data: Dict[str, Any],
        dimensions: List[MatrixDimension]
    ) -> Dict[str, float]:
        """Score target company on each dimension."""
        scores = {}

        for dim in dimensions:
            dim_name = dim.value
            score = company_data.get(f"{dim_name}_score")

            if score is None:
                # Try to derive score from raw data
                score = self._derive_score(company_data, dim)

            scores[dim_name] = score if score is not None else 5.0  # Default mid-range

        return scores

    def _score_competitor(
        self,
        competitor: CompetitorProfile,
        dimensions: List[MatrixDimension]
    ) -> Dict[str, float]:
        """Score competitor on each dimension."""
        scores = {}

        for dim in dimensions:
            dim_name = dim.value

            # Check if score already exists
            if dim_name in competitor.scores:
                scores[dim_name] = competitor.scores[dim_name]
            elif dim == MatrixDimension.MARKET_SHARE and competitor.market_share:
                scores[dim_name] = competitor.market_share
            elif dim == MatrixDimension.REVENUE and competitor.revenue:
                scores[dim_name] = min(competitor.revenue / 10, 10)  # Normalize to 10 scale
            else:
                # Default based on position
                default_scores = {
                    CompetitivePosition.LEADER: 8.0,
                    CompetitivePosition.CHALLENGER: 6.5,
                    CompetitivePosition.FOLLOWER: 5.0,
                    CompetitivePosition.NICHE: 4.0
                }
                scores[dim_name] = default_scores.get(competitor.position, 5.0)

        return scores

    def _derive_score(
        self,
        data: Dict[str, Any],
        dimension: MatrixDimension
    ) -> Optional[float]:
        """Derive score from raw data."""
        if dimension == MatrixDimension.MARKET_SHARE:
            return data.get("market_share")
        elif dimension == MatrixDimension.REVENUE:
            revenue = data.get("revenue")
            if revenue:
                # Logarithmic scale for revenue
                import math
                return min(math.log10(max(revenue, 1)) * 2, 10)
        elif dimension == MatrixDimension.FINANCIAL_STRENGTH:
            # Use revenue or other financial metrics as proxy
            revenue = data.get("revenue")
            if revenue:
                import math
                return min(math.log10(max(revenue, 1)) * 2, 10)
        return None

    def _normalize_scores(
        self,
        matrix: Dict[str, Dict[str, float]],
        dimensions: List[MatrixDimension]
    ) -> Dict[str, Dict[str, float]]:
        """Normalize scores to 0-100 scale across all companies."""
        normalized = {}

        for dim in dimensions:
            dim_name = dim.value
            values = [matrix[comp].get(dim_name, 0) for comp in matrix]

            if values:
                max_val = max(values) if max(values) > 0 else 1
                min_val = min(values)
                range_val = max_val - min_val if max_val != min_val else 1

                for comp in matrix:
                    if comp not in normalized:
                        normalized[comp] = {}
                    raw = matrix[comp].get(dim_name, 0)
                    normalized[comp][dim_name] = ((raw - min_val) / range_val) * 100

        return normalized

    def _identify_strategic_groups(
        self,
        company_name: str,
        company_data: Dict[str, Any],
        competitors: List[CompetitorProfile]
    ) -> Dict[str, List[str]]:
        """Identify strategic groups based on similarity."""
        groups = {
            "premium": [],
            "value": [],
            "niche": [],
            "broad_market": []
        }

        # Classify company
        company_group = self._classify_strategic_group(company_data)
        groups[company_group].append(company_name)

        # Classify competitors
        for competitor in competitors:
            comp_group = self._classify_strategic_group_competitor(competitor)
            groups[comp_group].append(competitor.name)

        # Remove empty groups
        return {k: v for k, v in groups.items() if v}

    def _classify_strategic_group(self, data: Dict[str, Any]) -> str:
        """Classify company into strategic group."""
        market_share = data.get("market_share", 0)
        product_range = data.get("product_range_score", 5)

        if market_share > 20 and product_range > 7:
            return "broad_market"
        elif market_share > 10:
            return "premium"
        elif product_range < 4:
            return "niche"
        else:
            return "value"

    def _classify_strategic_group_competitor(self, competitor: CompetitorProfile) -> str:
        """Classify competitor into strategic group."""
        if competitor.position == CompetitivePosition.LEADER:
            return "broad_market"
        elif competitor.position == CompetitivePosition.CHALLENGER:
            return "premium"
        elif competitor.position == CompetitivePosition.NICHE:
            return "niche"
        else:
            return "value"

    def _generate_market_map(
        self,
        company_name: str,
        company_data: Dict[str, Any],
        competitors: List[CompetitorProfile]
    ) -> Dict[str, Tuple[float, float]]:
        """Generate market position map (x=price, y=quality)."""
        market_map = {}

        # Company position
        price = company_data.get("pricing_score", 5)
        quality = company_data.get("product_range_score", 5)
        market_map[company_name] = (price * 10, quality * 10)

        # Competitor positions
        for competitor in competitors:
            price_score = competitor.scores.get("pricing", 5)
            quality_score = competitor.scores.get("product_range", 5)
            market_map[competitor.name] = (price_score * 10, quality_score * 10)

        return market_map

    def _generate_insights(
        self,
        company_name: str,
        company_data: Dict[str, Any],
        competitors: List[CompetitorProfile],
        matrix: Dict[str, Dict[str, float]]
    ) -> List[str]:
        """Generate competitive insights from matrix analysis."""
        insights = []

        company_scores = matrix.get(company_name, {})

        # Find strengths (top 20% scores)
        if company_scores:
            avg_score = sum(company_scores.values()) / len(company_scores)
            strengths = [dim for dim, score in company_scores.items() if score > 70]
            weaknesses = [dim for dim, score in company_scores.items() if score < 30]

            if strengths:
                insights.append(
                    f"Competitive advantages: Strong performance in {', '.join(strengths[:3])}"
                )

            if weaknesses:
                insights.append(
                    f"Areas for improvement: Below average in {', '.join(weaknesses[:3])}"
                )

        # Competitor threats
        leaders = [c for c in competitors if c.position == CompetitivePosition.LEADER]
        challengers = [c for c in competitors if c.position == CompetitivePosition.CHALLENGER]

        if leaders:
            insights.append(
                f"Market leaders to watch: {', '.join(c.name for c in leaders[:2])}"
            )

        if challengers:
            insights.append(
                f"Rising challengers: {', '.join(c.name for c in challengers[:2])}"
            )

        # Threat assessment
        high_threat = [c for c in competitors if c.threat_level == "high"]
        if high_threat:
            insights.append(
                f"High-threat competitors: {', '.join(c.name for c in high_threat[:3])}"
            )

        return insights

    def _generate_recommendations(
        self,
        company_name: str,
        company_data: Dict[str, Any],
        competitors: List[CompetitorProfile],
        matrix: Dict[str, Dict[str, float]]
    ) -> List[str]:
        """Generate strategic recommendations."""
        recommendations = []

        company_scores = matrix.get(company_name, {})

        # Identify improvement opportunities
        if company_scores:
            # Find dimensions where competitors score higher
            for competitor in competitors[:3]:  # Top 3 competitors
                comp_scores = matrix.get(competitor.name, {})
                for dim, score in comp_scores.items():
                    company_score = company_scores.get(dim, 0)
                    if score > company_score + 20:
                        recommendations.append(
                            f"Consider improving {dim.replace('_', ' ')} to match {competitor.name}'s performance"
                        )

        # Strategic positioning
        niche_competitors = [c for c in competitors if c.position == CompetitivePosition.NICHE]
        if niche_competitors:
            recommendations.append(
                "Monitor niche players for potential disruption: " +
                ", ".join(c.name for c in niche_competitors[:2])
            )

        # Competitive defense
        if any(c.threat_level == "high" for c in competitors):
            recommendations.append(
                "Develop defensive strategies for high-threat competitors"
            )

        return recommendations[:5]  # Limit to top 5

    def _generate_summary(
        self,
        company_name: str,
        competitors: List[CompetitorProfile],
        insights: List[str]
    ) -> str:
        """Generate executive summary of competitive analysis."""
        num_competitors = len(competitors)
        leaders = sum(1 for c in competitors if c.position == CompetitivePosition.LEADER)
        challengers = sum(1 for c in competitors if c.position == CompetitivePosition.CHALLENGER)

        summary_parts = [
            f"Competitive analysis for {company_name} against {num_competitors} competitors."
        ]

        if leaders:
            summary_parts.append(f"Market includes {leaders} established leader(s).")
        if challengers:
            summary_parts.append(f"{challengers} active challenger(s) identified.")

        if insights:
            summary_parts.append(f"Key finding: {insights[0]}")

        return " ".join(summary_parts)

    def format_as_markdown_table(
        self,
        matrix: CompetitiveMatrix,
        dimensions: Optional[List[str]] = None
    ) -> str:
        """Format competitive matrix as markdown table."""
        if dimensions is None:
            dimensions = [d.value for d in matrix.dimensions[:6]]  # Limit columns

        # Header
        header = "| Company | " + " | ".join(d.replace("_", " ").title() for d in dimensions) + " |"
        separator = "|" + "|".join("---" for _ in range(len(dimensions) + 1)) + "|"

        # Rows
        rows = [header, separator]

        for company, scores in matrix.matrix_data.items():
            row_values = [f"{scores.get(d, 0):.0f}" for d in dimensions]
            rows.append(f"| {company} | " + " | ".join(row_values) + " |")

        return "\n".join(rows)


def create_competitive_matrix(
    company_name: str,
    company_data: Dict[str, Any],
    competitors_data: List[Dict[str, Any]],
    dimensions: Optional[List[MatrixDimension]] = None
) -> CompetitiveMatrix:
    """Factory function to generate competitive matrix."""
    generator = CompetitiveMatrixGenerator()
    return generator.generate_matrix(
        company_name, company_data, competitors_data, dimensions
    )
