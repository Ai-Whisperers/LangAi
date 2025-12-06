"""
Reasoning Agent (Phase 13.2).

Advanced reasoning capabilities:
- Chain-of-thought analysis
- Causal reasoning
- Hypothesis generation and testing
- Strategic inference
- Multi-perspective evaluation

This agent applies structured reasoning to research data
to generate insights and strategic recommendations.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from anthropic import Anthropic

from ..config import get_config
from ..state import OverallState


# ============================================================================
# Data Models
# ============================================================================

class ReasoningType(str, Enum):
    """Types of reasoning approaches."""
    CAUSAL = "causal"           # Cause and effect
    COMPARATIVE = "comparative"  # Compare entities
    DEDUCTIVE = "deductive"     # General to specific
    INDUCTIVE = "inductive"     # Specific to general
    ABDUCTIVE = "abductive"     # Best explanation
    ANALOGICAL = "analogical"   # Pattern matching


class InsightType(str, Enum):
    """Types of insights generated."""
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    TREND = "trend"
    PATTERN = "pattern"
    ANOMALY = "anomaly"
    RECOMMENDATION = "recommendation"


@dataclass
class Hypothesis:
    """A hypothesis generated during reasoning."""
    statement: str
    confidence: float  # 0-1
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    status: str = "untested"  # untested, supported, refuted, uncertain

    def to_dict(self) -> Dict[str, Any]:
        return {
            "statement": self.statement,
            "confidence": round(self.confidence, 2),
            "supporting": len(self.supporting_evidence),
            "contradicting": len(self.contradicting_evidence),
            "status": self.status
        }


@dataclass
class Insight:
    """An insight derived from reasoning."""
    content: str
    insight_type: InsightType
    confidence: float
    reasoning_chain: List[str] = field(default_factory=list)
    implications: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "type": self.insight_type.value,
            "confidence": round(self.confidence, 2),
            "reasoning_steps": len(self.reasoning_chain),
            "implications": self.implications,
            "actions": self.action_items
        }


@dataclass
class ReasoningResult:
    """Complete result of reasoning analysis."""
    hypotheses: List[Hypothesis] = field(default_factory=list)
    insights: List[Insight] = field(default_factory=list)
    conclusions: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "insights": [i.to_dict() for i in self.insights],
            "conclusions": self.conclusions,
            "recommendations": self.recommendations,
            "confidence_score": round(self.confidence_score, 2)
        }


# ============================================================================
# Prompts
# ============================================================================

REASONING_PROMPT = """You are an expert strategic analyst applying structured reasoning to company research.

**COMPANY:** {company_name}

**RESEARCH DATA:**
{research_data}

**TASK:** Apply systematic reasoning to generate strategic insights.

**REASONING FRAMEWORK:**

### Step 1: Premise Identification
List the key facts and premises from the data:
1. [Premise 1]
2. [Premise 2]
...

### Step 2: Hypothesis Generation
Based on the premises, generate testable hypotheses:

**Hypothesis 1:** [Statement]
- Supporting evidence: [What supports this]
- Potential counterevidence: [What might contradict this]
- Confidence: [HIGH/MEDIUM/LOW]

**Hypothesis 2:** [Statement]
...

### Step 3: Causal Analysis
Identify cause-effect relationships:
- [Cause] → [Effect]
- [Cause] → [Effect]
...

### Step 4: Pattern Recognition
Identify patterns and trends:
- **Pattern 1:** [Description]
  - Evidence: [Supporting data]
  - Implication: [What this means]

### Step 5: Multi-Perspective Evaluation
Analyze from different viewpoints:

**Investor Perspective:**
- Opportunities: [List]
- Risks: [List]

**Competitor Perspective:**
- Threats posed by company: [List]
- Vulnerabilities: [List]

**Customer Perspective:**
- Value proposition: [Description]
- Concerns: [List]

### Step 6: Synthesis
**Key Insights:**
1. [Insight 1] - Confidence: [%]
2. [Insight 2] - Confidence: [%]
...

**Strategic Conclusions:**
1. [Conclusion with reasoning]
2. [Conclusion with reasoning]
...

**Recommendations:**
1. [Action item with rationale]
2. [Action item with rationale]
...

### Step 7: Confidence Assessment
**Overall Analysis Confidence:** [HIGH/MEDIUM/LOW]
**Data Quality Impact:** [How data gaps affect conclusions]

**REQUIREMENTS:**
- Show your reasoning chain explicitly
- Distinguish correlation from causation
- Acknowledge uncertainty appropriately
- Provide actionable recommendations

Begin your reasoning analysis:"""


HYPOTHESIS_TESTING_PROMPT = """Test the following hypothesis against available evidence:

