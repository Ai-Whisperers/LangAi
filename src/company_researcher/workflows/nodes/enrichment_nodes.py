"""
Enrichment Nodes for Research Workflow

This module contains nodes responsible for data enrichment:
- news_sentiment_node: Analyze news sentiment from search results (using AI)
- competitive_analysis_node: Generate competitive matrix analysis
- risk_assessment_node: Quantify risks for the company
"""

from typing import Dict, Any, List

from ...state import OverallState
# AI-powered sentiment analysis
from ...ai.sentiment import get_sentiment_analyzer, SentimentLevel
from ...agents.research.competitive_matrix import create_competitive_matrix
from ...agents.research.risk_quantifier import create_risk_quantifier


def news_sentiment_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 6: Analyze news sentiment from search results using AI.

    Args:
        state: Current workflow state

    Returns:
        State update with news sentiment profile
    """
    print("\n[NODE] Analyzing news sentiment with AI...")

    company_name = state["company_name"]
    search_results = state.get("search_results", [])

    if not search_results:
        print("[WARN] No search results for sentiment analysis")
        return {"news_sentiment": None}

    # Get AI sentiment analyzer
    analyzer = get_sentiment_analyzer()

    # Convert search results to articles format expected by analyzer
    articles = []
    for result in search_results:
        if isinstance(result, dict):
            articles.append({
                "content": result.get("content") or result.get("snippet") or result.get("text", ""),
                "url": result.get("url", ""),
                "title": result.get("title", "")
            })
        elif isinstance(result, str):
            articles.append({"content": result})

    # Analyze sentiment batch
    results = analyzer.analyze_batch(articles, company_name, max_articles=20)

    if not results:
        print("[WARN] No sentiment results generated")
        return {"news_sentiment": None}

    # Aggregate sentiment across all articles
    aggregation = analyzer.aggregate_sentiment(results)

    # Build sentiment dict in compatible format
    sentiment_dict = {
        "company_name": company_name,
        "total_articles": aggregation.article_count,
        "sentiment_score": aggregation.overall_score,
        "sentiment_level": aggregation.overall_sentiment.value if isinstance(aggregation.overall_sentiment, SentimentLevel) else aggregation.overall_sentiment,
        "sentiment_trend": "stable",  # AI doesn't track trend over time
        "key_topics": [],  # Would need additional analysis
        "positive_highlights": aggregation.top_positive_factors,
        "negative_highlights": aggregation.top_negative_factors,
        "confidence": aggregation.confidence,
        "category_breakdown": aggregation.sentiment_distribution,
        # Additional AI-provided fields
        "positive_ratio": aggregation.positive_ratio,
        "negative_ratio": aggregation.negative_ratio,
        "neutral_ratio": aggregation.neutral_ratio,
    }

    print(f"[OK] AI Sentiment analysis complete: {sentiment_dict['sentiment_level']} ({sentiment_dict['sentiment_score']:.2f})")

    return {
        "news_sentiment": sentiment_dict
    }


def competitive_analysis_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 7: Generate competitive matrix analysis.

    Args:
        state: Current workflow state

    Returns:
        State update with competitive matrix
    """
    print("\n[NODE] Generating competitive analysis...")

    company_name = state["company_name"]

    # Extract company data from state
    company_data = {
        "name": company_name,
        "revenue": state.get("key_metrics", {}).get("revenue") if state.get("key_metrics") else None,
        "market_share": state.get("key_metrics", {}).get("market_share") if state.get("key_metrics") else None,
        "employees": state.get("key_metrics", {}).get("employees") if state.get("key_metrics") else None,
    }

    # Extract competitors from state
    competitors_data = []
    competitors_list = state.get("competitors", []) or []
    for comp_name in competitors_list[:5]:  # Limit to 5 competitors
        competitors_data.append({
            "name": comp_name,
            "revenue": None,
            "market_share": None,
        })

    # Generate competitive matrix using factory function
    matrix = create_competitive_matrix(
        company_name=company_name,
        company_data=company_data,
        competitors_data=competitors_data
    )

    # Convert to dict for state storage
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
        "dimensions": [d.value for d in matrix.dimensions],
        "strategic_groups": matrix.strategic_groups,
        "insights": matrix.insights,
        "recommendations": matrix.recommendations,
    }

    print(f"[OK] Competitive analysis complete: {len(matrix.insights)} insights generated")

    return {
        "competitive_matrix": matrix_dict
    }


def risk_assessment_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 8: Quantify risks for the company.

    Args:
        state: Current workflow state

    Returns:
        State update with risk profile
    """
    print("\n[NODE] Quantifying risks...")

    # Build company data from state
    company_data = {
        "name": state["company_name"],
        "overview": state.get("company_overview", ""),
        "notes": state.get("notes", []),
        "key_metrics": state.get("key_metrics", {}),
        "competitors": state.get("competitors", []),
        "key_insights": state.get("key_insights", []),
        "region": state.get("detected_region"),
    }

    # Generate risk assessment
    quantifier = create_risk_quantifier()
    risk_profile = quantifier.assess_risks(company_data)

    # Convert to dict for state storage
    profile_dict = {
        "company_name": risk_profile.company_name,
        "overall_score": risk_profile.overall_score,
        "grade": risk_profile.grade,
        "risks": [
            {
                "category": r.category.value,
                "description": r.description,
                "severity": r.severity.value,
                "probability": r.probability.value if r.probability else None,
                "impact_score": r.impact_score,
                "mitigation": r.mitigation,
            }
            for r in risk_profile.risks
        ],
        "category_scores": {k.value: v for k, v in risk_profile.category_scores.items()},
        "risk_adjusted_metrics": risk_profile.risk_adjusted_metrics,
    }

    print(f"[OK] Risk assessment complete: Grade {risk_profile.grade}, Score {risk_profile.overall_score:.1f}/100")

    return {
        "risk_profile": profile_dict
    }
