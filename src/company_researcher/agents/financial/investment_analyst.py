"""
Investment Analyst Agent (Phase 15.2).

Investment-focused analysis capabilities:
- Investment thesis generation
- Risk assessment
- Valuation analysis
- Growth potential evaluation
- Competitive moat analysis
- Exit opportunity assessment

This agent generates investment-grade analysis for due diligence.

Note: This is a "meta-agent" that synthesizes outputs from other agents,
so it has a different interface than standard specialist agents.
It uses ParsingMixin for standardized extraction but doesn't inherit from
BaseSpecialistAgent due to its different input signature.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from ...config import get_config
from ...llm.client_factory import calculate_cost, get_anthropic_client, safe_extract_text
from ...state import OverallState
from ...types import GrowthStage, InvestmentRating, MoatStrength, RiskLevel  # Centralized enums
from ..base import create_empty_result, get_agent_logger
from ..base.specialist import ParsingMixin

# ============================================================================
# Data Models
# ============================================================================
# Note: InvestmentRating, RiskLevel, MoatStrength, GrowthStage imported from types.py


@dataclass
class RiskFactor:
    """An identified risk factor."""

    category: str  # Market, Financial, Operational, Regulatory, etc.
    description: str
    severity: RiskLevel
    likelihood: str  # HIGH/MEDIUM/LOW
    mitigation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "description": self.description,
            "severity": self.severity.value,
            "likelihood": self.likelihood,
            "mitigation": self.mitigation,
        }


@dataclass
class GrowthDriver:
    """A growth driver for the company."""

    driver: str
    impact: str  # HIGH/MEDIUM/LOW
    timeline: str  # SHORT/MEDIUM/LONG term
    confidence: str  # HIGH/MEDIUM/LOW
    evidence: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "driver": self.driver,
            "impact": self.impact,
            "timeline": self.timeline,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }


@dataclass
class ValuationMetric:
    """A valuation metric."""

    metric: str
    value: str
    benchmark: str
    assessment: str  # UNDERVALUED/FAIR/OVERVALUED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric": self.metric,
            "value": self.value,
            "benchmark": self.benchmark,
            "assessment": self.assessment,
        }


@dataclass
class InvestmentAnalysisResult:
    """Complete investment analysis result."""

    company_name: str
    investment_rating: InvestmentRating = InvestmentRating.HOLD
    overall_risk: RiskLevel = RiskLevel.MODERATE
    moat_strength: MoatStrength = MoatStrength.NARROW
    growth_stage: GrowthStage = GrowthStage.GROWTH
    investment_thesis: str = ""
    bull_case: List[str] = field(default_factory=list)
    bear_case: List[str] = field(default_factory=list)
    risk_factors: List[RiskFactor] = field(default_factory=list)
    growth_drivers: List[GrowthDriver] = field(default_factory=list)
    valuation_metrics: List[ValuationMetric] = field(default_factory=list)
    moat_sources: List[str] = field(default_factory=list)
    key_metrics_to_watch: List[str] = field(default_factory=list)
    catalysts: List[str] = field(default_factory=list)
    exit_opportunities: List[str] = field(default_factory=list)
    recommendation: str = ""
    analysis: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_name": self.company_name,
            "investment_rating": self.investment_rating.value,
            "overall_risk": self.overall_risk.value,
            "moat_strength": self.moat_strength.value,
            "growth_stage": self.growth_stage.value,
            "investment_thesis": self.investment_thesis,
            "bull_case": self.bull_case,
            "bear_case": self.bear_case,
            "risk_factors": [r.to_dict() for r in self.risk_factors],
            "growth_drivers": [g.to_dict() for g in self.growth_drivers],
            "valuation_metrics": [v.to_dict() for v in self.valuation_metrics],
            "moat_sources": self.moat_sources,
            "catalysts": self.catalysts,
            "exit_opportunities": self.exit_opportunities,
            "recommendation": self.recommendation,
        }


# ============================================================================
# Prompts
# ============================================================================

INVESTMENT_ANALYSIS_PROMPT = """You are an expert investment analyst performing due diligence on a company.

**TARGET COMPANY:** {company_name}

**AVAILABLE DATA:**
{research_data}

**TASK:** Generate comprehensive investment analysis suitable for institutional due diligence.

**STRUCTURE YOUR ANALYSIS:**

