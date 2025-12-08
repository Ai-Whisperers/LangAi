"""
Logic Critic Agent (Phase 10).

Quality assurance and verification specialist that:
- Extracts and verifies facts from agent outputs
- Detects contradictions and conflicts
- Calculates quality scores
- Identifies gaps in research
- Provides recommendations for improvement

This agent runs after all specialist agents and before report generation
to ensure research quality and accuracy.
"""

import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

from ...config import get_config
from ...llm.client_factory import get_anthropic_client, calculate_cost
from ...state import OverallState
from ...quality.fact_extractor import (
    FactExtractor,
    ExtractedFact,
    ExtractionResult,
    FactCategory
)
from ...quality.contradiction_detector import (
    ContradictionDetector,
    ContradictionReport,
    ContradictionSeverity
)
from ...quality.models import QualityReport, ConfidenceLevel
from enum import Enum
from dataclasses import dataclass


class IssueSeverity(str, Enum):
    """Severity levels for quality issues."""
    CRITICAL = "critical"  # Major contradiction or error
    HIGH = "high"         # Significant issue
    MEDIUM = "medium"     # Moderate concern
    LOW = "low"           # Minor issue
    INFO = "info"         # Informational only


@dataclass
class QualityIssue:
    """A quality issue found in research."""
    issue_type: str
    severity: IssueSeverity
    description: str
    location: str = ""
    recommendation: str = ""


class LogicCriticAgent:
    """Logic critic agent for quality assurance and verification."""

    def __init__(self, search_tool: Optional[Callable] = None, llm_client: Optional[Any] = None):
        self.search_tool = search_tool
        self.llm_client = llm_client or get_anthropic_client()

    async def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Perform logic critic analysis on research state."""
        return logic_critic_agent_node(state)


def create_logic_critic(search_tool: Callable = None, llm_client: Any = None) -> LogicCriticAgent:
    """Factory function to create a LogicCriticAgent."""
    return LogicCriticAgent(search_tool=search_tool, llm_client=llm_client)


# ============================================================================
# Required Research Sections
# ============================================================================

REQUIRED_SECTIONS = {
    "company_overview": {
        "name": "Company Overview",
        "fields": ["description", "headquarters", "founded", "employees"],
        "weight": 0.15
    },
    "financial": {
        "name": "Financial Analysis",
        "fields": ["revenue", "profitability", "funding", "valuation"],
        "weight": 0.25
    },
    "market": {
        "name": "Market Analysis",
        "fields": ["market_size", "market_share", "trends", "competitors"],
        "weight": 0.20
    },
    "product": {
        "name": "Product Analysis",
        "fields": ["products", "technology", "features"],
        "weight": 0.15
    },
    "competitive": {
        "name": "Competitive Intelligence",
        "fields": ["competitors", "positioning", "threats"],
        "weight": 0.15
    },
    "leadership": {
        "name": "Leadership",
        "fields": ["executives", "team"],
        "weight": 0.10
    }
}


# ============================================================================
# Gap Identification
# ============================================================================

class ResearchGap:
    """Represents a gap in research coverage."""

    def __init__(
        self,
        section: str,
        field: str,
        severity: str = "medium",
        recommendation: str = ""
    ):
        self.section = section
        self.field = field
        self.severity = severity
        self.recommendation = recommendation

    def to_dict(self) -> Dict[str, str]:
        return {
            "section": self.section,
            "field": self.field,
            "severity": self.severity,
            "recommendation": self.recommendation
        }


def identify_gaps(
    facts: List[ExtractedFact],
    agent_outputs: Dict[str, Any]
) -> List[ResearchGap]:
    """
    Identify gaps in research coverage.

    Args:
        facts: Extracted facts
        agent_outputs: Agent output data

    Returns:
        List of identified gaps
    """
    gaps = []

    # Group facts by category
    facts_by_category = {}
    for fact in facts:
        cat = fact.category.value
        if cat not in facts_by_category:
            facts_by_category[cat] = []
        facts_by_category[cat].append(fact)

    # Check each required section
    for section_id, section_info in REQUIRED_SECTIONS.items():
        section_facts = facts_by_category.get(section_id, [])

        # Check if section has enough coverage
        if len(section_facts) < 3:  # Minimum facts per section
            gaps.append(ResearchGap(
                section=section_info["name"],
                field="general",
                severity="high" if section_info["weight"] > 0.15 else "medium",
                recommendation=f"Need more facts for {section_info['name']} section"
            ))

        # Check specific fields
        for field in section_info["fields"]:
            field_covered = any(
                field in fact.content.lower()
                for fact in section_facts
            )
            if not field_covered:
                gaps.append(ResearchGap(
                    section=section_info["name"],
                    field=field,
                    severity="medium",
                    recommendation=f"Missing {field} information in {section_info['name']}"
                ))

    return gaps


# ============================================================================
# Quality Scoring
# ============================================================================

def calculate_comprehensive_quality(
    facts: List[ExtractedFact],
    contradiction_report: ContradictionReport,
    gaps: List[ResearchGap]
) -> Dict[str, Any]:
    """
    Calculate comprehensive quality score.

    Factors:
    - Fact count and coverage (25%)
    - Contradiction status (30%)
    - Gap coverage (25%)
    - Confidence distribution (20%)

    Returns:
        Quality metrics dictionary
    """
    # Fact coverage score
    total_facts = len(facts)
    if total_facts >= 50:
        fact_score = 100
    elif total_facts >= 30:
        fact_score = 80
    elif total_facts >= 15:
        fact_score = 60
    else:
        fact_score = 40

    # Contradiction score (fewer is better)
    contradiction_count = contradiction_report.total_count
    critical_count = contradiction_report.critical_count

    if critical_count > 0:
        contradiction_score = max(0, 100 - (critical_count * 30) - (contradiction_count * 10))
    elif contradiction_count > 0:
        contradiction_score = max(0, 100 - (contradiction_count * 15))
    else:
        contradiction_score = 100

    # Gap score (fewer is better)
    high_gaps = sum(1 for g in gaps if g.severity == "high")
    medium_gaps = sum(1 for g in gaps if g.severity == "medium")

    if high_gaps > 3:
        gap_score = 40
    elif high_gaps > 0:
        gap_score = 70 - (high_gaps * 10)
    else:
        gap_score = 100 - (medium_gaps * 5)
    gap_score = max(0, min(100, gap_score))

    # Confidence score
    high_confidence = sum(1 for f in facts if f.confidence_hint > 0.7)
    if total_facts > 0:
        confidence_score = (high_confidence / total_facts) * 100
    else:
        confidence_score = 0

    # Overall weighted score
    overall_score = (
        fact_score * 0.25 +
        contradiction_score * 0.30 +
        gap_score * 0.25 +
        confidence_score * 0.20
    )

    return {
        "overall_score": round(overall_score, 1),
        "fact_score": round(fact_score, 1),
        "contradiction_score": round(contradiction_score, 1),
        "gap_score": round(gap_score, 1),
        "confidence_score": round(confidence_score, 1),
        "total_facts": total_facts,
        "contradiction_count": contradiction_count,
        "critical_contradictions": critical_count,
        "high_gaps": high_gaps,
        "medium_gaps": medium_gaps,
        "passed": overall_score >= 75
    }


# ============================================================================
# Logic Critic Agent
# ============================================================================

LOGIC_CRITIC_PROMPT = """You are a critical analyst reviewing research about {company_name}.

