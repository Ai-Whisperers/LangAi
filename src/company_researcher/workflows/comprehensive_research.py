"""
Comprehensive Research Workflow - Full Feature Integration.

This workflow integrates ALL available agents and features:
- Core: Researcher, Analyst, Synthesizer
- Financial: Financial Analyst, Investment Analyst, Enhanced Financial
- Market: Market Analyst, Competitive Matrix, Competitor Scout
- Research: Deep Research, Reasoning, Multilingual, News Sentiment
- Specialized: ESG, Brand Auditor, Sales Intelligence, Social Media
- Quality: Cross-Source Validation, Contradiction Detection, Confidence Scoring

Workflow Architecture:
    START → Data Collection → Parallel Analysis → Quality Assurance
    → Advanced Analysis → Synthesis & Output → END
"""

import logging
from typing import Dict, Any

from langgraph.graph import StateGraph, END

# Import SearchRouter for multi-provider search with fallback
from ..integrations.search_router import get_search_router, SearchRouter

from ..state import OverallState, InputState, OutputState, create_initial_state, create_output_state
from ..config import get_config

# Quality modules
from ..quality import (
    check_research_quality,
    validate_research_data,
    detect_contradictions,
    score_facts,
    SourceQualityAssessor,
)
# Fact extraction from research module
from ..research import extract_facts

# Research modules
from ..agents.research.multilingual_search import (
    create_multilingual_generator,
)
from ..agents.research.competitive_matrix import create_competitive_matrix