### 1. Investment Thesis
Write a concise (2-3 paragraph) investment thesis covering:
- Why this company is/isn't investment worthy
- Key value drivers
- Risk/reward assessment

### 2. Investment Rating
- **Rating:** [STRONG_BUY/BUY/HOLD/SELL/AVOID]
- **Confidence:** [HIGH/MEDIUM/LOW]
- **Time Horizon:** [1-3 years / 3-5 years / 5+ years]
- **Rationale:** [Brief explanation]

### 3. Growth Assessment
- **Growth Stage:** [HYPERGROWTH/HIGH_GROWTH/GROWTH/MATURE/DECLINING]
- **Revenue Growth:** [Estimated %]
- **Market Growth:** [Estimated %]

**Growth Drivers:**
| Driver | Impact | Timeline | Confidence | Evidence |
|--------|--------|----------|------------|----------|
| [Driver 1] | [H/M/L] | [S/M/L] | [H/M/L] | [Evidence] |
...

### 4. Competitive Moat Analysis
- **Moat Strength:** [WIDE/NARROW/NONE]
- **Moat Sources:**
  - [Source 1]: [Description]
  - [Source 2]: [Description]
- **Moat Sustainability:** [Analysis]

### 5. Risk Assessment
- **Overall Risk Level:** [VERY_HIGH/HIGH/MODERATE/LOW/VERY_LOW]

**Risk Factors:**
| Category | Risk | Severity | Likelihood | Mitigation |
|----------|------|----------|------------|------------|
| Market | [Description] | [Level] | [H/M/L] | [Strategy] |
| Financial | [Description] | [Level] | [H/M/L] | [Strategy] |
| Operational | [Description] | [Level] | [H/M/L] | [Strategy] |
| Regulatory | [Description] | [Level] | [H/M/L] | [Strategy] |
| Competitive | [Description] | [Level] | [H/M/L] | [Strategy] |

### 6. Valuation Perspective
| Metric | Value | Benchmark | Assessment |
|--------|-------|-----------|------------|
| P/E or P/S | [Value] | [Industry avg] | [UNDER/FAIR/OVER] |
| EV/Revenue | [Value] | [Industry avg] | [UNDER/FAIR/OVER] |
| Growth-adjusted | [Value] | [Benchmark] | [UNDER/FAIR/OVER] |

### 7. Bull Case
Top reasons the investment could outperform:
1. [Bull point 1]
2. [Bull point 2]
3. [Bull point 3]

### 8. Bear Case
Top risks that could cause underperformance:
1. [Bear point 1]
2. [Bear point 2]
3. [Bear point 3]

### 9. Catalysts
Upcoming events that could move the stock/valuation:
1. [Catalyst 1] - Timeline: [When]
2. [Catalyst 2] - Timeline: [When]

### 10. Key Metrics to Watch
Metrics investors should monitor:
1. [Metric 1] - Current: [Value], Target: [Value]
2. [Metric 2] - Current: [Value], Target: [Value]

### 11. Exit Opportunities (for private investments)
Potential exit paths:
1. [Exit 1]: [Description and timeline]
2. [Exit 2]: [Description and timeline]

### 12. Recommendation
Final investment recommendation with specific action items.

**REQUIREMENTS:**
- Be objective and balanced
- Support conclusions with data
- Quantify where possible
- Address both upside and downside
- Consider multiple scenarios

