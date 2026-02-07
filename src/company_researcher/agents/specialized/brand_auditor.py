"""
Brand Auditor Agent (Phase 14.1).

Brand analysis capabilities:
- Brand perception analysis
- Brand consistency evaluation
- Messaging effectiveness
- Visual identity assessment
- Brand equity estimation
- Reputation monitoring

This agent analyzes company brand strength and market perception.

Refactored to use BaseSpecialistAgent for:
- Reduced code duplication
- Consistent agent interface
- Centralized LLM calling and cost tracking
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from ...config import get_config
from ...llm.client_factory import calculate_cost
from ...state import OverallState
from ...types import BrandHealth, BrandStrength, SentimentCategory  # Centralized enums
from ..base import create_empty_result, get_agent_logger
from ..base.specialist import BaseSpecialistAgent, ParsingMixin

# ============================================================================
# Data Models
# ============================================================================
# Note: BrandStrength, BrandHealth, SentimentCategory imported from types.py


@dataclass
class BrandMetric:
    """A brand metric measurement."""

    name: str
    score: float  # 0-100
    benchmark: float = 50.0
    trend: str = "stable"  # improving, stable, declining
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "score": round(self.score, 1),
            "benchmark": self.benchmark,
            "trend": self.trend,
            "notes": self.notes,
        }


@dataclass
class BrandAttribute:
    """A brand attribute with perception data."""

    attribute: str
    strength: float  # 0-100
    relevance: float  # 0-100
    differentiation: float  # 0-100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attribute": self.attribute,
            "strength": round(self.strength, 1),
            "relevance": round(self.relevance, 1),
            "differentiation": round(self.differentiation, 1),
        }


@dataclass
class BrandAuditResult:
    """Complete brand audit result."""

    company_name: str
    overall_strength: BrandStrength = BrandStrength.MODERATE
    brand_score: float = 50.0
    metrics: List[BrandMetric] = field(default_factory=list)
    attributes: List[BrandAttribute] = field(default_factory=list)
    sentiment: SentimentCategory = SentimentCategory.NEUTRAL
    key_messages: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    analysis: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_name": self.company_name,
            "overall_strength": self.overall_strength.value,
            "brand_score": round(self.brand_score, 1),
            "metrics": [m.to_dict() for m in self.metrics],
            "attributes": [a.to_dict() for a in self.attributes],
            "sentiment": self.sentiment.value,
            "key_messages": self.key_messages,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendations": self.recommendations,
        }


# ============================================================================
# Prompts
# ============================================================================

BRAND_AUDIT_PROMPT = """You are an expert brand strategist conducting a comprehensive brand audit.

**COMPANY:** {company_name}

**AVAILABLE DATA:**
{search_results}

**TASK:** Perform a detailed brand audit analysis.

**STRUCTURE YOUR ANALYSIS:**

### 1. Brand Overview
- **Brand Name:** {company_name}
- **Brand Positioning:** [How the brand positions itself]
- **Target Audience:** [Primary target segments]
- **Brand Promise:** [Core value proposition]

### 2. Brand Perception Metrics
Rate each on a scale of 0-100:

| Metric | Score | Trend | Notes |
|--------|-------|-------|-------|
| Brand Awareness | [0-100] | [↑/→/↓] | [Brief note] |
| Brand Recall | [0-100] | [↑/→/↓] | [Brief note] |
| Brand Loyalty | [0-100] | [↑/→/↓] | [Brief note] |
| Brand Trust | [0-100] | [↑/→/↓] | [Brief note] |
| Brand Relevance | [0-100] | [↑/→/↓] | [Brief note] |

### 3. Brand Attributes Analysis
Key attributes associated with the brand:

| Attribute | Strength (0-100) | Relevance | Differentiation |
|-----------|------------------|-----------|-----------------|
| [Attribute 1] | [Score] | [HIGH/MED/LOW] | [HIGH/MED/LOW] |
| [Attribute 2] | [Score] | [HIGH/MED/LOW] | [HIGH/MED/LOW] |
...

### 4. Brand Sentiment Analysis
- **Overall Sentiment:** [POSITIVE/NEUTRAL/NEGATIVE/MIXED]
- **Sentiment Breakdown:**
  - Positive themes: [List]
  - Negative themes: [List]
  - Common praise: [List]
  - Common complaints: [List]

### 5. Messaging Effectiveness
**Key Brand Messages:**
1. [Message 1] - Clarity: [HIGH/MED/LOW], Impact: [HIGH/MED/LOW]
2. [Message 2] - ...

**Message Consistency:** [CONSISTENT/INCONSISTENT]

### 6. Competitive Brand Position
How the brand compares to competitors:
- **Differentiation:** [What makes this brand unique]
- **Brand Gap:** [Where competitors are stronger]
- **Opportunity:** [Untapped brand positioning]

### 7. Brand Strengths
1. [Strength 1]
2. [Strength 2]
...

### 8. Brand Weaknesses
1. [Weakness 1]
2. [Weakness 2]
...

### 9. Overall Brand Score
**Brand Score:** [0-100]
**Brand Strength:** [DOMINANT/STRONG/MODERATE/WEAK/EMERGING]

### 10. Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
...

**REQUIREMENTS:**
- Base assessments on available data
- Be objective and balanced
- Provide specific, actionable recommendations
- Note data limitations if any