# Import nodes from modular package
from .nodes import (
    # Data collection
    fetch_financial_data_node,
    fetch_news_node,
    # Analysis
    core_analysis_node,
    financial_analysis_node,
    market_analysis_node,
    esg_analysis_node,
    brand_analysis_node,
    extract_data_node,
    should_continue_research,
    # Enrichment
    news_sentiment_node,
    risk_assessment_node,
    # Output
    investment_thesis_node,
    save_comprehensive_report_node,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Comprehensive-Specific Nodes
# =============================================================================

def generate_queries_node(state: OverallState) -> Dict[str, Any]:
    """
    Generate multilingual search queries for comprehensive coverage.

    Uses the MultilingualSearchGenerator for region-aware query generation.
    """
    config = get_config()
    company_name = state["company_name"]

    logger.info(f"[NODE] Generating queries for: {company_name}")

    # Use multilingual search generator
    ml_generator = create_multilingual_generator()
    region, language = ml_generator.detect_region(company_name)

    logger.info(f"[INFO] Detected region: {region.value}, language: {language.value}")

    # Generate multilingual queries
    ml_queries = ml_generator.generate_queries(
        company_name=company_name,
        region=region,
        language=language,
        max_queries=config.num_search_queries
    )

    queries = [mq.query for mq in ml_queries]

    # Add parent company queries
    parent_queries = ml_generator.get_parent_company_queries(company_name, max_queries=3)
    if parent_queries:
        queries.extend(parent_queries)

    # Add specialized queries for different aspects
    specialized_queries = [
        f"{company_name} ESG sustainability environmental social governance",
        f"{company_name} brand reputation customer reviews",
        f"{company_name} leadership management team executives",
        f"{company_name} patents technology innovation",
        f"{company_name} partnerships alliances acquisitions",
    ]
    queries.extend(specialized_queries)

    # Limit total queries
    queries = queries[:config.num_search_queries + 8]

    logger.info(f"[OK] Generated {len(queries)} queries")

    return {
        "search_queries": queries,
        "detected_region": region.value,
        "detected_language": language.value
    }


def search_node(state: OverallState) -> Dict[str, Any]:
    """
    Execute web searches using SearchRouter with automatic fallback.

    Fallback chain (premium tier): Tavily → Serper → DuckDuckGo
    """
    config = get_config()
    router = get_search_router()

    logger.info(f"[NODE] Executing {len(state['search_queries'])} searches (with fallback)...")
    logger.info(f"[INFO] Available providers: {router._get_available_providers()}")

    all_results = []
    total_search_cost = 0.0

    for query in state["search_queries"]:
        try:
            # Use premium tier for automatic fallback: Tavily → Serper → DuckDuckGo
            response = router.search(
                query=query,
                quality="premium",
                max_results=config.search_results_per_query
            )

            if response.success and response.results:
                # Convert SearchResult objects to dicts
                results = [r.to_dict() for r in response.results]
                all_results.append(results)
                total_search_cost += response.cost
                logger.debug(f"[OK] Query '{query[:50]}...' via {response.provider}: {len(results)} results")
            else:
                logger.warning(f"Search failed for '{query}': {response.error}")

        except Exception as e:
            logger.warning(f"Search error for '{query}': {e}")
            continue

    # Flatten and deduplicate results
    search_results = []
    sources = []
    seen_urls = set()

    for results in all_results:
        for result in results:
            url = result.get("url", "")
            if url not in seen_urls:
                seen_urls.add(url)
                search_results.append(result)
                sources.append({
                    "title": result.get("title", ""),
                    "url": url,
                    "score": result.get("score", 0.0)
                })

    # Limit results
    search_results = search_results[:config.max_search_results]
    sources = sources[:config.max_search_results]

    # Log search stats
    stats = router.get_stats()
    logger.info(f"[OK] Found {len(search_results)} unique results")
    logger.info(f"[STATS] Search providers used: {stats['by_provider']}")

    return {
        "search_results": search_results,
        "sources": sources,
        "total_cost": state.get("total_cost", 0.0) + total_search_cost
    }


def quality_check_node(state: OverallState) -> Dict[str, Any]:
    """
    Comprehensive quality check with multiple quality modules.
    """
    logger.info("[NODE] Running quality checks...")

    # Basic quality check
    quality_result = check_research_quality(
        company_name=state["company_name"],
        extracted_data=state.get("company_overview", ""),
        sources=state.get("sources", [])
    )

    quality_score = quality_result["quality_score"]
    missing_info = quality_result["missing_information"]

    logger.info(f"[QUALITY] Base score: {quality_score:.1f}/100")

    # Run contradiction detection
    contradictions = []
    try:
        agent_outputs = state.get("agent_outputs", {})
        if agent_outputs:
            contradiction_report = detect_contradictions(agent_outputs)
            contradictions = [
                {
                    "claim1": c.claim_a,
                    "claim2": c.claim_b,
                    "severity": c.severity.value if hasattr(c, "severity") else "medium"
                }
                for c in contradiction_report.contradictions
            ] if hasattr(contradiction_report, "contradictions") else []

            if contradictions:
                logger.info(f"[QUALITY] Found {len(contradictions)} contradictions")
                # Penalize score for contradictions
                quality_score -= len(contradictions) * 2
    except Exception as e:
        logger.warning(f"Contradiction detection failed: {e}")

    # Run cross-source validation
    validation_result = None
    try:
        sources = state.get("sources", [])
        if sources:
            validation_result = validate_research_data(
                state.get("company_overview", ""),
                sources
            )
            if validation_result:
                logger.info(f"[QUALITY] Validated {validation_result.validated_count} facts")
    except Exception as e:
        logger.warning(f"Cross-source validation failed: {e}")

    # Confidence scoring
    confidence_scores = {}
    try:
        facts = extract_facts(state.get("company_overview", ""))
        if facts:
            scored = score_facts(facts, state.get("sources", []))
            confidence_scores = {
                "average_confidence": sum(f.confidence for f in scored) / len(scored) if scored else 0,
                "high_confidence_count": sum(1 for f in scored if f.confidence > 0.7),
                "low_confidence_count": sum(1 for f in scored if f.confidence < 0.3),
            }
    except Exception as e:
        logger.warning(f"Confidence scoring failed: {e}")

    # Source quality assessment
    source_quality = {}
    try:
        assessor = SourceQualityAssessor()
        sources = state.get("sources", [])
        if sources:
            tier_counts = {}
            for source in sources:
                quality = assessor.assess(source)
                tier = quality.tier if hasattr(quality, "tier") else "unknown"
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
            source_quality = tier_counts
    except Exception as e:
        logger.warning(f"Source quality assessment failed: {e}")

    logger.info(f"[QUALITY] Final score: {quality_score:.1f}/100")

    return {
        "quality_score": max(0, min(100, quality_score)),
        "missing_info": missing_info,
        "contradictions": contradictions,
        "validation_result": validation_result.__dict__ if validation_result and hasattr(validation_result, "__dict__") else None,
        "confidence_scores": confidence_scores,
        "source_quality": source_quality,
        "iteration_count": state.get("iteration_count", 0) + 1,
        "total_cost": state.get("total_cost", 0.0) + quality_result["cost"],
        "total_tokens": {
            "input": state.get("total_tokens", {"input": 0, "output": 0})["input"] + quality_result["tokens"]["input"],
            "output": state.get("total_tokens", {"input": 0, "output": 0})["output"] + quality_result["tokens"]["output"]
        }
    }


def competitive_matrix_node(state: OverallState) -> Dict[str, Any]:
    """
    Generate competitive matrix analysis.
    """
    logger.info("[NODE] Generating competitive matrix...")

    company_name = state["company_name"]
    company_data = {
        "name": company_name,
        "revenue": state.get("financial_data", {}).get("revenue") if state.get("financial_data") else None,
        "market_share": state.get("key_metrics", {}).get("market_share") if state.get("key_metrics") else None,
    }

    competitors_data = []
    competitors_list = state.get("competitors", []) or []
    for comp_name in competitors_list[:5]:
        competitors_data.append({"name": comp_name})

    matrix = create_competitive_matrix(
        company_name=company_name,
        company_data=company_data,
        competitors_data=competitors_data
    )

    matrix_dict = {
        "company": {
            "name": matrix.company.name,
            "scores": matrix.company.scores,
            "position": matrix.company.position.value if matrix.company.position else None,
        },
        "competitors": [
            {
                "name": c.name,
                "scores": c.scores,
                "position": c.position.value if c.position else None,
            }
            for c in matrix.competitors
        ],
        "insights": matrix.insights,
        "recommendations": matrix.recommendations,
    }

    logger.info(f"[OK] Competitive matrix generated with {len(matrix.competitors)} competitors")

    return {"competitive_matrix": matrix_dict}


# =============================================================================
# Workflow Builder
# =============================================================================

def create_comprehensive_workflow() -> StateGraph:
    """
    Create the comprehensive LangGraph workflow.

    This workflow uses all available agents and features.
    """
    workflow = StateGraph(OverallState, input=InputState, output=OutputState)

    # Phase 1: Data Collection
    workflow.add_node("generate_queries", generate_queries_node)
    workflow.add_node("search", search_node)
    workflow.add_node("fetch_financial", fetch_financial_data_node)
    workflow.add_node("fetch_news", fetch_news_node)

    # Phase 2: Analysis
    workflow.add_node("core_analysis", core_analysis_node)
    workflow.add_node("financial_analysis", financial_analysis_node)
    workflow.add_node("market_analysis", market_analysis_node)
    workflow.add_node("esg_analysis", esg_analysis_node)
    workflow.add_node("brand_analysis", brand_analysis_node)
    workflow.add_node("news_sentiment", news_sentiment_node)

    # Phase 3: Quality
    workflow.add_node("extract_data", extract_data_node)
    workflow.add_node("quality_check", quality_check_node)

    # Phase 4: Advanced Analysis
    workflow.add_node("competitive_matrix", competitive_matrix_node)
    workflow.add_node("risk_assessment", risk_assessment_node)
    workflow.add_node("investment_thesis", investment_thesis_node)

    # Phase 5: Output
    workflow.add_node("save_report", save_comprehensive_report_node)

    # Define edges - Phase 1
    workflow.set_entry_point("generate_queries")
    workflow.add_edge("generate_queries", "search")
    workflow.add_edge("search", "fetch_financial")
    workflow.add_edge("fetch_financial", "fetch_news")

    # Phase 2 - Parallel would be ideal but keeping sequential for simplicity
    workflow.add_edge("fetch_news", "core_analysis")
    workflow.add_edge("core_analysis", "financial_analysis")
    workflow.add_edge("financial_analysis", "market_analysis")
    workflow.add_edge("market_analysis", "esg_analysis")
    workflow.add_edge("esg_analysis", "brand_analysis")
    workflow.add_edge("brand_analysis", "news_sentiment")

    # Phase 3
    workflow.add_edge("news_sentiment", "extract_data")
    workflow.add_edge("extract_data", "quality_check")

    # Conditional edge for iteration
    workflow.add_conditional_edges(
        "quality_check",
        should_continue_research,
        {
            "iterate": "generate_queries",
            "finish": "competitive_matrix"
        }
    )

    # Phase 4
    workflow.add_edge("competitive_matrix", "risk_assessment")
    workflow.add_edge("risk_assessment", "investment_thesis")

    # Phase 5
    workflow.add_edge("investment_thesis", "save_report")
    workflow.add_edge("save_report", END)

    return workflow.compile()


# =============================================================================
# Main Entry Point
# =============================================================================

def research_company_comprehensive(company_name: str) -> OutputState:
    """
    Research a company using the comprehensive workflow.

    This uses all available agents, integrations, and quality modules.

    Args:
        company_name: Name of company to research

    Returns:
        OutputState with comprehensive results
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"[COMPREHENSIVE] Researching: {company_name}")
    logger.info(f"{'='*60}")

    workflow = create_comprehensive_workflow()
    initial_state = create_initial_state(company_name)
    final_state = workflow.invoke(initial_state)
    output = create_output_state(final_state)

    logger.info(f"\n{'='*60}")
    logger.info("[RESULTS] Comprehensive Research Complete")
    logger.info(f"{'='*60}")
    logger.info(f"Report: {output['report_path']}")
    logger.info(f"Duration: {output['metrics']['duration_seconds']:.1f}s")
    logger.info(f"Cost: ${output['metrics']['cost_usd']:.4f}")
    logger.info(f"Quality: {output['metrics'].get('quality_score', 0):.1f}/100")
    logger.info(f"{'='*60}\n")

    return output