## Research Summary
{research_summary}

## Facts Analyzed: {fact_count}
## Contradictions Found: {contradiction_count}
## Gaps Identified: {gap_count}

## Quality Score: {quality_score}/100

## Task
Provide a critical assessment of this research including:

1. **Verification Status**: What facts are well-supported vs questionable?

2. **Contradiction Analysis**: For any contradictions, which version is likely correct and why?

3. **Gap Assessment**: What critical information is missing?

4. **Confidence Assessment**: How confident should we be in the overall research?

5. **Recommendations**: What specific actions would improve this research?

Be specific and actionable. Focus on the most important issues.

Provide your analysis:"""


def logic_critic_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Logic Critic Agent Node: Quality assurance and verification.

    Analyzes:
    1. Extracts facts from all agent outputs
    2. Detects contradictions
    3. Identifies gaps
    4. Calculates quality score
    5. Provides recommendations

    Args:
        state: Current workflow state

    Returns:
        State update with quality assessment
    """
    logger.info("Logic Critic agent starting - quality assurance analysis")

    config = get_config()
    company_name = state["company_name"]
    agent_outputs = state.get("agent_outputs", {})

    start_time = datetime.now()

    # Step 1: Extract facts from all agent outputs
    logger.debug("Step 1: Extracting facts")
    extractor = FactExtractor()
    all_facts: List[ExtractedFact] = []

    for agent_name, output in agent_outputs.items():
        if isinstance(output, dict) and output:
            result = extractor.extract_from_agent_output(output, agent_name)
            all_facts.extend(result.facts)
            logger.debug(f"  {agent_name}: {result.total_facts} facts extracted")

    logger.info(f"Total facts extracted: {len(all_facts)}")

    # Step 2: Detect contradictions
    logger.debug("Step 2: Detecting contradictions")
    detector = ContradictionDetector(use_llm=True)
    contradiction_report = detector.detect(all_facts)

    if contradiction_report.total_count > 0:
        logger.info(f"Found {contradiction_report.total_count} contradictions (Critical: {contradiction_report.critical_count}, High: {contradiction_report.high_count})")
    else:
        logger.debug("No contradictions detected")

    # Step 3: Identify gaps
    logger.debug("Step 3: Identifying gaps")
    gaps = identify_gaps(all_facts, agent_outputs)
    high_gaps = [g for g in gaps if g.severity == "high"]

    if gaps:
        logger.info(f"Found {len(gaps)} gaps ({len(high_gaps)} high severity)")
    else:
        logger.debug("No significant gaps")

    # Step 4: Calculate quality score
    logger.debug("Step 4: Calculating quality score")
    quality_metrics = calculate_comprehensive_quality(
        all_facts,
        contradiction_report,
        gaps
    )
    logger.info(f"Quality Score: {quality_metrics['overall_score']}/100")

    # Step 5: Generate LLM recommendations
    logger.debug("Step 5: Generating recommendations")

    # Build research summary
    research_parts = []
    if "company_overview" in agent_outputs:
        research_parts.append(f"Overview: {str(agent_outputs['company_overview'])[:500]}")
    for agent in ["financial", "market", "product", "competitor"]:
        if agent in agent_outputs:
            research_parts.append(f"{agent.title()}: {str(agent_outputs[agent])[:300]}")

    research_summary = "\n".join(research_parts)[:2000]

    prompt = LOGIC_CRITIC_PROMPT.format(
        company_name=company_name,
        research_summary=research_summary,
        fact_count=len(all_facts),
        contradiction_count=contradiction_report.total_count,
        gap_count=len(gaps),
        quality_score=quality_metrics['overall_score']
    )

    client = get_anthropic_client()
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=800,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )

    critic_analysis = response.content[0].text
    cost = calculate_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    duration = (datetime.now() - start_time).total_seconds()

    logger.info(f"Logic Critic agent complete - cost: ${cost:.4f}")

    # Build comprehensive output
    agent_output = {
        "analysis": critic_analysis,
        "quality_metrics": quality_metrics,
        "facts_analyzed": len(all_facts),
        "contradictions": {
            "total": contradiction_report.total_count,
            "critical": contradiction_report.critical_count,
            "high": contradiction_report.high_count,
            "details": [
                {
                    "id": c.id,
                    "topic": c.topic,
                    "severity": c.severity.value,
                    "explanation": c.explanation
                }
                for c in contradiction_report.contradictions[:5]  # Top 5
            ]
        },
        "gaps": {
            "total": len(gaps),
            "high_severity": len(high_gaps),
            "items": [g.to_dict() for g in gaps[:10]]  # Top 10
        },
        "recommendations": extract_recommendations(critic_analysis),
        "passed": quality_metrics['passed'],
        "cost": cost,
        "duration_seconds": duration,
        "tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }

    return {
        "agent_outputs": {"logic_critic": agent_output},
        "quality_score": quality_metrics['overall_score'],
        "total_cost": cost,
        "total_tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }


def extract_recommendations(analysis_text: str) -> List[str]:
    """Extract recommendations from analysis text."""
    recommendations = []

    # Look for recommendation section
    lines = analysis_text.split('\n')
    in_recommendations = False

    for line in lines:
        line = line.strip()
        if 'recommendation' in line.lower() or 'action' in line.lower():
            in_recommendations = True
            continue

        if in_recommendations and line.startswith(('-', '•', '*', '1', '2', '3')):
            rec = line.lstrip('-•*0123456789. ')
            if len(rec) > 10:
                recommendations.append(rec)

    return recommendations[:5]  # Top 5


# ============================================================================
# Alternative: Quick Critic (No LLM)
# ============================================================================

def quick_logic_critic_node(state: OverallState) -> Dict[str, Any]:
    """
    Quick Logic Critic without LLM (for cost-sensitive operations).

    Only performs rule-based analysis.
    """
    logger.info("Logic Critic (Quick) - running rule-based analysis")

    agent_outputs = state.get("agent_outputs", {})

    # Extract facts
    extractor = FactExtractor()
    all_facts = []
    for agent_name, output in agent_outputs.items():
        if isinstance(output, dict):
            result = extractor.extract_from_agent_output(output, agent_name)
            all_facts.extend(result.facts)

    # Detect contradictions (no LLM)
    detector = ContradictionDetector(use_llm=False)
    contradiction_report = detector.detect(all_facts)

    # Identify gaps
    gaps = identify_gaps(all_facts, agent_outputs)

    # Calculate quality
    quality_metrics = calculate_comprehensive_quality(
        all_facts, contradiction_report, gaps
    )

    logger.info(f"Logic Critic (Quick) Score: {quality_metrics['overall_score']}/100")

    return {
        "agent_outputs": {
            "logic_critic": {
                "quality_metrics": quality_metrics,
                "facts_analyzed": len(all_facts),
                "contradictions": contradiction_report.total_count,
                "gaps": len(gaps),
                "passed": quality_metrics['passed'],
                "cost": 0.0
            }
        },
        "quality_score": quality_metrics['overall_score']
    }
