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

from typing import Any, Dict, List

from langgraph.graph import END, StateGraph

from ..agents.research.competitive_matrix import create_competitive_matrix

# Research modules
from ..agents.research.multilingual_search import create_multilingual_generator
from ..config import get_config

# Import SearchRouter for multi-provider search with fallback
from ..integrations.search_router import get_search_router

# Quality modules
from ..quality import (
    SourceQualityAssessor,
    check_research_quality,
    detect_contradictions,
    score_facts,
    validate_research_data,
)

# Source relevance filtering (market share validation is in nodes/comprehensive_analysis_nodes.py)
from ..quality.source_assessor import AISourceRelevanceFilter

# Fact extraction from research module
from ..research import extract_facts

# Autonomous Discovery - enables learning from previous research
from ..research.autonomous_discovery import (
    analyze_research_gaps,
    detect_inconsistencies,
    find_relevant_cross_company_data,
    load_all_previous_research,
    load_previous_research,
)
from ..state import InputState, OutputState, OverallState, create_initial_state, create_output_state
from ..utils import get_logger

# Import nodes from modular package
from .nodes import (  # Data collection; Analysis; Enrichment; Output
    brand_analysis_node,
    core_analysis_node,
    enrich_executive_summary_node,
    esg_analysis_node,
    extract_data_node,
    fetch_financial_data_node,
    fetch_news_node,
    financial_analysis_node,
    financial_comparison_node,
    investment_thesis_node,
    market_analysis_node,
    news_sentiment_node,
    risk_assessment_node,
    save_comprehensive_report_node,
    should_continue_research,
)

logger = get_logger(__name__)


# =============================================================================
# Autonomous Discovery Node - Phase 0
# =============================================================================


def discovery_node(state: OverallState) -> Dict[str, Any]:
    """
    Phase 0: Autonomous Discovery - Learns from previous research before starting.

    This node:
    1. Loads previous research for context (if available)
    2. Identifies gaps in previous research
    3. Checks other companies for relevant cross-references
    4. Detects inconsistencies across research
    5. Builds context to guide query generation

    Returns:
        State update with discovery context
    """
    company_name = state["company_name"]
    logger.info(f"\n[DISCOVERY] Starting autonomous discovery for: {company_name}")

    # Step 1: Load previous research
    previous = load_previous_research(company_name)

    gap_analysis = None
    missing_fields: List[str] = []
    cross_company_data = []
    inconsistencies = []
    previous_quality = 0.0

    if previous:
        logger.info(
            f"[DISCOVERY] Found previous research (Quality: {previous.quality_score:.1f}/100)"
        )
        previous_quality = previous.quality_score

        # Step 2: Analyze gaps
        gap_analysis = analyze_research_gaps(previous)
        missing_fields = gap_analysis.priority_fields  # Focus on high-priority gaps
        logger.info(
            f"[DISCOVERY] Gap analysis: {gap_analysis.found_fields}/{gap_analysis.total_fields} fields found"
        )
        logger.info(f"[DISCOVERY] Priority gaps: {missing_fields}")

        # Step 3: Load cross-company data
        all_research = load_all_previous_research()
        if len(all_research) > 1:
            cross_company_data = find_relevant_cross_company_data(company_name, all_research)
            logger.info(f"[DISCOVERY] Found {len(cross_company_data)} cross-company references")

            # Step 4: Detect inconsistencies
            inconsistencies = detect_inconsistencies(
                company_name, previous.extracted_fields, all_research
            )
            if inconsistencies:
                logger.warning(
                    f"[DISCOVERY] Found {len(inconsistencies)} potential inconsistencies!"
                )
                for inc in inconsistencies[:3]:
                    logger.warning(f"  - {inc.field_name}: {inc.explanation}")
    else:
        logger.info("[DISCOVERY] No previous research found - starting fresh")
        # Default missing fields for first-time research
        missing_fields = ["ceo", "revenue", "market_share", "subscribers", "competitors"]

    # Build discovery context for downstream nodes
    discovery_context = {
        "has_previous_research": previous is not None,
        "previous_quality_score": previous_quality,
        "gap_analysis": gap_analysis.to_dict() if gap_analysis else None,
        "priority_gaps": missing_fields,
        "cross_company_data": [
            {
                "source": d.source_company,
                "field": d.field_name,
                "value": d.value,
                "context": d.context[:200] if d.context else "",
                "confidence": d.confidence,
            }
            for d in cross_company_data[:5]  # Limit to top 5
        ],
        "inconsistencies": [
            {"field": i.field_name, "severity": i.severity, "explanation": i.explanation}
            for i in inconsistencies
        ],
        "previous_extracted_fields": previous.extracted_fields if previous else {},
    }

    logger.info(f"[DISCOVERY] Complete - focusing on {len(missing_fields)} priority fields")

    return {
        "discovery_context": discovery_context,
        "missing_info": missing_fields,  # This will guide query generation
    }


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

    # Generate multilingual queries with brand disambiguation
    # This helps resolve ambiguous company names like "Personal" → "Núcleo S.A. telecomunicaciones"
    ml_queries = ml_generator.generate_queries(
        company_name=company_name,
        region=region,
        language=language,
        max_queries=config.num_search_queries,
        use_disambiguation=True,  # Enable brand name disambiguation
    )

    queries = [mq.query for mq in ml_queries]

    # Add parent company queries
    parent_queries = ml_generator.get_parent_company_queries(company_name, max_queries=3)
    if parent_queries:
        queries.extend(parent_queries)

    # Add specialized queries for different aspects
    # CEO/leadership is critical - add multiple CEO-specific queries
    specialized_queries = [
        f"{company_name} ESG sustainability environmental social governance",
        f"{company_name} brand reputation customer reviews",
        f"{company_name} leadership management team executives",
        f"who is the CEO of {company_name}",  # Direct CEO query
        f"{company_name} CEO appointed 2024",  # Recent appointment query
        f"{company_name} gerente general director",  # LATAM executive title
        f"{company_name} patents technology innovation",
        f"{company_name} partnerships alliances acquisitions",
    ]
    queries.extend(specialized_queries)

    # Limit total queries
    queries = queries[: config.num_search_queries + 8]

    logger.info(f"[OK] Generated {len(queries)} queries")

    return {
        "search_queries": queries,
        "detected_region": region.value,
        "detected_language": language.value,
    }