Begin your investment analysis:"""


# ============================================================================
# Investment Analyst Agent
# ============================================================================


class InvestmentAnalystAgent(ParsingMixin):
    """
    Investment Analyst Agent for due diligence.

    Inherits from:
    - ParsingMixin: Standardized extraction methods

    Note: This is a "meta-agent" with a different interface than standard
    specialist agents (takes research_data dict instead of search_results list).

    Generates:
    - Investment thesis
    - Risk assessment
    - Valuation analysis
    - Growth evaluation
    - Moat analysis

    Usage:
        agent = InvestmentAnalystAgent()
        result = agent.analyze(
            company_name="Tesla",
            research_data=data
        )
    """

    def __init__(self, config=None):
        """Initialize agent."""
        self._config = config or get_config()
        self._client = get_anthropic_client()

    def analyze(self, company_name: str, research_data: Dict[str, Any]) -> InvestmentAnalysisResult:
        """
        Perform investment analysis.

        Args:
            company_name: Target company
            research_data: Research data from other agents

        Returns:
            InvestmentAnalysisResult
        """
        formatted_data = self._format_research_data(research_data)

        prompt = INVESTMENT_ANALYSIS_PROMPT.format(
            company_name=company_name, research_data=formatted_data
        )

        response = self._client.messages.create(
            model=self._config.llm_model,
            max_tokens=self._config.investment_analyst_max_tokens,
            temperature=self._config.investment_analyst_temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        analysis = safe_extract_text(response, agent_name="investment_analyst")
        cost = calculate_cost(response.usage.input_tokens, response.usage.output_tokens)

        result = self._parse_analysis(company_name, analysis)
        result.analysis = analysis

        return result

    def _format_research_data(self, data: Dict[str, Any]) -> str:
        """Format research data for prompt."""
        sections = []

        for key, value in data.items():
            if isinstance(value, dict):
                if "analysis" in value:
                    sections.append(f"**{key.upper()}:**\n{value['analysis'][:1200]}")
                else:
                    sections.append(f"**{key.upper()}:**\n{str(value)[:600]}")
            elif isinstance(value, str):
                sections.append(f"**{key.upper()}:**\n{value[:1200]}")

        return "\n\n".join(sections[:10]) if sections else "Limited data available"

    def _parse_analysis(self, company_name: str, analysis: str) -> InvestmentAnalysisResult:
        """Parse analysis into structured result."""
        result = InvestmentAnalysisResult(company_name=company_name)

        # Extract investment rating
        result.investment_rating = self._extract_rating(analysis)

        # Extract risk level
        result.overall_risk = self._extract_risk_level(analysis)

        # Extract moat strength
        result.moat_strength = self._extract_moat_strength(analysis)

        # Extract growth stage
        result.growth_stage = self._extract_growth_stage(analysis)

        # Extract thesis
        result.investment_thesis = self._extract_thesis(analysis)

        # Extract lists
        result.bull_case = self._extract_case(analysis, "Bull")
        result.bear_case = self._extract_case(analysis, "Bear")
        result.moat_sources = self._extract_list(analysis, "Moat Source")
        result.catalysts = self._extract_list(analysis, "Catalyst")
        result.exit_opportunities = self._extract_list(analysis, "Exit")
        result.key_metrics_to_watch = self._extract_list(analysis, "Metric")

        # Extract risk factors
        result.risk_factors = self._extract_risk_factors(analysis)

        # Extract growth drivers
        result.growth_drivers = self._extract_growth_drivers(analysis)

        # Extract recommendation
        result.recommendation = self._extract_recommendation(analysis)

        return result

    def _extract_rating(self, analysis: str) -> InvestmentRating:
        """Extract investment rating."""
        analysis_upper = analysis.upper()

        if "STRONG_BUY" in analysis_upper or "STRONG BUY" in analysis_upper:
            return InvestmentRating.STRONG_BUY
        elif "BUY" in analysis_upper and "RATING" in analysis_upper:
            return InvestmentRating.BUY
        elif "SELL" in analysis_upper:
            return InvestmentRating.SELL
        elif "AVOID" in analysis_upper:
            return InvestmentRating.AVOID

        return InvestmentRating.HOLD

    def _extract_risk_level(self, analysis: str) -> RiskLevel:
        """Extract overall risk level."""
        analysis_upper = analysis.upper()

        if "VERY HIGH" in analysis_upper and "RISK" in analysis_upper:
            return RiskLevel.VERY_HIGH
        elif "HIGH" in analysis_upper and "RISK" in analysis_upper:
            return RiskLevel.HIGH
        elif "LOW" in analysis_upper and "RISK" in analysis_upper:
            return RiskLevel.LOW
        elif "VERY LOW" in analysis_upper:
            return RiskLevel.VERY_LOW

        return RiskLevel.MODERATE

    def _extract_moat_strength(self, analysis: str) -> MoatStrength:
        """Extract moat strength."""
        analysis_upper = analysis.upper()

        if "WIDE" in analysis_upper and "MOAT" in analysis_upper:
            return MoatStrength.WIDE
        elif "NARROW" in analysis_upper and "MOAT" in analysis_upper:
            return MoatStrength.NARROW
        elif "NO MOAT" in analysis_upper or "NONE" in analysis_upper:
            return MoatStrength.NONE

        return MoatStrength.NARROW

    def _extract_growth_stage(self, analysis: str) -> GrowthStage:
        """Extract growth stage."""
        analysis_upper = analysis.upper()

        if "HYPERGROWTH" in analysis_upper:
            return GrowthStage.HYPERGROWTH
        elif "HIGH_GROWTH" in analysis_upper or "HIGH GROWTH" in analysis_upper:
            return GrowthStage.HIGH_GROWTH
        elif "MATURE" in analysis_upper:
            return GrowthStage.MATURE
        elif "DECLINING" in analysis_upper:
            return GrowthStage.DECLINING

        return GrowthStage.GROWTH

    def _extract_thesis(self, analysis: str) -> str:
        """Extract investment thesis using ParsingMixin."""
        # Use ParsingMixin.extract_section for standardized extraction
        result = self.extract_section(analysis, "Investment Thesis", max_length=1000)
        return result if result else "Investment thesis not available"

    def _extract_case(self, analysis: str, case_type: str) -> List[str]:
        """Extract bull or bear case points."""
        points = []
        if f"{case_type} Case" in analysis:
            start = analysis.find(f"{case_type} Case")
            section = analysis[start : start + 800]
            lines = section.split("\n")
            for line in lines[1:]:
                if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "-", "•")):
                    point = line.strip().lstrip("0123456789.-•* ").strip()
                    if point and len(point) > 10:
                        points.append(point[:150])
                elif line.strip().startswith("##"):
                    break
        return points[:5]

    def _extract_list(self, analysis: str, keyword: str) -> List[str]:
        """Extract items near a keyword using ParsingMixin."""
        # Use ParsingMixin.extract_list_items for standardized extraction
        return self.extract_list_items(analysis, keyword, max_items=5)

    def _extract_risk_factors(self, analysis: str) -> List[RiskFactor]:
        """Extract risk factors."""
        factors = []
        categories = ["Market", "Financial", "Operational", "Regulatory", "Competitive"]

        for cat in categories:
            if cat in analysis:
                factors.append(
                    RiskFactor(
                        category=cat,
                        description=f"{cat} risk identified",
                        severity=RiskLevel.MODERATE,
                        likelihood="MEDIUM",
                        mitigation="Monitor closely",
                    )
                )

        return factors[:5]

    def _extract_growth_drivers(self, analysis: str) -> List[GrowthDriver]:
        """Extract growth drivers."""
        drivers = []

        if "Growth Driver" in analysis or "Driver" in analysis:
            lines = analysis.split("\n")
            for line in lines:
                if "driver" in line.lower() and "|" not in line:
                    cleaned = line.strip().lstrip("0123456789.-•* ").strip()
                    if cleaned and len(cleaned) > 10:
                        drivers.append(
                            GrowthDriver(
                                driver=cleaned[:100],
                                impact="MEDIUM",
                                timeline="MEDIUM",
                                confidence="MEDIUM",
                                evidence="Research data",
                            )
                        )

        return drivers[:5]

    def _extract_recommendation(self, analysis: str) -> str:
        """Extract final recommendation using ParsingMixin."""
        # Use ParsingMixin.extract_section for standardized extraction
        result = self.extract_section(analysis, "Recommendation", max_length=500)
        return result if result else "See full analysis for recommendation"


# ============================================================================
# Agent Node Function
# ============================================================================


def investment_analyst_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Investment Analyst Agent Node.

    Args:
        state: Current workflow state

    Returns:
        State update with investment analysis
    """
    logger = get_agent_logger("investment_analyst")
    config = get_config()
    company_name = state["company_name"]
    agent_outputs = state.get("agent_outputs", {})

    with logger.agent_run(company_name):
        if not agent_outputs:
            logger.no_data()
            return create_empty_result("investment")

        logger.analyzing(len(agent_outputs))

        agent = InvestmentAnalystAgent(config)
        result = agent.analyze(company_name, agent_outputs)
        cost = calculate_cost(700, 2000)

        logger.info(f"Rating: {result.investment_rating.value}")
        logger.info(f"Risk: {result.overall_risk.value}")
        logger.info(f"Moat: {result.moat_strength.value}")
        logger.complete(cost=cost)

        return {
            "agent_outputs": {
                "investment": {**result.to_dict(), "analysis": result.analysis, "cost": cost}
            },
            "total_cost": cost,
        }


# ============================================================================
# Factory Function
# ============================================================================


def create_investment_analyst() -> InvestmentAnalystAgent:
    """Create an Investment Analyst Agent instance."""
    return InvestmentAnalystAgent()