Begin your brand audit:"""


# ============================================================================
# Brand Auditor Agent
# ============================================================================


class BrandAuditorAgent(BaseSpecialistAgent[BrandAuditResult], ParsingMixin):
    """
    Brand Auditor Agent for comprehensive brand analysis.

    Inherits from:
    - BaseSpecialistAgent: Common agent functionality (LLM calls, formatting, cost tracking)
    - ParsingMixin: Standardized extraction methods

    Analyzes:
    - Brand perception and awareness
    - Brand attributes and associations
    - Sentiment and reputation
    - Messaging effectiveness
    - Competitive positioning

    Usage:
        agent = BrandAuditorAgent()
        result = agent.analyze(  # Note: use analyze() from base class
            company_name="Tesla",
            search_results=results
        )
    """

    # Class attributes for BaseSpecialistAgent
    agent_name = "brand_auditor"

    def _get_prompt(self, company_name: str, formatted_results: str) -> str:
        """Build the brand audit prompt."""
        return BRAND_AUDIT_PROMPT.format(
            company_name=company_name, search_results=formatted_results
        )

    def _parse_analysis(self, company_name: str, analysis: str) -> BrandAuditResult:
        """Parse LLM analysis into structured result using ParsingMixin methods."""
        result = BrandAuditResult(company_name=company_name)

        # Extract metrics from table using ParsingMixin
        result.metrics = self._extract_metrics(analysis)

        # Extract attributes (custom logic for brand-specific attributes)
        result.attributes = self._extract_attributes(analysis)

        # Extract sentiment using ParsingMixin.extract_sentiment
        sentiment_str = self.extract_sentiment(analysis)
        result.sentiment = (
            SentimentCategory(sentiment_str)
            if sentiment_str in ["positive", "negative", "neutral", "mixed"]
            else SentimentCategory.NEUTRAL
        )

        # Extract lists using ParsingMixin.extract_list_items
        result.strengths = self.extract_list_items(analysis, "Strength")
        result.weaknesses = self.extract_list_items(analysis, "Weakness")
        result.recommendations = self.extract_list_items(analysis, "Recommendation")
        result.key_messages = self.extract_list_items(analysis, "Message")

        # Extract overall score using ParsingMixin.extract_score
        result.brand_score = self.extract_score(analysis, "Brand Score")
        result.overall_strength = self._determine_strength(result.brand_score)

        return result

    def _extract_metrics(self, analysis: str) -> List[BrandMetric]:
        """Extract brand metrics from analysis using ParsingMixin."""
        metric_names = [
            "Brand Awareness",
            "Brand Recall",
            "Brand Loyalty",
            "Brand Trust",
            "Brand Relevance",
        ]

        # Use ParsingMixin.extract_metrics_table for standardized extraction
        metrics_dict = self.extract_metrics_table(analysis, metric_names)

        # Convert dict to BrandMetric objects
        metrics = []
        for name, data in metrics_dict.items():
            metrics.append(BrandMetric(name=name, score=data["score"], trend=data["trend"]))

        return metrics

    def _extract_attributes(self, analysis: str) -> List[BrandAttribute]:
        """Extract brand attributes from analysis."""
        attributes = []

        # Look for common brand attributes
        attribute_keywords = [
            "innovative",
            "reliable",
            "premium",
            "affordable",
            "sustainable",
            "trustworthy",
            "modern",
            "traditional",
        ]

        for keyword in attribute_keywords:
            if keyword.lower() in analysis.lower():
                # Estimate scores based on context
                strength = 60 if keyword in analysis else 40
                attributes.append(
                    BrandAttribute(
                        attribute=keyword.capitalize(),
                        strength=strength,
                        relevance=70,
                        differentiation=50,
                    )
                )

        return attributes[:5]

    # NOTE: _extract_sentiment, _extract_list_section, _extract_score methods
    # are now provided by ParsingMixin (extract_sentiment, extract_list_items, extract_score)

    def _determine_strength(self, score: float) -> BrandStrength:
        """Determine brand strength from score."""
        if score >= 80:
            return BrandStrength.DOMINANT
        elif score >= 65:
            return BrandStrength.STRONG
        elif score >= 45:
            return BrandStrength.MODERATE
        elif score >= 30:
            return BrandStrength.EMERGING
        else:
            return BrandStrength.WEAK

    # Backwards compatibility alias
    def audit(self, company_name: str, search_results: List[Dict[str, Any]]) -> BrandAuditResult:
        """
        Perform brand audit (alias for analyze()).

        Deprecated: Use analyze() instead for consistency with other agents.
        """
        return self.analyze(company_name, search_results)


# ============================================================================
# Agent Node Function
# ============================================================================


def brand_auditor_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Brand Auditor Agent Node for workflow integration.

    Args:
        state: Current workflow state

    Returns:
        State update with brand audit results
    """
    logger = get_agent_logger("brand_auditor")
    config = get_config()
    company_name = state["company_name"]
    search_results = state.get("search_results", [])

    with logger.agent_run(company_name):
        if not search_results:
            logger.no_data()
            return create_empty_result("brand")

        logger.analyzing(len(search_results))

        # Run brand audit using base class analyze() method
        agent = BrandAuditorAgent(config)
        result = agent.analyze(company_name=company_name, search_results=search_results)

        # Calculate cost
        cost = calculate_cost(500, 1500)  # Estimated

        logger.info(f"Brand Score: {result.brand_score}")
        logger.info(f"Strength: {result.overall_strength.value}")
        logger.info(f"Sentiment: {result.sentiment.value}")
        logger.complete(cost=cost)

        return {
            "agent_outputs": {
                "brand": {**result.to_dict(), "analysis": result.analysis, "cost": cost}
            },
            "total_cost": cost,
        }


# ============================================================================
# Factory Function
# ============================================================================


def create_brand_auditor() -> BrandAuditorAgent:
    """Create a Brand Auditor Agent instance."""
    return BrandAuditorAgent()
