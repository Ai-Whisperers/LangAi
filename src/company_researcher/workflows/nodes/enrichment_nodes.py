"""
Enrichment Nodes for Research Workflow

This module contains nodes responsible for data enrichment:
- news_sentiment_node: Analyze news sentiment from search results (using AI)
- competitive_analysis_node: Generate competitive matrix analysis
- risk_assessment_node: Quantify risks for the company
"""

from typing import Any, Dict

from ...agents.research.competitive_matrix import (
    FinancialMetric,
    create_competitive_matrix,
    create_financial_comparison,
)
from ...agents.research.risk_quantifier import create_risk_quantifier

# AI-powered sentiment analysis
from ...ai.sentiment import SentimentLevel, get_sentiment_analyzer
from ...state import OverallState


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
            articles.append(
                {
                    "content": result.get("content")
                    or result.get("snippet")
                    or result.get("text", ""),
                    "url": result.get("url", ""),
                    "title": result.get("title", ""),
                }
            )
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
        "sentiment_level": (
            aggregation.overall_sentiment.value
            if isinstance(aggregation.overall_sentiment, SentimentLevel)
            else aggregation.overall_sentiment
        ),
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

    print(
        f"[OK] AI Sentiment analysis complete: {sentiment_dict['sentiment_level']} ({sentiment_dict['sentiment_score']:.2f})"
    )

    return {"news_sentiment": sentiment_dict}


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
        "revenue": (
            state.get("key_metrics", {}).get("revenue") if state.get("key_metrics") else None
        ),
        "market_share": (
            state.get("key_metrics", {}).get("market_share") if state.get("key_metrics") else None
        ),
        "employees": (
            state.get("key_metrics", {}).get("employees") if state.get("key_metrics") else None
        ),
    }

    # Extract competitors from state
    competitors_data = []
    competitors_list = state.get("competitors", []) or []
    for comp_name in competitors_list[:5]:  # Limit to 5 competitors
        competitors_data.append(
            {
                "name": comp_name,
                "revenue": None,
                "market_share": None,
            }
        )

    # Generate competitive matrix using factory function
    matrix = create_competitive_matrix(
        company_name=company_name, company_data=company_data, competitors_data=competitors_data
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

    return {"competitive_matrix": matrix_dict}


def risk_assessment_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 8: Quantify risks for the company.

    Args:
        state: Current workflow state

    Returns:
        State update with risk profile
    """
    print("\n[NODE] Quantifying risks...")

    company_name = state["company_name"]

    # Build company data from state (financial/operational metrics)
    company_data = {
        "debt_to_equity": (
            state.get("key_metrics", {}).get("debt_to_equity") if state.get("key_metrics") else None
        ),
        "profit_margin": (
            state.get("key_metrics", {}).get("profit_margin") if state.get("key_metrics") else None
        ),
        "revenue_growth": (
            state.get("key_metrics", {}).get("revenue_growth") if state.get("key_metrics") else None
        ),
        "pe_ratio": (
            state.get("key_metrics", {}).get("pe_ratio") if state.get("key_metrics") else None
        ),
        "employee_turnover": (
            state.get("key_metrics", {}).get("employee_turnover")
            if state.get("key_metrics")
            else None
        ),
    }

    # Build market data from state
    market_data = {
        "market_share": (
            state.get("key_metrics", {}).get("market_share") if state.get("key_metrics") else None
        ),
        "competitors": state.get("competitors", []),
        "market_growth": (
            state.get("key_metrics", {}).get("market_growth") if state.get("key_metrics") else None
        ),
    }

    # Combine text content for risk indicator extraction
    content_parts = []
    if state.get("company_overview"):
        content_parts.append(state["company_overview"])
    for note in state.get("notes", []) or []:
        if isinstance(note, str):
            content_parts.append(note)
    content = "\n".join(content_parts) if content_parts else None

    # Generate risk assessment with correct signature
    quantifier = create_risk_quantifier()
    risk_profile = quantifier.assess_risks(
        company_name=company_name,
        company_data=company_data,
        market_data=market_data,
        content=content,
    )

    # Convert to dict for state storage (using correct attribute names)
    profile_dict = {
        "company_name": risk_profile.company_name,
        "overall_score": risk_profile.overall_risk_score,
        "grade": risk_profile.risk_grade,
        "risks": [
            {
                "name": r.name,
                "category": r.category.value,
                "description": r.description,
                "level": r.level.value,
                "probability": r.probability.value if r.probability else None,
                "impact_score": r.impact_score,
                "likelihood_score": r.likelihood_score,
                "risk_score": r.risk_score,
                "mitigation": r.mitigation,
                "trend": r.trend,
            }
            for r in risk_profile.risks
        ],
        "risk_by_category": {
            k: [r.name for r in v] for k, v in risk_profile.risk_by_category.items()
        },
        "risk_matrix": risk_profile.risk_matrix,
        "key_risks": risk_profile.key_risks,
        "risk_adjusted_metrics": risk_profile.risk_adjusted_metrics,
        "recommendations": risk_profile.recommendations,
        "summary": risk_profile.summary,
    }

    print(
        f"[OK] Risk assessment complete: Grade {risk_profile.risk_grade}, Score {risk_profile.overall_risk_score:.1f}/100"
    )

    return {"risk_profile": profile_dict}


def financial_comparison_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 9: Generate structured financial comparison with competitors.

    Args:
        state: Current workflow state

    Returns:
        State update with financial comparison table
    """
    print("\n[NODE] Generating financial comparison table...")

    company_name = state["company_name"]

    # Build company financial data from state
    key_metrics = state.get("key_metrics", {}) or {}
    company_data = {
        "name": company_name,
        "revenue": key_metrics.get("revenue"),
        "revenue_growth": key_metrics.get("revenue_growth"),
        "ebitda_margin": key_metrics.get("ebitda_margin") or key_metrics.get("operating_margin"),
        "profit_margin": key_metrics.get("profit_margin") or key_metrics.get("net_margin"),
        "debt_to_equity": key_metrics.get("debt_to_equity"),
        "market_cap": key_metrics.get("market_cap"),
        "subscribers": key_metrics.get("subscribers"),
        "arpu": key_metrics.get("arpu"),
    }

    # Build competitors data from state
    competitors_list = state.get("competitors", []) or []
    competitors_data = []

    for comp_name in competitors_list[:5]:  # Limit to 5 competitors
        # Try to get competitor data from competitive_matrix if available
        comp_matrix = state.get("competitive_matrix", {})
        comp_scores = {}
        if comp_matrix:
            for comp_info in comp_matrix.get("competitors", []):
                if comp_info.get("name") == comp_name:
                    comp_scores = comp_info.get("scores", {})
                    break

        competitors_data.append(
            {
                "name": comp_name,
                "revenue": comp_scores.get("revenue"),
                "revenue_growth": comp_scores.get("revenue_growth"),
                "ebitda_margin": comp_scores.get("ebitda_margin"),
                "profit_margin": comp_scores.get("profit_margin"),
                "debt_to_equity": comp_scores.get("debt_to_equity"),
                "market_cap": comp_scores.get("market_cap"),
            }
        )

    # Determine metrics based on industry (telecom includes subscribers/ARPU)
    detected_industry = state.get("detected_industry", "")
    if "telecom" in detected_industry.lower() or "telecommunications" in detected_industry.lower():
        metrics = [
            FinancialMetric.REVENUE,
            FinancialMetric.REVENUE_GROWTH,
            FinancialMetric.EBITDA_MARGIN,
            FinancialMetric.PROFIT_MARGIN,
            FinancialMetric.DEBT_TO_EQUITY,
            FinancialMetric.SUBSCRIBERS,
            FinancialMetric.ARPU,
        ]
    else:
        metrics = [
            FinancialMetric.REVENUE,
            FinancialMetric.REVENUE_GROWTH,
            FinancialMetric.EBITDA_MARGIN,
            FinancialMetric.PROFIT_MARGIN,
            FinancialMetric.DEBT_TO_EQUITY,
            FinancialMetric.MARKET_CAP,
        ]

    # Generate financial comparison
    comparison = create_financial_comparison(
        company_name=company_name,
        company_data=company_data,
        competitors_data=competitors_data,
        metrics=metrics,
    )

    # Convert to dict for state storage
    comparison_dict = comparison.to_dict()
    comparison_dict["markdown"] = comparison.to_markdown()

    print(
        f"[OK] Financial comparison complete: {len(comparison.rows)} metrics compared across {len(competitors_list)} competitors"
    )

    return {"financial_comparison": comparison_dict}