**HYPOTHESIS:** {hypothesis}

**AVAILABLE EVIDENCE:**
{evidence}

**ANALYSIS:**
1. Evidence SUPPORTING the hypothesis:
   - [Evidence 1] - Strength: [STRONG/MODERATE/WEAK]
   - [Evidence 2] - ...

2. Evidence CONTRADICTING the hypothesis:
   - [Evidence 1] - Strength: [STRONG/MODERATE/WEAK]
   - ...

3. Missing evidence needed:
   - [What data would help]

**VERDICT:**
- Status: [SUPPORTED/REFUTED/UNCERTAIN/NEEDS_MORE_DATA]
- Confidence: [0-100%]
- Reasoning: [Brief explanation]"""


STRATEGIC_INFERENCE_PROMPT = """Based on the research data for {company_name}, perform strategic inference:

**DATA:**
{data}

**INFER:**
1. What strategic moves is the company likely to make?
2. What market dynamics are influencing their decisions?
3. What competitive advantages are sustainable?
4. What are the key success factors going forward?

Provide numbered insights with confidence levels and reasoning."""


# ============================================================================
# Reasoning Agent
# ============================================================================

class ReasoningAgent:
    """
    Reasoning Agent for strategic analysis.

    Applies multiple reasoning approaches:
    - Chain-of-thought analysis
    - Hypothesis generation and testing
    - Causal reasoning
    - Strategic inference

    Usage:
        agent = ReasoningAgent()
        result = agent.reason(
            company_name="Tesla",
            research_data=data,
            reasoning_types=[ReasoningType.CAUSAL, ReasoningType.DEDUCTIVE]
        )
    """

    def __init__(self, config=None):
        """Initialize agent."""
        self._config = config or get_config()
        self._client = Anthropic(api_key=self._config.anthropic_api_key)

    def reason(
        self,
        company_name: str,
        research_data: Dict[str, Any],
        reasoning_types: Optional[List[ReasoningType]] = None
    ) -> ReasoningResult:
        """
        Apply structured reasoning to research data.

        Args:
            company_name: Company name
            research_data: Research data from agents
            reasoning_types: Types of reasoning to apply

        Returns:
            ReasoningResult with insights and recommendations
        """
        reasoning_types = reasoning_types or [
            ReasoningType.CAUSAL,
            ReasoningType.DEDUCTIVE
        ]

        total_cost = 0.0
        result = ReasoningResult()

        # 1. Primary reasoning analysis
        print("[Reasoning] Performing primary analysis...")
        primary = self._primary_reasoning(company_name, research_data)
        total_cost += primary["cost"]

        # Extract hypotheses
        result.hypotheses = self._extract_hypotheses(primary["analysis"])

        # Extract insights
        result.insights = self._extract_insights(primary["analysis"])

        # 2. Test key hypotheses
        if result.hypotheses:
            print(f"[Reasoning] Testing {len(result.hypotheses)} hypotheses...")
            for hypothesis in result.hypotheses[:3]:  # Test top 3
                test_result = self._test_hypothesis(
                    hypothesis.statement,
                    self._format_evidence(research_data)
                )
                total_cost += test_result["cost"]

                # Update hypothesis based on test
                self._update_hypothesis(hypothesis, test_result["analysis"])

        # 3. Strategic inference
        print("[Reasoning] Generating strategic inferences...")
        strategic = self._strategic_inference(company_name, research_data)
        total_cost += strategic["cost"]

        # Extract conclusions and recommendations
        result.conclusions = self._extract_conclusions(primary["analysis"])
        result.recommendations = self._extract_recommendations(strategic["analysis"])

        # Calculate overall confidence
        result.confidence_score = self._calculate_confidence(result)

        return result

    def _primary_reasoning(
        self,
        company_name: str,
        research_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform primary reasoning analysis."""
        formatted_data = self._format_research_data(research_data)

        prompt = REASONING_PROMPT.format(
            company_name=company_name,
            research_data=formatted_data
        )

        response = self._client.messages.create(
            model=self._config.llm_model,
            max_tokens=2000,
            temperature=0.1,  # Slightly creative for reasoning
            messages=[{"role": "user", "content": prompt}]
        )

        cost = self._config.calculate_llm_cost(
            response.usage.input_tokens,
            response.usage.output_tokens
        )

        return {
            "analysis": response.content[0].text,
            "cost": cost
        }

    def _test_hypothesis(
        self,
        hypothesis: str,
        evidence: str
    ) -> Dict[str, Any]:
        """Test a hypothesis against evidence."""
        prompt = HYPOTHESIS_TESTING_PROMPT.format(
            hypothesis=hypothesis,
            evidence=evidence
        )

        response = self._client.messages.create(
            model=self._config.llm_model,
            max_tokens=800,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}]
        )

        cost = self._config.calculate_llm_cost(
            response.usage.input_tokens,
            response.usage.output_tokens
        )

        return {
            "analysis": response.content[0].text,
            "cost": cost
        }

    def _strategic_inference(
        self,
        company_name: str,
        research_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate strategic inferences."""
        formatted_data = self._format_research_data(research_data)

        prompt = STRATEGIC_INFERENCE_PROMPT.format(
            company_name=company_name,
            data=formatted_data[:3000]  # Limit data
        )

        response = self._client.messages.create(
            model=self._config.llm_model,
            max_tokens=1000,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )

        cost = self._config.calculate_llm_cost(
            response.usage.input_tokens,
            response.usage.output_tokens
        )

        return {
            "analysis": response.content[0].text,
            "cost": cost
        }

    def _format_research_data(self, data: Dict[str, Any]) -> str:
        """Format research data for prompts."""
        sections = []

        for key, value in data.items():
            if isinstance(value, dict):
                if "analysis" in value:
                    sections.append(f"**{key.upper()}:**\n{value['analysis'][:1000]}")
                else:
                    sections.append(f"**{key.upper()}:**\n{str(value)[:500]}")
            elif isinstance(value, str):
                sections.append(f"**{key.upper()}:**\n{value[:1000]}")

        return "\n\n".join(sections) if sections else "No data available"

    def _format_evidence(self, data: Dict[str, Any]) -> str:
        """Format data as evidence for hypothesis testing."""
        evidence_points = []

        for key, value in data.items():
            if isinstance(value, dict) and "analysis" in value:
                # Extract key statements from analysis
                analysis = value["analysis"]
                lines = analysis.split("\n")
                for line in lines[:10]:
                    if line.strip() and len(line.strip()) > 20:
                        evidence_points.append(f"- {line.strip()[:200]}")

        return "\n".join(evidence_points[:20]) if evidence_points else "Limited evidence available"

    def _extract_hypotheses(self, analysis: str) -> List[Hypothesis]:
        """Extract hypotheses from analysis."""
        hypotheses = []
        lines = analysis.split("\n")

        current_hypothesis = None

        for line in lines:
            line = line.strip()

            if "Hypothesis" in line and ":" in line:
                # Start of new hypothesis
                if current_hypothesis:
                    hypotheses.append(current_hypothesis)

                statement = line.split(":", 1)[1].strip() if ":" in line else line
                # Remove markdown formatting
                statement = statement.replace("**", "").replace("*", "")

                current_hypothesis = Hypothesis(
                    statement=statement,
                    confidence=0.5  # Default
                )

            elif current_hypothesis:
                if "confidence" in line.lower():
                    if "high" in line.lower():
                        current_hypothesis.confidence = 0.8
                    elif "low" in line.lower():
                        current_hypothesis.confidence = 0.3
                elif "supporting" in line.lower() or "support" in line.lower():
                    current_hypothesis.supporting_evidence.append(line)
                elif "contradict" in line.lower() or "counter" in line.lower():
                    current_hypothesis.contradicting_evidence.append(line)

        if current_hypothesis:
            hypotheses.append(current_hypothesis)

        return hypotheses[:5]  # Limit

    def _extract_insights(self, analysis: str) -> List[Insight]:
        """Extract insights from analysis."""
        insights = []
        lines = analysis.split("\n")

        # Look for numbered insights or key findings
        for i, line in enumerate(lines):
            line = line.strip()

            if ("Insight" in line or "Key Finding" in line) and ":" in line:
                content = line.split(":", 1)[1].strip()

                # Determine type
                insight_type = InsightType.PATTERN
                if "risk" in content.lower():
                    insight_type = InsightType.RISK
                elif "opportunity" in content.lower():
                    insight_type = InsightType.OPPORTUNITY
                elif "trend" in content.lower():
                    insight_type = InsightType.TREND
                elif "recommend" in content.lower():
                    insight_type = InsightType.RECOMMENDATION

                # Extract confidence
                confidence = 0.6  # Default
                if "high" in lines[i:i+3]:
                    confidence = 0.8
                elif "low" in lines[i:i+3]:
                    confidence = 0.4

                insights.append(Insight(
                    content=content[:200],
                    insight_type=insight_type,
                    confidence=confidence
                ))

        return insights[:10]

    def _extract_conclusions(self, analysis: str) -> List[str]:
        """Extract conclusions from analysis."""
        conclusions = []

        # Look for conclusion section
        if "Conclusion" in analysis:
            section_start = analysis.find("Conclusion")
            section = analysis[section_start:section_start+1000]

            for line in section.split("\n"):
                line = line.strip()
                if line and len(line) > 20 and not line.startswith("#"):
                    # Clean up
                    if line.startswith(("-", "•", "*")):
                        line = line[1:].strip()
                    if line.startswith(("1.", "2.", "3.")):
                        line = line[2:].strip()

                    if len(line) > 20:
                        conclusions.append(line[:200])

        return conclusions[:5]

    def _extract_recommendations(self, analysis: str) -> List[str]:
        """Extract recommendations from analysis."""
        recommendations = []

        for line in analysis.split("\n"):
            line = line.strip()

            # Look for recommendation patterns
            if any(marker in line.lower() for marker in ["recommend", "should", "suggest", "action"]):
                if len(line) > 30:
                    # Clean up
                    if line.startswith(("-", "•", "*")):
                        line = line[1:].strip()
                    if line.startswith(("1.", "2.", "3.")):
                        line = line[2:].strip()

                    recommendations.append(line[:200])

        return recommendations[:5]

    def _update_hypothesis(self, hypothesis: Hypothesis, test_result: str) -> None:
        """Update hypothesis based on test result."""
        test_lower = test_result.lower()

        if "supported" in test_lower:
            hypothesis.status = "supported"
            hypothesis.confidence = min(0.9, hypothesis.confidence + 0.2)
        elif "refuted" in test_lower:
            hypothesis.status = "refuted"
            hypothesis.confidence = max(0.1, hypothesis.confidence - 0.3)
        elif "uncertain" in test_lower:
            hypothesis.status = "uncertain"
        else:
            hypothesis.status = "needs_more_data"

    def _calculate_confidence(self, result: ReasoningResult) -> float:
        """Calculate overall confidence score."""
        scores = []

        # Hypothesis confidence
        if result.hypotheses:
            hyp_confidence = sum(h.confidence for h in result.hypotheses) / len(result.hypotheses)
            scores.append(hyp_confidence)

        # Insight confidence
        if result.insights:
            insight_confidence = sum(i.confidence for i in result.insights) / len(result.insights)
            scores.append(insight_confidence)

        # Data completeness factor
        completeness = 0.5
        if result.conclusions:
            completeness += 0.2
        if result.recommendations:
            completeness += 0.2
        scores.append(completeness)

        return sum(scores) / len(scores) if scores else 0.5


# ============================================================================
# Agent Node Function
# ============================================================================

def reasoning_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Reasoning Agent Node for workflow integration.

    Args:
        state: Current workflow state

    Returns:
        State update with reasoning results
    """
    print("\n" + "=" * 70)
    print("[AGENT: Reasoning] Strategic reasoning analysis...")
    print("=" * 70)

    company_name = state["company_name"]
    agent_outputs = state.get("agent_outputs", {})

    if not agent_outputs:
        print("[Reasoning] WARNING: No agent outputs available!")
        return {
            "agent_outputs": {
                "reasoning": {
                    "analysis": "No data available for reasoning",
                    "insights": [],
                    "cost": 0.0
                }
            }
        }

    # Run reasoning agent
    agent = ReasoningAgent()
    result = agent.reason(
        company_name=company_name,
        research_data=agent_outputs
    )

    print(f"[Reasoning] Generated {len(result.hypotheses)} hypotheses")
    print(f"[Reasoning] Generated {len(result.insights)} insights")
    print(f"[Reasoning] Confidence: {result.confidence_score:.0%}")
    print("=" * 70)

    return {
        "agent_outputs": {
            "reasoning": {
                **result.to_dict(),
                "analysis": self._format_result_text(result)
            }
        }
    }


def _format_result_text(result: ReasoningResult) -> str:
    """Format reasoning result as text."""
    sections = []

    if result.hypotheses:
        sections.append("**Hypotheses:**")
        for h in result.hypotheses:
            sections.append(f"- {h.statement} ({h.status}, {h.confidence:.0%})")

    if result.insights:
        sections.append("\n**Insights:**")
        for i in result.insights:
            sections.append(f"- [{i.insight_type.value}] {i.content}")

    if result.conclusions:
        sections.append("\n**Conclusions:**")
        for c in result.conclusions:
            sections.append(f"- {c}")

    if result.recommendations:
        sections.append("\n**Recommendations:**")
        for r in result.recommendations:
            sections.append(f"- {r}")

    return "\n".join(sections)


# ============================================================================
# Factory Function
# ============================================================================

def create_reasoning_agent() -> ReasoningAgent:
    """Create a Reasoning Agent instance."""
    return ReasoningAgent()
