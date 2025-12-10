"""
Output Nodes for Research Workflow

This module contains nodes responsible for final output generation:
- investment_thesis_node: Generate investment thesis
- save_report_node: Generate and save markdown report

Also includes formatters for report sections.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from ...state import OverallState
from ...config import get_config
from ...prompts import format_sources_for_report
from ...agents.research.investment_thesis import create_thesis_generator


# ============================================================================
# Report Formatters
# ============================================================================

def _format_news_sentiment(sentiment: Optional[Dict[str, Any]]) -> str:
    """Format news sentiment for report."""
    if not sentiment:
        return "*No news sentiment analysis available*"

    sections = []

    # Overall sentiment
    level = sentiment.get("sentiment_level", "neutral")
    score = sentiment.get("sentiment_score", 0)
    trend = sentiment.get("sentiment_trend", "stable")
    confidence = sentiment.get("confidence", 0) * 100

    sections.append(f"**Overall Sentiment:** {level.replace('_', ' ').title()}")
    sections.append(f"**Sentiment Score:** {score:.2f} (-1.0 to 1.0)")
    sections.append(f"**Trend:** {trend.title()}")
    sections.append(f"**Confidence:** {confidence:.0f}%")

    # Key topics
    topics = sentiment.get("key_topics", [])
    if topics:
        sections.append(f"\n**Key Topics:** {', '.join(topics)}")

    # Positive highlights
    positives = sentiment.get("positive_highlights", [])
    if positives:
        sections.append("\n### Positive Coverage")
        for highlight in positives[:3]:
            sections.append(f"- {highlight}")

    # Negative highlights
    negatives = sentiment.get("negative_highlights", [])
    if negatives:
        sections.append("\n### Negative Coverage")
        for highlight in negatives[:3]:
            sections.append(f"- {highlight}")

    # Category breakdown
    categories = sentiment.get("category_breakdown", {})
    if categories:
        sections.append("\n### Coverage by Category")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            sections.append(f"- **{category.replace('_', ' ').title()}:** {count} articles")

    return "\n".join(sections)


def _format_competitive_analysis(matrix: Optional[Dict[str, Any]]) -> str:
    """Format competitive matrix for report."""
    if not matrix:
        return "*No competitive analysis available*"

    sections = []

    # Company position
    company = matrix.get("company", {})
    sections.append(f"### Target Company: {company.get('name', 'N/A')}")
    if company.get("position"):
        sections.append(f"**Competitive Position:** {company.get('position')}")

    # Competitors
    competitors = matrix.get("competitors", [])
    if competitors:
        sections.append("\n### Competitors")
        for comp in competitors:
            pos = comp.get("position", "Unknown")
            sections.append(f"- **{comp.get('name', 'N/A')}** ({pos})")

    # Strategic insights
    insights = matrix.get("insights", [])
    if insights:
        sections.append("\n### Strategic Insights")
        for insight in insights[:5]:
            sections.append(f"- {insight}")

    # Recommendations
    recommendations = matrix.get("recommendations", [])
    if recommendations:
        sections.append("\n### Strategic Recommendations")
        for rec in recommendations[:3]:
            sections.append(f"- {rec}")

    return "\n".join(sections)


def _format_risk_profile(profile: Optional[Dict[str, Any]]) -> str:
    """Format risk profile for report."""
    if not profile:
        return "*No risk assessment available*"

    sections = []

    # Overall grade
    sections.append(f"**Overall Risk Grade:** {profile.get('grade', 'N/A')}")
    sections.append(f"**Risk Score:** {profile.get('overall_score', 0):.1f}/100")

    # Category scores
    category_scores = profile.get("category_scores", {})
    if category_scores:
        sections.append("\n### Risk by Category")
        for category, score in category_scores.items():
            sections.append(f"- **{category.replace('_', ' ').title()}:** {score:.1f}/100")

    # Key risks
    risks = profile.get("risks", [])
    if risks:
        sections.append("\n### Key Risks Identified")
        for risk in risks[:5]:
            severity = risk.get("severity", "Unknown")
            sections.append(f"- **{risk.get('description', 'N/A')}** (Severity: {severity})")
            if risk.get("mitigation"):
                sections.append(f"  - *Mitigation:* {risk.get('mitigation')}")

    return "\n".join(sections)


def _format_investment_thesis(thesis: Optional[Dict[str, Any]]) -> str:
    """Format investment thesis for report."""
    if not thesis:
        return "*No investment thesis available*"

    sections = []

    # Recommendation
    rec = thesis.get("recommendation", "N/A")
    confidence = thesis.get("confidence", 0) * 100
    horizon = thesis.get("target_horizon", "N/A")

    sections.append(f"### Investment Recommendation: **{rec}**")
    sections.append(f"**Confidence:** {confidence:.0f}% | **Time Horizon:** {horizon}")

    # Summary
    if thesis.get("summary"):
        sections.append(f"\n{thesis.get('summary')}")

    # Bull case
    bull = thesis.get("bull_case", {})
    if bull:
        sections.append("\n### Bull Case")
        sections.append(f"**Thesis:** {bull.get('thesis', 'N/A')}")
        sections.append(f"**Upside Potential:** {bull.get('upside_potential', 0):.1f}%")
        if bull.get("catalysts"):
            sections.append("**Catalysts:**")
            for catalyst in bull.get("catalysts", [])[:3]:
                sections.append(f"- {catalyst}")

    # Bear case
    bear = thesis.get("bear_case", {})
    if bear:
        sections.append("\n### Bear Case")
        sections.append(f"**Thesis:** {bear.get('thesis', 'N/A')}")
        sections.append(f"**Downside Risk:** {bear.get('downside_risk', 0):.1f}%")
        if bear.get("risks"):
            sections.append("**Key Risks:**")
            for risk in bear.get("risks", [])[:3]:
                sections.append(f"- {risk}")

    # Valuation
    valuation = thesis.get("valuation", {})
    if valuation:
        sections.append("\n### Valuation")
        if valuation.get("current_price"):
            sections.append(f"- Current Price: ${valuation.get('current_price'):.2f}")
        if valuation.get("target_price"):
            sections.append(f"- Target Price: ${valuation.get('target_price'):.2f}")
        if valuation.get("upside_downside"):
            sections.append(f"- Upside/Downside: {valuation.get('upside_downside'):.1f}%")
        if valuation.get("valuation_grade"):
            sections.append(f"- Valuation Grade: {valuation.get('valuation_grade')}")

    # Suitable for
    suitable = thesis.get("suitable_for", [])
    if suitable:
        sections.append(f"\n**Suitable For:** {', '.join(suitable)}")

    # Key metrics to watch
    metrics = thesis.get("key_metrics_to_watch", [])
    if metrics:
        sections.append("\n### Key Metrics to Watch")
        for metric in metrics[:5]:
            sections.append(f"- {metric}")

    return "\n".join(sections)


# ============================================================================
# Output Nodes
# ============================================================================

def investment_thesis_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 8: Generate investment thesis.

    Args:
        state: Current workflow state

    Returns:
        State update with investment thesis
    """
    print("\n[NODE] Generating investment thesis...")

    # Build company data from state
    company_data = {
        "name": state["company_name"],
        "overview": state.get("company_overview", ""),
        "key_metrics": state.get("key_metrics", {}),
        "products_services": state.get("products_services", []),
        "competitors": state.get("competitors", []),
        "key_insights": state.get("key_insights", []),
        "competitive_matrix": state.get("competitive_matrix"),
    }

    # Get risk profile if available
    risk_profile = state.get("risk_profile")

    # Generate investment thesis
    generator = create_thesis_generator()
    thesis = generator.generate_thesis(company_data, risk_profile)

    # Convert to dict for state storage
    thesis_dict = {
        "company_name": thesis.company_name,
        "recommendation": thesis.recommendation.value,
        "confidence": thesis.confidence,
        "target_horizon": thesis.target_horizon.value,
        "summary": thesis.summary,
        "bull_case": {
            "thesis": thesis.bull_case.thesis,
            "catalysts": thesis.bull_case.catalysts,
            "upside_potential": thesis.bull_case.upside_potential,
            "probability": thesis.bull_case.probability,
        },
        "bear_case": {
            "thesis": thesis.bear_case.thesis,
            "risks": thesis.bear_case.risks,
            "downside_risk": thesis.bear_case.downside_risk,
            "probability": thesis.bear_case.probability,
        },
        "valuation": {
            "current_price": thesis.valuation.current_price,
            "target_price": thesis.valuation.target_price,
            "upside_downside": thesis.valuation.upside_downside,
            "pe_ratio": thesis.valuation.pe_ratio,
            "ev_ebitda": thesis.valuation.ev_ebitda,
            "valuation_grade": thesis.valuation.valuation_grade,
        } if thesis.valuation else None,
        "key_metrics_to_watch": thesis.key_metrics_to_watch,
        "suitable_for": [p.value for p in thesis.suitable_for],
    }

    print(f"[OK] Investment thesis complete: {thesis.recommendation.value} ({thesis.confidence:.0%} confidence)")

    return {
        "investment_thesis": thesis_dict
    }