def _is_executive_query(query: str) -> bool:
    """Check if query is looking for executive/leadership information."""
    executive_keywords = [
        "ceo",
        "chief executive",
        "chief officer",
        "leadership",
        "management team",
        "executives",
        "director",
        "gerente general",
        "presidente",
        "board of directors",
        "appointed",
        "named as",
        "c-suite",
        "founder",
        "cfo",
        "cto",
        "coo",
    ]
    query_lower = query.lower()
    return any(kw in query_lower for kw in executive_keywords)


def search_node(state: OverallState) -> Dict[str, Any]:
    """
    Execute web searches using SearchRouter with automatic fallback.

    Fallback chain (premium tier): DuckDuckGo → Brave → Serper → Tavily
    Executive queries use min_results=5 to force escalation to Serper for better data.
    """
    config = get_config()
    router = get_search_router()

    logger.info(f"[NODE] Executing {len(state['search_queries'])} searches (with fallback)...")
    logger.info(f"[INFO] Available providers: {router._get_available_providers()}")

    all_results = []
    total_search_cost = 0.0

    for query in state["search_queries"]:
        try:
            # Executive queries need more results to force escalation to Serper
            # (Brave often returns only 3 results without executive data)
            is_executive = _is_executive_query(query)
            min_results_threshold = 5 if is_executive else 3

            # Use premium tier for automatic fallback
            response = router.search(
                query=query,
                quality="premium",
                max_results=config.search_results_per_query,
                min_results=min_results_threshold,
            )

            if response.success and response.results:
                # Convert SearchResult objects to dicts
                results = [r.to_dict() for r in response.results]
                all_results.append(results)
                total_search_cost += response.cost
                provider_info = f"[EXEC]" if is_executive else ""
                logger.debug(
                    f"[OK]{provider_info} Query '{query[:50]}...' via {response.provider}: {len(results)} results"
                )
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
                sources.append(
                    {
                        "title": result.get("title", ""),
                        "url": url,
                        "score": result.get("score", 0.0),
                    }
                )

    # Apply AI source relevance filtering to remove irrelevant sources
    # This filters out "Paraguay history" when researching "Personal Paraguay telecom"
    company_name = state["company_name"]
    relevance_filter = AISourceRelevanceFilter()
    original_count = len(search_results)

    # Filter sources for relevance to the research target
    search_results = relevance_filter.ai_relevance_check(
        sources=search_results,
        research_target=company_name,
        industry="telecom",  # Default to telecom for this project
        company_context=state.get("discovery_context", {}),
    )

    if original_count != len(search_results):
        logger.info(f"[FILTER] Removed {original_count - len(search_results)} irrelevant sources")

    # Rebuild sources list from filtered results
    sources = [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "score": r.get("relevance_score", 0.5),
        }
        for r in search_results
    ]

    # Limit results
    search_results = search_results[: config.max_search_results]
    sources = sources[: config.max_search_results]

    # Log search stats
    stats = router.get_stats()
    logger.info(f"[OK] Found {len(search_results)} unique results")
    logger.info(f"[STATS] Search providers used: {stats['by_provider']}")

    return {
        "search_results": search_results,
        "sources": sources,
        "total_cost": state.get("total_cost", 0.0) + total_search_cost,
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
        sources=state.get("sources", []),
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
            contradictions = (
                [
                    {
                        "claim1": c.claim_a,
                        "claim2": c.claim_b,
                        "severity": c.severity.value if hasattr(c, "severity") else "medium",
                    }
                    for c in contradiction_report.contradictions
                ]
                if hasattr(contradiction_report, "contradictions")
                else []
            )

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
            validation_result = validate_research_data(state.get("company_overview", ""), sources)
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
                "average_confidence": (
                    sum(f.confidence for f in scored) / len(scored) if scored else 0
                ),
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
                # Extract URL from source (handles both dict and string)
                url = source.get("url", source) if isinstance(source, dict) else source
                if not url or not isinstance(url, str):
                    continue
                quality, score = assessor.assess(url)
                tier = quality.value if hasattr(quality, "value") else str(quality)
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
            source_quality = tier_counts
    except Exception as e:
        logger.warning(f"Source quality assessment failed: {e}")

    logger.info(f"[QUALITY] Final score: {quality_score:.1f}/100")

    return {
        "quality_score": max(0, min(100, quality_score)),
        "missing_info": missing_info,
        "contradictions": contradictions,
        "validation_result": (
            validation_result.__dict__
            if validation_result and hasattr(validation_result, "__dict__")
            else None
        ),
        "confidence_scores": confidence_scores,
        "source_quality": source_quality,
        "iteration_count": state.get("iteration_count", 0) + 1,
        "total_cost": state.get("total_cost", 0.0) + quality_result["cost"],
        "total_tokens": {
            "input": state.get("total_tokens", {"input": 0, "output": 0})["input"]
            + quality_result["tokens"]["input"],
            "output": state.get("total_tokens", {"input": 0, "output": 0})["output"]
            + quality_result["tokens"]["output"],
        },
    }


def competitive_matrix_node(state: OverallState) -> Dict[str, Any]:
    """
    Generate competitive matrix analysis.
    """
    logger.info("[NODE] Generating competitive matrix...")

    company_name = state["company_name"]
    company_data = {
        "name": company_name,
        "revenue": (
            state.get("financial_data", {}).get("revenue") if state.get("financial_data") else None
        ),
        "market_share": (
            state.get("key_metrics", {}).get("market_share") if state.get("key_metrics") else None
        ),
    }

    competitors_data = []
    competitors_list = state.get("competitors", []) or []
    for comp_name in competitors_list[:5]:
        competitors_data.append({"name": comp_name})

    matrix = create_competitive_matrix(
        company_name=company_name, company_data=company_data, competitors_data=competitors_data
    )

    # Get company scores from matrix_data
    company_scores = matrix.matrix_data.get(matrix.company_name, {})

    matrix_dict = {
        "company": {
            "name": matrix.company_name,
            "scores": company_scores,
            "position": None,  # Position is in strategic_groups, not on company
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
        "strategic_groups": matrix.strategic_groups,
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

    # Phase 0: Autonomous Discovery (learns from previous research)
    workflow.add_node("discovery", discovery_node)

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
    workflow.add_node("financial_comparison", financial_comparison_node)
    workflow.add_node("risk_assessment", risk_assessment_node)
    workflow.add_node("investment_thesis", investment_thesis_node)

    # Phase 5: Output (with cross-section enrichment)
    workflow.add_node("enrich_summary", enrich_executive_summary_node)
    workflow.add_node("save_report", save_comprehensive_report_node)

    # Define edges - Phase 0 (Discovery)
    workflow.set_entry_point("discovery")
    workflow.add_edge("discovery", "generate_queries")

    # Phase 1 edges
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
        {"iterate": "generate_queries", "finish": "competitive_matrix"},
    )

    # Phase 4
    workflow.add_edge("competitive_matrix", "financial_comparison")
    workflow.add_edge("financial_comparison", "risk_assessment")
    workflow.add_edge("risk_assessment", "investment_thesis")

    # Phase 5 (with cross-section enrichment before final report)
    workflow.add_edge("investment_thesis", "enrich_summary")
    workflow.add_edge("enrich_summary", "save_report")
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
    # Increase recursion limit for complex multi-iteration workflows
    final_state = workflow.invoke(initial_state, config={"recursion_limit": 50})
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
