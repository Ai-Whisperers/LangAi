"""
Quality Assurance Subgraph - Phase 11

Handles comprehensive quality verification:
- Fact extraction from analysis outputs
- Contradiction detection (rule-based + LLM)
- Gap identification (missing information)
- Quality scoring with detailed breakdown
- Iteration recommendation

This subgraph ensures research quality meets threshold before
proceeding to output generation.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from langgraph.graph import END, START, StateGraph

from ...agents.quality.logic_critic import logic_critic_agent_node
from ...quality import check_research_quality
from ...state.workflow import OverallState
from ...utils import get_logger, utc_now

logger = get_logger(__name__)


@dataclass
class QualityConfig:
    """Configuration for quality assurance subgraph."""

    # Quality thresholds
    min_quality_score: float = 85.0
    max_iterations: int = 2

    # Quality check components
    enable_fact_extraction: bool = True
    enable_contradiction_detection: bool = True
    enable_gap_analysis: bool = True
    enable_logic_critic: bool = True

    # Scoring weights
    weight_completeness: float = 0.3
    weight_accuracy: float = 0.3
    weight_consistency: float = 0.2
    weight_freshness: float = 0.2

    # Iteration behavior
    auto_iterate: bool = True
    iterate_on_gaps: bool = True
    iterate_on_contradictions: bool = True


# ============================================================================
# Quality Check Nodes
# ============================================================================


def extract_facts_node(state: OverallState) -> Dict[str, Any]:
    """
    Extract verifiable facts from analysis outputs.

    This node:
    1. Parses agent outputs for factual claims
    2. Categorizes facts by type (financial, market, product, etc.)
    3. Assigns confidence scores to each fact

    Args:
        state: Current workflow state

    Returns:
        State update with extracted facts
    """
    logger.info("[NODE] Extracting facts from analysis...")

    agent_outputs = state.get("agent_outputs", {})
    company_overview = state.get("company_overview", "")

    facts = []
    fact_categories = {
        "financial": [],
        "market": [],
        "product": [],
        "competitor": [],
        "general": [],
    }

    # Extract facts from each agent output
    for agent_name, output in agent_outputs.items():
        analysis = output.get("analysis", "")

        # Simple fact extraction (would use NLP in production)
        # Look for sentences with numbers, percentages, or claims
        if analysis:
            # Split into sentences
            sentences = analysis.replace("\n", " ").split(". ")

            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue

                # Check if sentence contains factual indicators
                has_number = any(char.isdigit() for char in sentence)
                has_percentage = "%" in sentence
                has_currency = "$" in sentence or "EUR" in sentence
                has_claim_word = any(
                    word in sentence.lower()
                    for word in ["is", "are", "was", "were", "has", "have", "revenue", "market"]
                )

                if has_number or has_percentage or has_currency or has_claim_word:
                    fact = {
                        "text": sentence[:500],  # Truncate long facts
                        "source_agent": agent_name,
                        "confidence": 0.7 if has_number else 0.5,
                        "category": _categorize_fact(agent_name, sentence),
                    }
                    facts.append(fact)
                    fact_categories[fact["category"]].append(fact)

    logger.info(f"[FACTS] Extracted {len(facts)} facts from {len(agent_outputs)} agents")

    return {
        "extracted_facts": facts,
        "fact_categories": fact_categories,
        "facts_count": len(facts),
    }


def _categorize_fact(agent_name: str, sentence: str) -> str:
    """Categorize a fact based on source agent and content."""
    if agent_name in ("financial", "investment"):
        return "financial"
    elif agent_name in ("market", "competitor"):
        return "market"
    elif agent_name == "product":
        return "product"
    elif "competitor" in sentence.lower() or "rival" in sentence.lower():
        return "competitor"
    else:
        return "general"


def detect_contradictions_node(state: OverallState) -> Dict[str, Any]:
    """
    Detect contradictions between facts from different sources.

    This node:
    1. Compares facts across agents
    2. Identifies conflicting claims
    3. Flags high-severity contradictions

    Args:
        state: Current workflow state

    Returns:
        State update with detected contradictions
    """
    logger.info("[NODE] Detecting contradictions...")

    facts = state.get("extracted_facts", [])
    contradictions = []

    # Group facts by category for comparison
    categories = {}
    for fact in facts:
        cat = fact.get("category", "general")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(fact)

    # Compare facts within same category from different sources
    for category, cat_facts in categories.items():
        if len(cat_facts) < 2:
            continue

        for i, fact1 in enumerate(cat_facts):
            for fact2 in cat_facts[i + 1 :]:
                # Skip if same source
                if fact1.get("source_agent") == fact2.get("source_agent"):
                    continue

                # Check for potential contradiction (simplified)
                contradiction = _check_contradiction(fact1, fact2)
                if contradiction:
                    contradictions.append(contradiction)

    # Categorize by severity
    critical_contradictions = [c for c in contradictions if c.get("severity") == "critical"]
    high_contradictions = [c for c in contradictions if c.get("severity") == "high"]
    low_contradictions = [c for c in contradictions if c.get("severity") == "low"]

    logger.info(
        f"[CONTRADICTIONS] Found {len(contradictions)} "
        f"(critical: {len(critical_contradictions)}, high: {len(high_contradictions)})"
    )

    return {
        "contradictions": {
            "total": len(contradictions),
            "critical": len(critical_contradictions),
            "high": len(high_contradictions),
            "low": len(low_contradictions),
            "items": contradictions[:10],  # Top 10 contradictions
        },
    }


def _check_contradiction(fact1: Dict, fact2: Dict) -> Optional[Dict]:
    """Check if two facts contradict each other."""
    text1 = fact1.get("text", "").lower()
    text2 = fact2.get("text", "").lower()

    # Look for numerical contradictions (simplified)
    import re

    # Extract numbers from both facts
    numbers1 = re.findall(r"\$?[\d,]+\.?\d*[BMK]?%?", text1)
    numbers2 = re.findall(r"\$?[\d,]+\.?\d*[BMK]?%?", text2)

    # Check if facts discuss same topic but have different numbers
    common_topics = ["revenue", "employees", "market", "growth", "share"]

    for topic in common_topics:
        if topic in text1 and topic in text2:
            if numbers1 and numbers2 and numbers1[0] != numbers2[0]:
                return {
                    "fact1": fact1,
                    "fact2": fact2,
                    "topic": topic,
                    "severity": "high" if topic == "revenue" else "low",
                    "description": f"Conflicting {topic} data between agents",
                }

    return None


def identify_gaps_node(state: OverallState) -> Dict[str, Any]:
    """
    Identify gaps in research coverage.

    This node:
    1. Checks for missing required information
    2. Evaluates section completeness
    3. Generates recommendations for additional research

    Args:
        state: Current workflow state

    Returns:
        State update with identified gaps
    """
    logger.info("[NODE] Identifying information gaps...")

    # Required sections for comprehensive research
    required_sections = {
        "company_overview": {
            "description": "Company description and background",
            "source_field": "company_overview",
            "severity": "high",
        },
        "financial_metrics": {
            "description": "Revenue, profitability, financial health",
            "source_field": "key_metrics",
            "severity": "high",
        },
        "products_services": {
            "description": "Products and services catalog",
            "source_field": "products_services",
            "severity": "medium",
        },
        "competitors": {
            "description": "Competitive landscape",
            "source_field": "competitors",
            "severity": "medium",
        },
        "market_position": {
            "description": "Market share and positioning",
            "source_field": "agent_outputs.market",
            "severity": "medium",
        },
    }

    gaps = []
    gap_recommendations = []

    for section_name, section_info in required_sections.items():
        field = section_info["source_field"]

        # Check if field exists and has content
        if "." in field:
            # Nested field (e.g., agent_outputs.market)
            parts = field.split(".")
            value = state
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    value = None
                    break
        else:
            value = state.get(field)

        is_missing = value is None or (isinstance(value, (str, list, dict)) and not value)

        if is_missing:
            gaps.append(
                {
                    "section": section_name,
                    "field": field,
                    "description": section_info["description"],
                    "severity": section_info["severity"],
                    "recommendation": f"Research more about {section_info['description'].lower()}",
                }
            )

            if section_info["severity"] in ("high", "critical"):
                gap_recommendations.append(
                    f"Search for: {state.get('company_name', 'company')} {section_name.replace('_', ' ')}"
                )

    # Count by severity
    high_severity_gaps = len([g for g in gaps if g["severity"] in ("high", "critical")])

    logger.info(f"[GAPS] Found {len(gaps)} gaps ({high_severity_gaps} high severity)")

    return {
        "gaps": {
            "total": len(gaps),
            "high_severity": high_severity_gaps,
            "items": gaps,
        },
        "gap_recommendations": gap_recommendations[:5],  # Top 5 recommendations
    }


def calculate_quality_score_node(state: OverallState) -> Dict[str, Any]:
    """
    Calculate comprehensive quality score.

    This node combines metrics from:
    1. Fact extraction (completeness)
    2. Contradiction detection (consistency)
    3. Gap analysis (coverage)
    4. Logic critic analysis (accuracy)

    Args:
        state: Current workflow state

    Returns:
        State update with quality score and breakdown
    """
    logger.info("[NODE] Calculating quality score...")

    # Get component scores
    facts_count = state.get("facts_count", 0)
    contradictions = state.get("contradictions", {})
    gaps = state.get("gaps", {})

    # Logic critic score (if available)
    agent_outputs = state.get("agent_outputs", {})
    logic_critic_output = agent_outputs.get("logic_critic", {})
    logic_critic_score = logic_critic_output.get("quality_metrics", {}).get("overall_score", 0)

    # Calculate component scores (0-100)
    # Completeness: Based on facts extracted
    completeness_score = min(100, facts_count * 2)  # 50 facts = 100%

    # Consistency: Based on contradictions
    total_contradictions = contradictions.get("total", 0)
    critical_contradictions = contradictions.get("critical", 0)
    consistency_score = max(0, 100 - (critical_contradictions * 20) - (total_contradictions * 5))

    # Coverage: Based on gaps
    total_gaps = gaps.get("total", 0)
    high_severity_gaps = gaps.get("high_severity", 0)
    coverage_score = max(0, 100 - (high_severity_gaps * 25) - (total_gaps * 10))

    # Accuracy: Use logic critic score if available
    accuracy_score = (
        logic_critic_score
        if logic_critic_score > 0
        else (completeness_score + consistency_score) / 2
    )

    # Weighted final score
    weights = {
        "completeness": 0.25,
        "consistency": 0.25,
        "coverage": 0.25,
        "accuracy": 0.25,
    }

    final_score = (
        completeness_score * weights["completeness"]
        + consistency_score * weights["consistency"]
        + coverage_score * weights["coverage"]
        + accuracy_score * weights["accuracy"]
    )

    quality_breakdown = {
        "completeness": round(completeness_score, 1),
        "consistency": round(consistency_score, 1),
        "coverage": round(coverage_score, 1),
        "accuracy": round(accuracy_score, 1),
        "final_score": round(final_score, 1),
        "weights": weights,
    }

    logger.info(f"[QUALITY] Score: {final_score:.1f}/100")
    logger.info(
        f"[QUALITY] Breakdown: completeness={completeness_score:.0f}, consistency={consistency_score:.0f}, coverage={coverage_score:.0f}, accuracy={accuracy_score:.0f}"
    )

    return {
        "quality_score": round(final_score, 1),
        "quality_breakdown": quality_breakdown,
    }


def should_iterate_node(state: OverallState) -> Dict[str, Any]:
    """
    Determine if research should iterate for better quality.

    Args:
        state: Current workflow state

    Returns:
        State update with iteration decision and recommendations
    """
    quality_score = state.get("quality_score", 0)
    iteration_count = state.get("iteration_count", 0)
    gaps = state.get("gaps", {})
    contradictions = state.get("contradictions", {})

    # Get configuration (could be passed in config)
    min_quality = 85.0
    max_iterations = 2

    should_iterate = False
    iteration_reason = ""

    if quality_score < min_quality and iteration_count < max_iterations:
        should_iterate = True

        if gaps.get("high_severity", 0) > 0:
            iteration_reason = "High severity gaps in coverage"
        elif contradictions.get("critical", 0) > 0:
            iteration_reason = "Critical contradictions detected"
        else:
            iteration_reason = (
                f"Quality score ({quality_score:.1f}) below threshold ({min_quality})"
            )

    # Generate missing info list for iteration
    missing_info = []
    if should_iterate:
        for gap in gaps.get("items", [])[:5]:
            missing_info.append(gap.get("description", ""))

    return {
        "should_iterate": should_iterate,
        "iteration_reason": iteration_reason,
        "missing_info": missing_info,
        "iteration_count": iteration_count + 1,
    }


# ============================================================================
# Routing Functions
# ============================================================================


def route_quality_decision(state: OverallState) -> str:
    """
    Route based on quality check results.

    Args:
        state: Current workflow state

    Returns:
        "iterate" or "complete"
    """
    should_iterate = state.get("should_iterate", False)

    if should_iterate:
        logger.info("[ROUTE] Quality check failed - recommending iteration")
        return "iterate"
    else:
        logger.info("[ROUTE] Quality check passed - proceeding to output")
        return "complete"


# ============================================================================
# Subgraph Creation
# ============================================================================


def create_quality_subgraph(config: Optional[QualityConfig] = None) -> StateGraph:
    """
    Create the quality assurance subgraph.

    This subgraph:
    1. Extracts facts from analysis
    2. Detects contradictions
    3. Identifies information gaps
    4. Calculates quality score
    5. Determines if iteration is needed

    Args:
        config: Optional configuration

    Returns:
        Compiled StateGraph
    """
    if config is None:
        config = QualityConfig()

    graph = StateGraph(OverallState)

    # ========================================
    # Add Nodes
    # ========================================

    if config.enable_fact_extraction:
        graph.add_node("extract_facts", extract_facts_node)

    if config.enable_contradiction_detection:
        graph.add_node("detect_contradictions", detect_contradictions_node)

    if config.enable_gap_analysis:
        graph.add_node("identify_gaps", identify_gaps_node)

    if config.enable_logic_critic:
        graph.add_node("logic_critic", logic_critic_agent_node)

    graph.add_node("calculate_score", calculate_quality_score_node)
    graph.add_node("should_iterate", should_iterate_node)

    # ========================================
    # Define Edges
    # ========================================

    # Build edge sequence based on enabled components
    previous_node = None

    if config.enable_fact_extraction:
        if previous_node:
            graph.add_edge(previous_node, "extract_facts")
        else:
            graph.set_entry_point("extract_facts")
        previous_node = "extract_facts"

    if config.enable_contradiction_detection:
        if previous_node:
            graph.add_edge(previous_node, "detect_contradictions")
        else:
            graph.set_entry_point("detect_contradictions")
        previous_node = "detect_contradictions"

    if config.enable_gap_analysis:
        if previous_node:
            graph.add_edge(previous_node, "identify_gaps")
        else:
            graph.set_entry_point("identify_gaps")
        previous_node = "identify_gaps"

    if config.enable_logic_critic:
        if previous_node:
            graph.add_edge(previous_node, "logic_critic")
        else:
            graph.set_entry_point("logic_critic")
        previous_node = "logic_critic"

    # Always end with score calculation and iteration check
    if previous_node:
        graph.add_edge(previous_node, "calculate_score")
    else:
        graph.set_entry_point("calculate_score")

    graph.add_edge("calculate_score", "should_iterate")
    graph.add_edge("should_iterate", END)

    return graph.compile()


def create_simple_quality_subgraph() -> StateGraph:
    """
    Create a simplified quality check subgraph.

    Uses only the basic quality check without detailed analysis.

    Returns:
        Compiled StateGraph
    """
    graph = StateGraph(OverallState)

    def simple_quality_check(state: OverallState) -> Dict[str, Any]:
        """Simple quality check using existing function."""
        result = check_research_quality(
            company_name=state.get("company_name", "Unknown"),
            extracted_data=state.get("company_overview", ""),
            sources=state.get("sources", []),
        )

        iteration_count = state.get("iteration_count", 0) + 1

        return {
            "quality_score": result["quality_score"],
            "missing_info": result.get("missing_information", []),
            "iteration_count": iteration_count,
            "total_cost": state.get("total_cost", 0.0) + result.get("cost", 0.0),
        }

    graph.add_node("quality_check", simple_quality_check)

    graph.set_entry_point("quality_check")
    graph.add_edge("quality_check", END)

    return graph.compile()
