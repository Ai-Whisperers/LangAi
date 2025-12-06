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
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from anthropic import Anthropic

from ..config import get_config
from ..state import OverallState


# ============================================================================
# Data Models
# ============================================================================

class BrandStrength(str, Enum):
    """Brand strength levels."""
    DOMINANT = "dominant"      # Market-leading brand
    STRONG = "strong"         # Well-recognized
    MODERATE = "moderate"     # Moderate recognition
    WEAK = "weak"            # Low recognition
    EMERGING = "emerging"     # Building brand


class SentimentCategory(str, Enum):
    """Sentiment categories."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


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
            "notes": self.notes
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
            "differentiation": round(self.differentiation, 1)
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
            "recommendations": self.recommendations
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

class BrandAuditorAgent:
    """
    Brand Auditor Agent for comprehensive brand analysis.

    Analyzes:
    - Brand perception and awareness
    - Brand attributes and associations
    - Sentiment and reputation
    - Messaging effectiveness
    - Competitive positioning

    Usage:
        agent = BrandAuditorAgent()
        result = agent.audit(
            company_name="Tesla",
            search_results=results
        )
    """

    def __init__(self, config=None):
        """Initialize agent."""
        self._config = config or get_config()
        self._client = Anthropic(api_key=self._config.anthropic_api_key)

    def audit(
        self,
        company_name: str,
        search_results: List[Dict[str, Any]]
    ) -> BrandAuditResult:
        """
        Perform brand audit.

        Args:
            company_name: Company to audit
            search_results: Search results with brand data

        Returns:
            BrandAuditResult
        """
        # Format search results
        formatted_results = self._format_search_results(search_results)

        prompt = BRAND_AUDIT_PROMPT.format(
            company_name=company_name,
            search_results=formatted_results
        )

        # Call LLM
        response = self._client.messages.create(
            model=self._config.llm_model,
            max_tokens=2000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )

        analysis = response.content[0].text
        cost = self._config.calculate_llm_cost(
            response.usage.input_tokens,
            response.usage.output_tokens
        )

        # Parse analysis into structured result
        result = self._parse_audit_result(company_name, analysis)
        result.analysis = analysis

        return result

    def _format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for prompt."""
        if not results:
            return "No search results available"

        formatted = []
        for i, r in enumerate(results[:10], 1):
            formatted.append(
                f"Source {i}: {r.get('title', 'N/A')}\n"
                f"Content: {r.get('content', '')[:400]}...\n"
            )

        return "\n".join(formatted)

    def _parse_audit_result(
        self,
        company_name: str,
        analysis: str
    ) -> BrandAuditResult:
        """Parse LLM analysis into structured result."""
        result = BrandAuditResult(company_name=company_name)

        # Extract metrics from table
        result.metrics = self._extract_metrics(analysis)

        # Extract attributes
        result.attributes = self._extract_attributes(analysis)

        # Extract sentiment
        result.sentiment = self._extract_sentiment(analysis)

        # Extract strengths and weaknesses
        result.strengths = self._extract_list_section(analysis, "Strength")
        result.weaknesses = self._extract_list_section(analysis, "Weakness")

        # Extract recommendations
        result.recommendations = self._extract_list_section(analysis, "Recommendation")

        # Extract key messages
        result.key_messages = self._extract_list_section(analysis, "Message")

        # Extract overall score
        result.brand_score = self._extract_score(analysis)
        result.overall_strength = self._determine_strength(result.brand_score)

        return result

    def _extract_metrics(self, analysis: str) -> List[BrandMetric]:
        """Extract brand metrics from analysis."""
        metrics = []
        metric_names = ["Brand Awareness", "Brand Recall", "Brand Loyalty",
                       "Brand Trust", "Brand Relevance"]

        for name in metric_names:
            if name in analysis:
                # Try to find score after the metric name
                import re
                pattern = rf"{name}.*?(\d{{1,3}})"
                match = re.search(pattern, analysis)
                if match:
                    score = float(match.group(1))
                    trend = "stable"
                    if "↑" in analysis[match.start():match.end()+20]:
                        trend = "improving"
                    elif "↓" in analysis[match.start():match.end()+20]:
                        trend = "declining"

                    metrics.append(BrandMetric(
                        name=name,
                        score=min(100, score),
                        trend=trend
                    ))

        return metrics

    def _extract_attributes(self, analysis: str) -> List[BrandAttribute]:
        """Extract brand attributes from analysis."""
        attributes = []

        # Look for common brand attributes
        attribute_keywords = [
            "innovative", "reliable", "premium", "affordable",
            "sustainable", "trustworthy", "modern", "traditional"
        ]

        for keyword in attribute_keywords:
            if keyword.lower() in analysis.lower():
                # Estimate scores based on context
                strength = 60 if keyword in analysis else 40
                attributes.append(BrandAttribute(
                    attribute=keyword.capitalize(),
                    strength=strength,
                    relevance=70,
                    differentiation=50
                ))

        return attributes[:5]

    def _extract_sentiment(self, analysis: str) -> SentimentCategory:
        """Extract overall sentiment."""
        analysis_lower = analysis.lower()

        if "positive" in analysis_lower and "sentiment" in analysis_lower:
            return SentimentCategory.POSITIVE
        elif "negative" in analysis_lower and "sentiment" in analysis_lower:
            return SentimentCategory.NEGATIVE
        elif "mixed" in analysis_lower:
            return SentimentCategory.MIXED

        return SentimentCategory.NEUTRAL

    def _extract_list_section(self, analysis: str, section_keyword: str) -> List[str]:
        """Extract items from a list section."""
        items = []
        lines = analysis.split("\n")

        in_section = False
        for line in lines:
            if section_keyword.lower() in line.lower() and ("##" in line or "**" in line):
                in_section = True
                continue

            if in_section:
                if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "-", "•")):
                    item = line.strip().lstrip("0123456789.-•* ").strip()
                    if item and len(item) > 5:
                        items.append(item[:150])
                elif "##" in line or "**" in line:
                    break

        return items[:5]

    def _extract_score(self, analysis: str) -> float:
        """Extract overall brand score."""
        import re

        # Look for "Brand Score: XX" pattern
        patterns = [
            r"Brand Score[:\s]*(\d{1,3})",
            r"Overall.*?(\d{1,3})\s*/\s*100",
            r"(\d{1,3})\s*/\s*100"
        ]

        for pattern in patterns:
            match = re.search(pattern, analysis, re.IGNORECASE)
            if match:
                score = float(match.group(1))
                return min(100, score)

        return 50.0  # Default

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
    print("\n" + "=" * 70)
    print("[AGENT: Brand Auditor] Brand perception analysis...")
    print("=" * 70)

    config = get_config()
    company_name = state["company_name"]
    search_results = state.get("search_results", [])

    if not search_results:
        print("[Brand] WARNING: No search results available!")
        return {
            "agent_outputs": {
                "brand": {
                    "analysis": "No data available for brand audit",
                    "brand_score": 0,
                    "cost": 0.0
                }
            }
        }

    # Run brand audit
    agent = BrandAuditorAgent(config)
    result = agent.audit(
        company_name=company_name,
        search_results=search_results
    )

    # Calculate cost
    cost = config.calculate_llm_cost(500, 1500)  # Estimated

    print(f"[Brand] Brand Score: {result.brand_score}")
    print(f"[Brand] Strength: {result.overall_strength.value}")
    print(f"[Brand] Sentiment: {result.sentiment.value}")
    print("=" * 70)

    return {
        "agent_outputs": {
            "brand": {
                **result.to_dict(),
                "analysis": result.analysis,
                "cost": cost
            }
        },
        "total_cost": cost
    }


# ============================================================================
# Factory Function
# ============================================================================

def create_brand_auditor() -> BrandAuditorAgent:
    """Create a Brand Auditor Agent instance."""
    return BrandAuditorAgent()
