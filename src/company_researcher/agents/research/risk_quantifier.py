"""
Risk Quantifier - Quantifies and categorizes business risks.

This module provides:
- Risk identification from research data
- Risk scoring and categorization
- Risk-adjusted metrics
- Risk matrix generation
- Investment risk assessment

Usage:
    from company_researcher.agents.research.risk_quantifier import (
        RiskQuantifier,
        create_risk_quantifier,
        RiskCategory,
        RiskLevel,
    )

    quantifier = RiskQuantifier()
    assessment = quantifier.assess_risks(company_data, market_data)
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
from ...utils import get_logger

logger = get_logger(__name__)


class RiskCategory(Enum):
    """Categories of business risk."""
    MARKET = "market"           # Market competition, demand changes
    FINANCIAL = "financial"     # Debt, liquidity, profitability
    OPERATIONAL = "operational" # Execution, supply chain, technology
    REGULATORY = "regulatory"   # Compliance, legal, policy changes
    STRATEGIC = "strategic"     # Business model, leadership, M&A
    REPUTATIONAL = "reputational"  # Brand, PR, customer perception
    GEOPOLITICAL = "geopolitical"  # Country risk, trade, currency


class RiskLevel(Enum):
    """Risk severity levels."""
    CRITICAL = 5    # Immediate existential threat
    HIGH = 4        # Significant impact likely
    MEDIUM = 3      # Moderate impact possible
    LOW = 2         # Minor impact expected
    MINIMAL = 1     # Negligible impact


class RiskProbability(Enum):
    """Probability of risk occurrence."""
    VERY_LIKELY = 5    # >80% chance
    LIKELY = 4         # 60-80% chance
    POSSIBLE = 3       # 40-60% chance
    UNLIKELY = 2       # 20-40% chance
    RARE = 1           # <20% chance


@dataclass
class Risk:
    """A quantified risk."""
    name: str
    category: RiskCategory
    level: RiskLevel
    probability: RiskProbability
    impact_score: float         # 1-10 scale
    likelihood_score: float     # 1-10 scale
    risk_score: float           # Combined score
    description: str
    mitigation: Optional[str] = None
    trend: str = "stable"       # increasing, stable, decreasing
    source: Optional[str] = None


@dataclass
class RiskAssessment:
    """Complete risk assessment result."""
    company_name: str
    overall_risk_score: float   # 1-100
    risk_grade: str             # A, B, C, D, F
    risks: List[Risk]
    risk_by_category: Dict[str, List[Risk]]
    risk_matrix: Dict[str, Dict[str, float]]  # {category: {metric: score}}
    key_risks: List[str]        # Top 3-5 risks
    risk_adjusted_metrics: Dict[str, float]
    recommendations: List[str]
    summary: str


# Risk indicators from text content
RISK_INDICATORS = {
    RiskCategory.MARKET: [
        r"declining\s+market\s+share",
        r"intense\s+competition",
        r"market\s+saturation",
        r"new\s+entrants?",
        r"disruption|disruptive",
        r"commoditization",
        r"price\s+war",
        r"demand\s+decline",
    ],
    RiskCategory.FINANCIAL: [
        r"debt\s+(?:burden|level|load)",
        r"liquidity\s+(?:concern|issue|problem)",
        r"cash\s+flow\s+(?:negative|concern)",
        r"profit(?:ability)?\s+(?:decline|pressure)",
        r"credit\s+(?:downgrade|rating)",
        r"bankruptcy|insolvency",
        r"loss(?:es)?\s+reported",
        r"margin\s+(?:compression|decline|pressure)",
    ],
    RiskCategory.OPERATIONAL: [
        r"supply\s+chain\s+(?:disruption|issue)",
        r"operational\s+(?:challenge|issue)",
        r"technology\s+(?:failure|risk|debt)",
        r"cybersecurity|cyber\s+(?:attack|threat)",
        r"talent\s+(?:shortage|retention)",
        r"execution\s+risk",
        r"manufacturing\s+(?:issue|problem)",
    ],
    RiskCategory.REGULATORY: [
        r"regulatory\s+(?:scrutiny|investigation|fine)",
        r"compliance\s+(?:issue|violation|risk)",
        r"antitrust|anti-trust",
        r"data\s+privacy",
        r"litigation|lawsuit",
        r"government\s+(?:regulation|intervention)",
        r"policy\s+(?:change|risk)",
    ],
    RiskCategory.STRATEGIC: [
        r"leadership\s+(?:change|turnover|uncertainty)",
        r"strategy\s+(?:shift|pivot|uncertainty)",
        r"acquisition\s+(?:risk|integration)",
        r"diversification\s+(?:lack|need)",
        r"business\s+model\s+(?:risk|challenge)",
        r"succession\s+(?:planning|risk)",
    ],
    RiskCategory.REPUTATIONAL: [
        r"reputation(?:al)?\s+(?:risk|damage|concern)",
        r"brand\s+(?:damage|crisis)",
        r"customer\s+(?:complaint|dissatisfaction)",
        r"scandal|controversy",
        r"negative\s+(?:publicity|press|coverage)",
        r"social\s+media\s+(?:backlash|crisis)",
    ],
    RiskCategory.GEOPOLITICAL: [
        r"geopolitical\s+(?:risk|tension|uncertainty)",
        r"trade\s+(?:war|tension|barrier)",
        r"currency\s+(?:risk|volatility|exposure)",
        r"emerging\s+market\s+(?:risk|exposure)",
        r"political\s+(?:instability|risk)",
        r"sanctions?",
        r"tariff",
    ],
}


class RiskQuantifier:
    """Quantifies business risks from research data."""

    # Base risk weights by category
    CATEGORY_WEIGHTS = {
        RiskCategory.FINANCIAL: 0.20,
        RiskCategory.MARKET: 0.18,
        RiskCategory.OPERATIONAL: 0.15,
        RiskCategory.REGULATORY: 0.15,
        RiskCategory.STRATEGIC: 0.12,
        RiskCategory.REPUTATIONAL: 0.10,
        RiskCategory.GEOPOLITICAL: 0.10,
    }

    # Risk grade thresholds
    GRADE_THRESHOLDS = {
        "A": (0, 20),      # Very low risk
        "B": (20, 40),     # Low risk
        "C": (40, 60),     # Moderate risk
        "D": (60, 80),     # High risk
        "F": (80, 100),    # Very high risk
    }

    def __init__(
        self,
        custom_weights: Optional[Dict[str, float]] = None,
        risk_tolerance: str = "moderate"  # conservative, moderate, aggressive
    ):
        """Initialize the risk quantifier."""
        self.category_weights = self.CATEGORY_WEIGHTS.copy()
        if custom_weights:
            for cat, weight in custom_weights.items():
                if cat in self.category_weights:
                    self.category_weights[cat] = weight

        self.risk_tolerance = risk_tolerance

    def assess_risks(
        self,
        company_name: str,
        company_data: Dict[str, Any],
        market_data: Optional[Dict[str, Any]] = None,
        content: Optional[str] = None
    ) -> RiskAssessment:
        """
        Perform comprehensive risk assessment.

        Args:
            company_name: Name of the company
            company_data: Financial and operational data
            market_data: Market and competitive data
            content: Raw text content to analyze for risk indicators

        Returns:
            RiskAssessment with quantified risks
        """
        logger.info(f"Assessing risks for {company_name}")

        risks = []

        # Extract risks from text content
        if content:
            text_risks = self._extract_risks_from_text(content)
            risks.extend(text_risks)

        # Assess financial risks
        financial_risks = self._assess_financial_risks(company_data)
        risks.extend(financial_risks)

        # Assess market risks
        if market_data:
            market_risks = self._assess_market_risks(market_data)
            risks.extend(market_risks)

        # Assess operational risks
        operational_risks = self._assess_operational_risks(company_data)
        risks.extend(operational_risks)

        # Calculate overall risk score
        overall_score = self._calculate_overall_score(risks)

        # Determine risk grade
        risk_grade = self._determine_grade(overall_score)

        # Group risks by category
        risk_by_category = self._group_by_category(risks)

        # Generate risk matrix
        risk_matrix = self._generate_risk_matrix(risks)

        # Identify key risks (top 5)
        key_risks = self._identify_key_risks(risks)

        # Calculate risk-adjusted metrics
        risk_adjusted = self._calculate_risk_adjusted_metrics(
            company_data, overall_score
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(risks, risk_grade)

        # Generate summary
        summary = self._generate_summary(
            company_name, overall_score, risk_grade, risks
        )

        return RiskAssessment(
            company_name=company_name,
            overall_risk_score=overall_score,
            risk_grade=risk_grade,
            risks=risks,
            risk_by_category=risk_by_category,
            risk_matrix=risk_matrix,
            key_risks=key_risks,
            risk_adjusted_metrics=risk_adjusted,
            recommendations=recommendations,
            summary=summary
        )

    def _extract_risks_from_text(self, content: str) -> List[Risk]:
        """Extract risks from text content using pattern matching."""
        risks = []
        content_lower = content.lower()

        for category, patterns in RISK_INDICATORS.items():
            for pattern in patterns:
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                if matches:
                    # Create risk based on indicator
                    risk = Risk(
                        name=self._pattern_to_name(pattern),
                        category=category,
                        level=RiskLevel.MEDIUM,  # Default
                        probability=RiskProbability.POSSIBLE,
                        impact_score=5.0,
                        likelihood_score=5.0,
                        risk_score=25.0,
                        description=f"Identified from content: {matches[0]}",
                        source="text_analysis"
                    )
                    risks.append(risk)

        return risks

    def _pattern_to_name(self, pattern: str) -> str:
        """Convert regex pattern to readable risk name."""
        # Remove regex special chars and format
        name = re.sub(r'\\s\+|\\s\*|\?\!|\?|\\', ' ', pattern)
        name = re.sub(r'\(\?:[^)]+\)', '', name)
        name = re.sub(r'[()|\[\]]', '', name)
        name = name.strip().replace('  ', ' ')
        return name.title()

    def _assess_financial_risks(self, company_data: Dict[str, Any]) -> List[Risk]:
        """Assess financial risks from company data."""
        risks = []

        # Debt-to-equity risk
        debt_equity = company_data.get("debt_to_equity")
        if debt_equity is not None:
            if debt_equity > 2.0:
                risks.append(Risk(
                    name="High Leverage",
                    category=RiskCategory.FINANCIAL,
                    level=RiskLevel.HIGH,
                    probability=RiskProbability.LIKELY,
                    impact_score=7.0,
                    likelihood_score=7.0,
                    risk_score=49.0,
                    description=f"Debt-to-equity ratio of {debt_equity:.2f} indicates high leverage",
                    mitigation="Consider debt reduction or equity financing"
                ))
            elif debt_equity > 1.0:
                risks.append(Risk(
                    name="Moderate Leverage",
                    category=RiskCategory.FINANCIAL,
                    level=RiskLevel.MEDIUM,
                    probability=RiskProbability.POSSIBLE,
                    impact_score=5.0,
                    likelihood_score=5.0,
                    risk_score=25.0,
                    description=f"Debt-to-equity ratio of {debt_equity:.2f}",
                    mitigation="Monitor debt levels"
                ))

        # Profit margin risk
        profit_margin = company_data.get("profit_margin")
        if profit_margin is not None:
            if profit_margin < 5:
                risks.append(Risk(
                    name="Low Profitability",
                    category=RiskCategory.FINANCIAL,
                    level=RiskLevel.HIGH,
                    probability=RiskProbability.LIKELY,
                    impact_score=6.0,
                    likelihood_score=7.0,
                    risk_score=42.0,
                    description=f"Profit margin of {profit_margin:.1f}% is below healthy threshold",
                    mitigation="Focus on cost reduction and pricing optimization"
                ))

        # Revenue growth risk
        revenue_growth = company_data.get("revenue_growth")
        if revenue_growth is not None:
            if revenue_growth < -10:
                risks.append(Risk(
                    name="Revenue Decline",
                    category=RiskCategory.FINANCIAL,
                    level=RiskLevel.HIGH,
                    probability=RiskProbability.VERY_LIKELY,
                    impact_score=8.0,
                    likelihood_score=9.0,
                    risk_score=72.0,
                    description=f"Revenue declining at {revenue_growth:.1f}%",
                    mitigation="Urgent need for revenue diversification"
                ))
            elif revenue_growth < 0:
                risks.append(Risk(
                    name="Stagnant Revenue",
                    category=RiskCategory.FINANCIAL,
                    level=RiskLevel.MEDIUM,
                    probability=RiskProbability.LIKELY,
                    impact_score=5.0,
                    likelihood_score=6.0,
                    risk_score=30.0,
                    description=f"Revenue growth of {revenue_growth:.1f}%",
                    mitigation="Explore growth opportunities"
                ))

        return risks

    def _assess_market_risks(self, market_data: Dict[str, Any]) -> List[Risk]:
        """Assess market risks from competitive data."""
        risks = []

        # Market share risk
        market_share = market_data.get("market_share")
        if market_share is not None:
            if market_share < 5:
                risks.append(Risk(
                    name="Low Market Share",
                    category=RiskCategory.MARKET,
                    level=RiskLevel.MEDIUM,
                    probability=RiskProbability.POSSIBLE,
                    impact_score=5.0,
                    likelihood_score=6.0,
                    risk_score=30.0,
                    description=f"Market share of {market_share:.1f}% indicates limited market presence",
                    mitigation="Focus on market expansion strategies"
                ))

        # Competitive intensity
        competitors = market_data.get("competitors", [])
        if len(competitors) > 10:
            risks.append(Risk(
                name="High Competition",
                category=RiskCategory.MARKET,
                level=RiskLevel.MEDIUM,
                probability=RiskProbability.LIKELY,
                impact_score=5.0,
                likelihood_score=7.0,
                risk_score=35.0,
                description=f"Operating in highly competitive market with {len(competitors)}+ competitors",
                mitigation="Differentiation and niche focus"
            ))

        # Market growth
        market_growth = market_data.get("market_growth")
        if market_growth is not None and market_growth < 0:
            risks.append(Risk(
                name="Declining Market",
                category=RiskCategory.MARKET,
                level=RiskLevel.HIGH,
                probability=RiskProbability.LIKELY,
                impact_score=7.0,
                likelihood_score=7.0,
                risk_score=49.0,
                description=f"Operating in declining market ({market_growth:.1f}% growth)",
                mitigation="Consider market pivot or diversification"
            ))

        return risks

    def _assess_operational_risks(self, company_data: Dict[str, Any]) -> List[Risk]:
        """Assess operational risks."""
        risks = []

        # Employee turnover
        turnover = company_data.get("employee_turnover")
        if turnover is not None and turnover > 20:
            risks.append(Risk(
                name="High Employee Turnover",
                category=RiskCategory.OPERATIONAL,
                level=RiskLevel.MEDIUM,
                probability=RiskProbability.LIKELY,
                impact_score=5.0,
                likelihood_score=6.0,
                risk_score=30.0,
                description=f"Employee turnover of {turnover:.1f}% indicates retention issues",
                mitigation="Improve employee engagement and compensation"
            ))

        # Technology dependency
        tech_age = company_data.get("tech_stack_age")
        if tech_age is not None and tech_age > 5:
            risks.append(Risk(
                name="Technology Obsolescence",
                category=RiskCategory.OPERATIONAL,
                level=RiskLevel.MEDIUM,
                probability=RiskProbability.POSSIBLE,
                impact_score=6.0,
                likelihood_score=5.0,
                risk_score=30.0,
                description="Legacy technology stack may require modernization",
                mitigation="Plan technology upgrade roadmap"
            ))

        return risks

    def _calculate_overall_score(self, risks: List[Risk]) -> float:
        """Calculate overall risk score (0-100)."""
        if not risks:
            return 20.0  # Base risk level

        # Weight by category
        category_scores = {}
        for risk in risks:
            cat = risk.category
            if cat not in category_scores:
                category_scores[cat] = []
            category_scores[cat].append(risk.risk_score)

        # Calculate weighted average
        weighted_sum = 0.0
        total_weight = 0.0

        for category, weight in self.category_weights.items():
            if category in category_scores:
                cat_avg = sum(category_scores[category]) / len(category_scores[category])
                weighted_sum += cat_avg * weight
                total_weight += weight

        if total_weight > 0:
            overall = weighted_sum / total_weight
        else:
            overall = 20.0

        # Normalize to 0-100
        return min(100, max(0, overall))

    def _determine_grade(self, score: float) -> str:
        """Determine risk grade from score."""
        for grade, (low, high) in self.GRADE_THRESHOLDS.items():
            if low <= score < high:
                return grade
        return "F"

    def _group_by_category(self, risks: List[Risk]) -> Dict[str, List[Risk]]:
        """Group risks by category."""
        grouped = {}
        for risk in risks:
            cat_name = risk.category.value
            if cat_name not in grouped:
                grouped[cat_name] = []
            grouped[cat_name].append(risk)
        return grouped

    def _generate_risk_matrix(self, risks: List[Risk]) -> Dict[str, Dict[str, float]]:
        """Generate risk matrix (impact vs likelihood by category)."""
        matrix = {}
        for risk in risks:
            cat = risk.category.value
            if cat not in matrix:
                matrix[cat] = {"impact": 0, "likelihood": 0, "count": 0}
            matrix[cat]["impact"] += risk.impact_score
            matrix[cat]["likelihood"] += risk.likelihood_score
            matrix[cat]["count"] += 1

        # Average the scores
        for cat in matrix:
            if matrix[cat]["count"] > 0:
                matrix[cat]["impact"] /= matrix[cat]["count"]
                matrix[cat]["likelihood"] /= matrix[cat]["count"]
            del matrix[cat]["count"]

        return matrix

    def _identify_key_risks(self, risks: List[Risk]) -> List[str]:
        """Identify top 5 key risks."""
        sorted_risks = sorted(risks, key=lambda r: r.risk_score, reverse=True)
        return [f"{r.name}: {r.description}" for r in sorted_risks[:5]]

    def _calculate_risk_adjusted_metrics(
        self,
        company_data: Dict[str, Any],
        risk_score: float
    ) -> Dict[str, float]:
        """Calculate risk-adjusted financial metrics."""
        risk_discount = risk_score / 100  # 0-1 scale

        metrics = {}

        # Risk-adjusted revenue growth
        revenue_growth = company_data.get("revenue_growth")
        if revenue_growth is not None:
            metrics["risk_adjusted_growth"] = revenue_growth * (1 - risk_discount * 0.5)

        # Risk-adjusted valuation multiple
        pe_ratio = company_data.get("pe_ratio")
        if pe_ratio is not None:
            metrics["risk_adjusted_pe"] = pe_ratio * (1 - risk_discount * 0.3)

        # Risk premium
        metrics["implied_risk_premium"] = risk_discount * 10  # 0-10% risk premium

        return metrics

    def _generate_recommendations(
        self,
        risks: List[Risk],
        grade: str
    ) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []

        # Grade-based recommendations
        if grade in ["D", "F"]:
            recommendations.append(
                "URGENT: Implement comprehensive risk management program"
            )

        # Category-specific recommendations
        categories_found = set(r.category for r in risks)

        if RiskCategory.FINANCIAL in categories_found:
            recommendations.append(
                "Review financial structure and improve liquidity position"
            )

        if RiskCategory.MARKET in categories_found:
            recommendations.append(
                "Strengthen competitive positioning and market differentiation"
            )

        if RiskCategory.OPERATIONAL in categories_found:
            recommendations.append(
                "Enhance operational efficiency and technology infrastructure"
            )

        if RiskCategory.REGULATORY in categories_found:
            recommendations.append(
                "Strengthen compliance framework and regulatory monitoring"
            )

        # Risk-specific mitigations
        for risk in sorted(risks, key=lambda r: r.risk_score, reverse=True)[:3]:
            if risk.mitigation:
                recommendations.append(f"For {risk.name}: {risk.mitigation}")

        return recommendations[:7]  # Limit to 7 recommendations

    def _generate_summary(
        self,
        company_name: str,
        score: float,
        grade: str,
        risks: List[Risk]
    ) -> str:
        """Generate executive risk summary."""
        risk_count = len(risks)
        high_risks = sum(1 for r in risks if r.level in [RiskLevel.CRITICAL, RiskLevel.HIGH])

        summary_parts = [
            f"Risk Assessment for {company_name}: Grade {grade} (Score: {score:.0f}/100)"
        ]

        if grade == "A":
            summary_parts.append("Overall risk profile is very low.")
        elif grade == "B":
            summary_parts.append("Risk profile is manageable with standard practices.")
        elif grade == "C":
            summary_parts.append("Moderate risk level requires active management.")
        elif grade == "D":
            summary_parts.append("High risk level demands significant attention.")
        else:
            summary_parts.append("Critical risk level - immediate action required.")

        summary_parts.append(
            f"Identified {risk_count} risk factors, including {high_risks} high/critical risks."
        )

        return " ".join(summary_parts)


def create_risk_quantifier(
    custom_weights: Optional[Dict[str, float]] = None,
    risk_tolerance: str = "moderate"
) -> RiskQuantifier:
    """Factory function to create RiskQuantifier."""
    return RiskQuantifier(
        custom_weights=custom_weights,
        risk_tolerance=risk_tolerance
    )