def save_report_node(state: OverallState) -> Dict[str, Any]:
    """
    Node 9: Generate and save enhanced markdown report.

    Includes:
    - Company overview
    - Competitive analysis
    - Risk assessment
    - Investment thesis
    - Sources

    Args:
        state: Current workflow state

    Returns:
        State update with report path
    """
    config = get_config()

    print("\n[NODE] Generating enhanced markdown report...")

    # Calculate duration
    duration = (datetime.now() - state.get("start_time", datetime.now())).total_seconds()

    # Create output directory
    output_dir = Path(config.output_dir) / state["company_name"].replace(" ", "_")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate report filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"report_{timestamp}.md"

    # Format sources for report
    formatted_sources = format_sources_for_report(state["sources"])

    # Format enhanced analysis sections
    competitive_section = _format_competitive_analysis(state.get("competitive_matrix"))
    risk_section = _format_risk_profile(state.get("risk_profile"))
    thesis_section = _format_investment_thesis(state.get("investment_thesis"))
    sentiment_section = _format_news_sentiment(state.get("news_sentiment"))

    # Get region info
    region_info = ""
    if state.get("detected_region"):
        region_info = f" | Region: {state.get('detected_region')}"

    # Generate report content
    report_content = f"""# {state['company_name']} - Research Report

*Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*{region_info}

---

## Company Overview

{state.get('company_overview', '*No overview available*')}

---

## Investment Thesis

{thesis_section}

---

## Risk Assessment

{risk_section}

---

## Competitive Analysis

{competitive_section}

---

## News Sentiment

{sentiment_section}

---

## Sources

{formatted_sources}

---

*This report was automatically generated by the Company Researcher System*

**Metrics:** Quality Score: {state.get('quality_score', 0):.1f}/100 | Iterations: {state.get('iteration_count', 0)} | Duration: {duration:.1f}s | Cost: ${state.get('total_cost', 0.0):.4f} | Sources: {len(state.get('sources', []))}
"""

    # Save report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"[OK] Report saved to: {report_path}")

    return {
        "report_path": str(report_path)
    }


# Export formatters for use in other modules
__all__ = [
    "investment_thesis_node",
    "save_report_node",
    # Formatters
    "_format_news_sentiment",
    "_format_competitive_analysis",
    "_format_risk_profile",
    "_format_investment_thesis",
]
