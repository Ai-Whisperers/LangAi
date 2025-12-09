"""
Investment Thesis Generator - Creates structured investment recommendations.

This module provides:
- Investment thesis generation from research data
- Bull/bear case analysis
- Valuation framework
- Investment recommendations with rationale
- Risk/reward assessment

Usage:
    from company_researcher.agents.research.investment_thesis import (
        InvestmentThesisGenerator,
        create_thesis_generator,
        InvestmentRecommendation,
    )

    generator = InvestmentThesisGenerator()
    thesis = generator.generate_thesis(company_data, financials, risks)
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class InvestmentRecommendation(Enum):
    """Investment recommendation categories."""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"
    NOT_RATED = "not_rated"


class InvestmentHorizon(Enum):
    """Investment time horizon."""
    SHORT_TERM = "short_term"      # < 1 year
    MEDIUM_TERM = "medium_term"    # 1-3 years
    LONG_TERM = "long_term"        # 3+ years


class InvestorProfile(Enum):
    """Target investor profile."""
    GROWTH = "growth"              # High growth, higher risk
    VALUE = "value"                # Undervalued assets
    INCOME = "income"              # Dividend focused
    BALANCED = "balanced"          # Mix of growth and value
    SPECULATIVE = "speculative"    # High risk/reward


@dataclass
class BullCase:
    """Bullish investment thesis."""
    headline: str
    key_drivers: List[str]
    catalysts: List[str]
    target_upside: float          # Percentage upside potential
    probability: float            # Probability estimate (0-1)
    timeframe: str


@dataclass
class BearCase:
    """Bearish investment thesis."""
    headline: str
    key_risks: List[str]
    triggers: List[str]
    target_downside: float        # Percentage downside risk
    probability: float            # Probability estimate (0-1)
    timeframe: str


@dataclass
class ValuationMetrics:
    """Valuation analysis."""
    current_price: Optional[float] = None
    fair_value_estimate: Optional[float] = None
    upside_potential: Optional[float] = None
    pe_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    price_to_sales: Optional[float] = None
    price_to_book: Optional[float] = None
    peer_average_pe: Optional[float] = None
    dcf_value: Optional[float] = None
    valuation_grade: str = "C"    # A-F


@dataclass
class InvestmentThesis:
    """Complete investment thesis."""
    company_name: str
    recommendation: InvestmentRecommendation
    confidence: float             # 0-100
    target_price: Optional[float]
    current_price: Optional[float]
    upside_potential: Optional[float]
    horizon: InvestmentHorizon
    suitable_for: List[InvestorProfile]

    # Analysis components
    bull_case: BullCase
    bear_case: BearCase
    valuation: ValuationMetrics

    # Key points
    investment_highlights: List[str]
    key_risks: List[str]
    catalysts: List[str]

    # Detailed rationale
    rationale: str
    summary: str


class InvestmentThesisGenerator:
    """Generates investment thesis from research data."""

    # Recommendation thresholds
    RECOMMENDATION_THRESHOLDS = {
        InvestmentRecommendation.STRONG_BUY: {"min_upside": 30, "max_risk": 30},
        InvestmentRecommendation.BUY: {"min_upside": 15, "max_risk": 50},
        InvestmentRecommendation.HOLD: {"min_upside": -10, "max_risk": 70},
        InvestmentRecommendation.SELL: {"min_upside": -25, "max_risk": 80},
        InvestmentRecommendation.STRONG_SELL: {"min_upside": -100, "max_risk": 100},
    }

    def __init__(
        self,
        risk_tolerance: str = "moderate",
        default_horizon: InvestmentHorizon = InvestmentHorizon.MEDIUM_TERM
    ):
        """Initialize the thesis generator."""
        self.risk_tolerance = risk_tolerance
        self.default_horizon = default_horizon

    def generate_thesis(
        self,
        company_name: str,
        company_data: Dict[str, Any],
        financial_data: Optional[Dict[str, Any]] = None,
        market_data: Optional[Dict[str, Any]] = None,
        risk_assessment: Optional[Dict[str, Any]] = None
    ) -> InvestmentThesis:
        """
        Generate comprehensive investment thesis.

        Args:
            company_name: Name of the company
            company_data: General company information
            financial_data: Financial metrics and performance
            market_data: Market position and competitive data
            risk_assessment: Risk analysis results

        Returns:
            InvestmentThesis with recommendation and analysis
        """
        logger.info(f"Generating investment thesis for {company_name}")

        financial_data = financial_data or {}
        market_data = market_data or {}
        risk_assessment = risk_assessment or {}

        # Build valuation metrics
        valuation = self._analyze_valuation(financial_data, market_data)

        # Generate bull case
        bull_case = self._generate_bull_case(
            company_data, financial_data, market_data
        )

        # Generate bear case
        bear_case = self._generate_bear_case(
            company_data, financial_data, risk_assessment
        )

        # Calculate upside potential
        upside = self._calculate_upside(valuation, bull_case, bear_case)

        # Determine recommendation
        risk_score = risk_assessment.get("overall_risk_score", 50)
        recommendation = self._determine_recommendation(upside, risk_score)

        # Calculate confidence
        confidence = self._calculate_confidence(
            financial_data, market_data, risk_assessment
        )

        # Identify suitable investor profiles
        suitable_for = self._identify_suitable_investors(
            upside, risk_score, financial_data
        )

        # Extract investment highlights
        highlights = self._extract_highlights(
            company_data, financial_data, market_data
        )

        # Extract key risks
        key_risks = self._extract_key_risks(risk_assessment)

        # Identify catalysts
        catalysts = self._identify_catalysts(
            company_data, market_data, bull_case
        )

        # Generate rationale
        rationale = self._generate_rationale(
            company_name, recommendation, upside, highlights, key_risks
        )

        # Generate summary
        summary = self._generate_summary(
            company_name, recommendation, upside, confidence
        )

        return InvestmentThesis(
            company_name=company_name,
            recommendation=recommendation,
            confidence=confidence,
            target_price=valuation.fair_value_estimate,
            current_price=valuation.current_price,
            upside_potential=upside,
            horizon=self.default_horizon,
            suitable_for=suitable_for,
            bull_case=bull_case,
            bear_case=bear_case,
            valuation=valuation,
            investment_highlights=highlights,
            key_risks=key_risks,
            catalysts=catalysts,
            rationale=rationale,
            summary=summary
        )

    def _analyze_valuation(
        self,
        financial_data: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> ValuationMetrics:
        """Analyze company valuation."""
        current_price = financial_data.get("stock_price") or financial_data.get("current_price")
        pe_ratio = financial_data.get("pe_ratio")
        ev_ebitda = financial_data.get("ev_ebitda")
        price_to_sales = financial_data.get("price_to_sales")
        price_to_book = financial_data.get("price_to_book")

        # Estimate fair value
        fair_value = None
        if pe_ratio and financial_data.get("earnings_per_share"):
            eps = financial_data["earnings_per_share"]
            # Use industry average P/E if available
            target_pe = market_data.get("peer_average_pe", pe_ratio * 1.1)
            fair_value = eps * target_pe

        # Calculate upside potential
        upside = None
        if current_price and fair_value:
            upside = ((fair_value - current_price) / current_price) * 100

        # Determine valuation grade
        grade = self._grade_valuation(pe_ratio, ev_ebitda, price_to_sales)

        return ValuationMetrics(
            current_price=current_price,
            fair_value_estimate=fair_value,
            upside_potential=upside,
            pe_ratio=pe_ratio,
            ev_ebitda=ev_ebitda,
            price_to_sales=price_to_sales,
            price_to_book=price_to_book,
            peer_average_pe=market_data.get("peer_average_pe"),
            valuation_grade=grade
        )

    def _grade_valuation(
        self,
        pe_ratio: Optional[float],
        ev_ebitda: Optional[float],
        price_to_sales: Optional[float]
    ) -> str:
        """Grade valuation attractiveness."""
        score = 0
        count = 0

        if pe_ratio is not None:
            if pe_ratio < 15:
                score += 4
            elif pe_ratio < 25:
                score += 3
            elif pe_ratio < 35:
                score += 2
            else:
                score += 1
            count += 1

        if ev_ebitda is not None:
            if ev_ebitda < 8:
                score += 4
            elif ev_ebitda < 12:
                score += 3
            elif ev_ebitda < 18:
                score += 2
            else:
                score += 1
            count += 1

        if price_to_sales is not None:
            if price_to_sales < 2:
                score += 4
            elif price_to_sales < 5:
                score += 3
            elif price_to_sales < 10:
                score += 2
            else:
                score += 1
            count += 1

        if count == 0:
            return "NR"  # Not Rated

        avg_score = score / count
        if avg_score >= 3.5:
            return "A"
        elif avg_score >= 2.5:
            return "B"
        elif avg_score >= 1.5:
            return "C"
        else:
            return "D"

    def _generate_bull_case(
        self,
        company_data: Dict[str, Any],
        financial_data: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> BullCase:
        """Generate bullish investment thesis."""
        drivers = []
        catalysts = []

        # Analyze growth
        revenue_growth = financial_data.get("revenue_growth", 0)
        if revenue_growth > 10:
            drivers.append(f"Strong revenue growth ({revenue_growth:.1f}%)")
            catalysts.append("Continued market expansion")

        # Analyze market position
        market_share = market_data.get("market_share", 0)
        if market_share > 15:
            drivers.append(f"Market leadership ({market_share:.1f}% share)")

        # Analyze profitability
        profit_margin = financial_data.get("profit_margin", 0)
        if profit_margin > 15:
            drivers.append(f"Strong profitability ({profit_margin:.1f}% margin)")

        # Industry tailwinds
        market_growth = market_data.get("market_growth", 0)
        if market_growth > 5:
            drivers.append(f"Growing market ({market_growth:.1f}% industry growth)")
            catalysts.append("Industry tailwinds supporting growth")

        # Default drivers if none found
        if not drivers:
            drivers = [
                "Potential for operational improvement",
                "Market consolidation opportunities"
            ]

        if not catalysts:
            catalysts = [
                "New product launches",
                "Market expansion initiatives"
            ]

        # Calculate potential upside
        upside = min(50, revenue_growth * 2 + market_share * 0.5)

        return BullCase(
            headline=f"Growth story with {upside:.0f}% upside potential",
            key_drivers=drivers[:4],
            catalysts=catalysts[:3],
            target_upside=upside,
            probability=0.4,  # Base probability
            timeframe="12-24 months"
        )

    def _generate_bear_case(
        self,
        company_data: Dict[str, Any],
        financial_data: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> BearCase:
        """Generate bearish investment thesis."""
        risks = []
        triggers = []

        # Analyze financial risks
        debt_equity = financial_data.get("debt_to_equity", 0)
        if debt_equity > 1.5:
            risks.append(f"High leverage (D/E: {debt_equity:.1f})")
            triggers.append("Rising interest rates impact")

        # Revenue decline
        revenue_growth = financial_data.get("revenue_growth", 0)
        if revenue_growth < 0:
            risks.append(f"Revenue decline ({revenue_growth:.1f}%)")
            triggers.append("Continued market share loss")

        # Extract from risk assessment
        key_risks = risk_assessment.get("key_risks", [])
        for risk in key_risks[:2]:
            if isinstance(risk, str):
                risks.append(risk)
            elif isinstance(risk, dict):
                risks.append(risk.get("name", "Unknown risk"))

        # Default risks if none found
        if not risks:
            risks = [
                "Competitive pressure intensification",
                "Economic downturn impact"
            ]

        if not triggers:
            triggers = [
                "Market disruption from new entrants",
                "Regulatory changes"
            ]

        # Calculate potential downside
        risk_score = risk_assessment.get("overall_risk_score", 50)
        downside = min(50, risk_score * 0.6)

        return BearCase(
            headline=f"Risk scenario with {downside:.0f}% downside",
            key_risks=risks[:4],
            triggers=triggers[:3],
            target_downside=downside,
            probability=0.3,
            timeframe="12-18 months"
        )

    def _calculate_upside(
        self,
        valuation: ValuationMetrics,
        bull_case: BullCase,
        bear_case: BearCase
    ) -> float:
        """Calculate expected upside potential."""
        # Start with valuation-based upside
        if valuation.upside_potential is not None:
            base_upside = valuation.upside_potential
        else:
            # Use weighted bull/bear cases
            base_upside = (
                bull_case.target_upside * bull_case.probability -
                bear_case.target_downside * bear_case.probability
            )

        return base_upside

    def _determine_recommendation(
        self,
        upside: float,
        risk_score: float
    ) -> InvestmentRecommendation:
        """Determine investment recommendation."""
        # Adjust upside for risk
        risk_adjusted_upside = upside - (risk_score * 0.3)

        if risk_adjusted_upside >= 25:
            return InvestmentRecommendation.STRONG_BUY
        elif risk_adjusted_upside >= 10:
            return InvestmentRecommendation.BUY
        elif risk_adjusted_upside >= -10:
            return InvestmentRecommendation.HOLD
        elif risk_adjusted_upside >= -25:
            return InvestmentRecommendation.SELL
        else:
            return InvestmentRecommendation.STRONG_SELL

    def _calculate_confidence(
        self,
        financial_data: Dict[str, Any],
        market_data: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> float:
        """Calculate confidence in the recommendation."""
        confidence = 50.0  # Base confidence

        # Data quality factors
        if financial_data.get("pe_ratio"):
            confidence += 10
        if financial_data.get("revenue_growth") is not None:
            confidence += 10
        if market_data.get("market_share"):
            confidence += 10
        if risk_assessment.get("overall_risk_score"):
            confidence += 10

        # Consistency factors
        if risk_assessment.get("risk_grade") in ["A", "B"]:
            confidence += 5

        return min(95, confidence)

    def _identify_suitable_investors(
        self,
        upside: float,
        risk_score: float,
        financial_data: Dict[str, Any]
    ) -> List[InvestorProfile]:
        """Identify suitable investor profiles."""
        suitable = []

        # Growth investors
        if upside > 20 and financial_data.get("revenue_growth", 0) > 10:
            suitable.append(InvestorProfile.GROWTH)

        # Value investors
        if financial_data.get("pe_ratio", 100) < 15:
            suitable.append(InvestorProfile.VALUE)

        # Income investors
        if financial_data.get("dividend_yield", 0) > 3:
            suitable.append(InvestorProfile.INCOME)

        # Balanced investors
        if 30 <= risk_score <= 60:
            suitable.append(InvestorProfile.BALANCED)

        # Speculative investors
        if upside > 40 or risk_score > 70:
            suitable.append(InvestorProfile.SPECULATIVE)

        # Default to balanced
        if not suitable:
            suitable.append(InvestorProfile.BALANCED)

        return suitable

    def _extract_highlights(
        self,
        company_data: Dict[str, Any],
        financial_data: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> List[str]:
        """Extract key investment highlights."""
        highlights = []

        # Market position
        if market_data.get("market_share", 0) > 15:
            highlights.append(
                f"Market leader with {market_data['market_share']:.1f}% share"
            )

        # Growth
        if financial_data.get("revenue_growth", 0) > 10:
            highlights.append(
                f"Strong growth at {financial_data['revenue_growth']:.1f}% annually"
            )

        # Profitability
        if financial_data.get("profit_margin", 0) > 15:
            highlights.append(
                f"High profitability with {financial_data['profit_margin']:.1f}% margins"
            )

        # Valuation
        if financial_data.get("pe_ratio") and financial_data["pe_ratio"] < 20:
            highlights.append(
                f"Attractive valuation at {financial_data['pe_ratio']:.1f}x P/E"
            )

        # Company strengths
        strengths = company_data.get("strengths", [])
        for strength in strengths[:2]:
            highlights.append(strength)

        # Default highlights
        if not highlights:
            highlights = [
                "Established market presence",
                "Diversified business model"
            ]

        return highlights[:5]

    def _extract_key_risks(self, risk_assessment: Dict[str, Any]) -> List[str]:
        """Extract key investment risks."""
        risks = risk_assessment.get("key_risks", [])

        if not risks:
            risks = [
                "Market competition intensification",
                "Economic downturn sensitivity",
                "Regulatory environment changes"
            ]

        # Ensure string format
        formatted = []
        for risk in risks[:5]:
            if isinstance(risk, str):
                formatted.append(risk)
            elif isinstance(risk, dict):
                formatted.append(risk.get("name", str(risk)))
            else:
                formatted.append(str(risk))

        return formatted

    def _identify_catalysts(
        self,
        company_data: Dict[str, Any],
        market_data: Dict[str, Any],
        bull_case: BullCase
    ) -> List[str]:
        """Identify potential stock catalysts."""
        catalysts = list(bull_case.catalysts)

        # Market catalysts
        if market_data.get("market_growth", 0) > 5:
            catalysts.append("Industry tailwinds and market expansion")

        # Company-specific catalysts
        if company_data.get("upcoming_products"):
            catalysts.append("New product launches")

        if company_data.get("expansion_plans"):
            catalysts.append("Geographic or market expansion")

        # Generic catalysts
        if len(catalysts) < 3:
            catalysts.extend([
                "Earnings beats and guidance raises",
                "Strategic partnerships or acquisitions"
            ])

        return list(dict.fromkeys(catalysts))[:5]  # Deduplicate

    def _generate_rationale(
        self,
        company_name: str,
        recommendation: InvestmentRecommendation,
        upside: float,
        highlights: List[str],
        risks: List[str]
    ) -> str:
        """Generate detailed investment rationale."""
        rec_text = {
            InvestmentRecommendation.STRONG_BUY: "Strong Buy",
            InvestmentRecommendation.BUY: "Buy",
            InvestmentRecommendation.HOLD: "Hold",
            InvestmentRecommendation.SELL: "Sell",
            InvestmentRecommendation.STRONG_SELL: "Strong Sell",
            InvestmentRecommendation.NOT_RATED: "Not Rated"
        }

        parts = [
            f"We rate {company_name} as {rec_text[recommendation]} "
            f"with an expected upside of {upside:.1f}%.",
            "",
            "Investment Highlights:",
        ]

        for highlight in highlights[:3]:
            parts.append(f"• {highlight}")

        parts.append("")
        parts.append("Key Risks to Monitor:")
        for risk in risks[:3]:
            parts.append(f"• {risk}")

        return "\n".join(parts)

    def _generate_summary(
        self,
        company_name: str,
        recommendation: InvestmentRecommendation,
        upside: float,
        confidence: float
    ) -> str:
        """Generate executive summary."""
        rec_text = recommendation.value.replace("_", " ").title()

        return (
            f"Investment Thesis: {rec_text} on {company_name} with "
            f"{upside:.1f}% upside potential. Confidence: {confidence:.0f}%."
        )


def create_thesis_generator(
    risk_tolerance: str = "moderate",
    horizon: InvestmentHorizon = InvestmentHorizon.MEDIUM_TERM
) -> InvestmentThesisGenerator:
    """Factory function to create InvestmentThesisGenerator."""
    return InvestmentThesisGenerator(
        risk_tolerance=risk_tolerance,
        default_horizon=horizon
    )
