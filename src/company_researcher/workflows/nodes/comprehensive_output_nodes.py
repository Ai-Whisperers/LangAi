"""
Comprehensive Output Nodes for Multi-Section Report Generation.

This module contains nodes for generating comprehensive reports with:
- Executive summary
- Financial analysis
- Market analysis
- ESG analysis
- Brand analysis
- Competitive landscape
- Risk assessment
- Investment thesis
- News sentiment
- Sources
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from ...state import OverallState
from ...config import get_config
from ...utils import get_logger, utc_now

logger = get_logger(__name__)


# =============================================================================
# Cross-Section Data Enrichment Node
# =============================================================================

def enrich_executive_summary_node(state: OverallState) -> Dict[str, Any]:
    """
    Enrich executive summary with data from specialized analyses.

    This node runs AFTER all specialized analyses and BEFORE the final report,
    propagating key data points (market share, CEO, revenue) from specialized
    sections back to the executive summary.
    """
    logger.info("[NODE] Enriching executive summary with cross-section data...")

    company_overview = state.get("company_overview", "")
    if not company_overview:
        return {}

    enrichments = []

    # Extract market share from market analysis
    market_analysis = state.get("agent_outputs", {}).get("market", "")
    if market_analysis:
        # Look for market share percentages
        market_share_match = re.search(
            r'market share[^\d]*(\d+\.?\d*)\s*%',
            market_analysis, re.IGNORECASE
        )
        if market_share_match:
            market_share = market_share_match.group(1)
            # Check if market share is already in overview
            if "Market Share" in company_overview and "No specific" in company_overview:
                company_overview = re.sub(
                    r'(\*\*Market Share[^*]*\*\*[:\s]*)([^\n]*)',
                    f'\\1{market_share}% (from market analysis)',
                    company_overview
                )
                enrichments.append(f"market_share: {market_share}%")

        # Extract competitors
        competitors_section = re.search(
            r'(?:competitors|competidores)[^\n]*\n((?:\s*[-*]\s*[^\n]+\n)+)',
            market_analysis, re.IGNORECASE
        )
        if competitors_section:
            # Check if competitors are missing in overview
            if "Competitors" in company_overview and "No specific" in company_overview.split("Competitors")[1][:100]:
                competitors_text = competitors_section.group(1).strip()
                company_overview = re.sub(
                    r'(## Competitors\n)([^\n]*No specific[^\n]*)',
                    f'\\1{competitors_text}',
                    company_overview
                )
                enrichments.append("competitors list")

    # Extract CEO from notes or other analyses
    for note in state.get("notes", []) or []:
        if isinstance(note, str):
            # Look for CEO mentions
            ceo_patterns = [
                r'CEO[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                r'Chief Executive Officer[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                r'Gerente General[:\s]+([A-Z][a-záéíóú]+\s+[A-Z][a-záéíóú]+(?:\s+[A-Z][a-záéíóú]+)?)',
            ]
            for pattern in ceo_patterns:
                ceo_match = re.search(pattern, note)
                if ceo_match:
                    ceo_name = ceo_match.group(1)
                    # Update overview if CEO is missing
                    if "CEO" in company_overview and "No specific" in company_overview:
                        company_overview = re.sub(
                            r'(\*\*CEO[^*]*\*\*[:\s]*)([^\n]*No specific[^\n]*)',
                            f'\\1{ceo_name}',
                            company_overview
                        )
                        enrichments.append(f"ceo: {ceo_name}")
                        break

    # Extract revenue from financial analysis
    financial_analysis = state.get("agent_outputs", {}).get("financial", "")
    if financial_analysis:
        revenue_match = re.search(
            r'(?:revenue|ingresos)[^\d$]*\$?\s*(\d+(?:\.\d+)?)\s*(million|billion|M|B|millones)',
            financial_analysis, re.IGNORECASE
        )
        if revenue_match:
            revenue_value = revenue_match.group(1)
            revenue_unit = revenue_match.group(2)
            if "Revenue" in company_overview and "No specific" in company_overview:
                company_overview = re.sub(
                    r'(\*\*Annual Revenue[^*]*\*\*[:\s]*)([^\n]*No specific[^\n]*)',
                    f'\\1${revenue_value} {revenue_unit} (from financial analysis)',
                    company_overview
                )
                enrichments.append(f"revenue: ${revenue_value} {revenue_unit}")

    if enrichments:
        logger.info(f"[OK] Enriched executive summary with: {', '.join(enrichments)}")
    else:
        logger.info("[OK] No additional data to enrich")

    return {
        "company_overview": company_overview,
    }


# =============================================================================
# Comprehensive Report Generation Node
# =============================================================================

def save_comprehensive_report_node(state: OverallState) -> Dict[str, Any]:
    """
    Generate and save comprehensive markdown report with all analyses.
    """
    config = get_config()

    logger.info("[NODE] Generating comprehensive report...")

    duration = (utc_now() - state.get("start_time", utc_now())).total_seconds()

    # Create output directory
    output_dir = Path(config.output_dir) / state["company_name"].replace(" ", "_").lower()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamp
    timestamp = utc_now().strftime("%Y%m%d_%H%M%S")

    # Format all sections
    sections = {
        "overview": state.get("company_overview", "*No overview available*"),
        "financial": _format_agent_output("Financial Analysis", state.get("agent_outputs", {}).get("financial")),
        "market": _format_agent_output("Market Analysis", state.get("agent_outputs", {}).get("market")),
        "esg": _format_agent_output("ESG Analysis", state.get("agent_outputs", {}).get("esg")),
        "brand": _format_agent_output("Brand Analysis", state.get("agent_outputs", {}).get("brand")),
        "sentiment": _format_news_sentiment(state.get("news_sentiment")),
        "competitive": _format_competitive_analysis(state.get("competitive_matrix")),
        "financial_comparison": _format_financial_comparison(state.get("financial_comparison")),
        "risk": _format_risk_profile(state.get("risk_profile")),
        "investment": _format_investment_thesis(state.get("investment_thesis")),
        "sources": _format_sources_report(state.get("sources", [])),
    }

    # Generate full report
    report_content = f"""# {state['company_name']} - Comprehensive Research Report

*Generated on {utc_now().strftime("%Y-%m-%d %H:%M:%S")}*
*Region: {state.get('detected_region', 'Unknown')} | Language: {state.get('detected_language', 'Unknown')}*

---

## Executive Summary

{sections['overview']}

---

## Financial Analysis

{sections['financial']}

---

## Market Analysis

{sections['market']}

---

## ESG Analysis

{sections['esg']}

---

## Brand & Reputation

{sections['brand']}

---

## News Sentiment

{sections['sentiment']}

---

## Competitive Landscape

{sections['competitive']}

---

## Financial Comparison

{sections['financial_comparison']}

---

## Risk Assessment

{sections['risk']}

---

## Investment Thesis

{sections['investment']}

---

## Sources

{sections['sources']}

---

## Research Metrics

| Metric | Value |
|--------|-------|
| Quality Score | {state.get('quality_score', 0):.1f}/100 |
| Iterations | {state.get('iteration_count', 0)} |
| Duration | {duration:.1f}s |
| Total Cost | ${state.get('total_cost', 0.0):.4f} |
| Sources Used | {len(state.get('sources', []))} |
| Contradictions Found | {len(state.get('contradictions', []))} |

---

*This report was automatically generated by the Company Researcher System (Comprehensive Mode)*
"""

    # Save full report
    report_path = output_dir / f"00_full_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    # Save individual section files
    section_files = [
        ("01_executive_summary.md", "Executive Summary", sections["overview"]),
        ("02_financial_analysis.md", "Financial Analysis", sections["financial"]),
        ("03_market_analysis.md", "Market Analysis", sections["market"]),
        ("04_esg_analysis.md", "ESG Analysis", sections["esg"]),
        ("05_brand_analysis.md", "Brand & Reputation", sections["brand"]),
        ("06_competitive_analysis.md", "Competitive Landscape", sections["competitive"]),
        ("06b_financial_comparison.md", "Financial Comparison", sections["financial_comparison"]),
        ("07_risk_assessment.md", "Risk Assessment", sections["risk"]),
        ("08_investment_thesis.md", "Investment Thesis", sections["investment"]),
        ("09_sources.md", "Sources", sections["sources"]),
    ]

    for filename, title, content in section_files:
        filepath = output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {state['company_name']} - {title}\n\n{content}")

    # Save metrics JSON
    metrics = {
        "company_name": state["company_name"],
        "quality_score": state.get("quality_score", 0),
        "iterations": state.get("iteration_count", 0),
        "duration_seconds": duration,
        "total_cost": state.get("total_cost", 0.0),
        "sources_count": len(state.get("sources", [])),
        "contradictions_count": len(state.get("contradictions", [])),
        "confidence_scores": state.get("confidence_scores", {}),
        "source_quality": state.get("source_quality", {}),
        "timestamp": timestamp,
    }

    metrics_path = output_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    logger.info(f"[OK] Comprehensive report saved: {report_path}")

    return {
        "report_path": str(report_path),
        "output_dir": str(output_dir),
    }


# =============================================================================
# Formatter Functions
# =============================================================================

def _format_agent_output(title: str, content: Optional[str]) -> str:
    """Format an agent's output."""
    if not content:
        return f"*No {title.lower()} available*"
    return content


def _format_news_sentiment(sentiment: Optional[Dict]) -> str:
    """Format news sentiment section."""
    if not sentiment:
        return "*No news sentiment analysis available*"

    sections = [
        f"**Overall Sentiment:** {sentiment.get('sentiment_level', 'N/A')}",
        f"**Score:** {sentiment.get('sentiment_score', 0):.2f}",
        f"**Trend:** {sentiment.get('sentiment_trend', 'N/A')}",
        f"**Articles Analyzed:** {sentiment.get('total_articles', 0)}",
    ]

    topics = sentiment.get("key_topics", [])
    if topics:
        sections.append(f"\n**Key Topics:** {', '.join(topics)}")

    positives = sentiment.get("positive_highlights", [])
    if positives:
        sections.append("\n### Positive Coverage")
        for p in positives[:3]:
            sections.append(f"- {p}")

    negatives = sentiment.get("negative_highlights", [])
    if negatives:
        sections.append("\n### Areas of Concern")
        for n in negatives[:3]:
            sections.append(f"- {n}")

    return "\n".join(sections)


def _format_competitive_analysis(matrix: Optional[Dict]) -> str:
    """Format competitive matrix section."""
    if not matrix:
        return "*No competitive analysis available*"

    sections = []
    company = matrix.get("company", {})
    sections.append(f"### Target: {company.get('name', 'N/A')}")
    if company.get("position"):
        sections.append(f"**Position:** {company.get('position')}")

    competitors = matrix.get("competitors", [])
    if competitors:
        sections.append("\n### Key Competitors")
        for c in competitors:
            sections.append(f"- **{c.get('name', 'N/A')}** ({c.get('position', 'Unknown')})")

    insights = matrix.get("insights", [])
    if insights:
        sections.append("\n### Strategic Insights")
        for i in insights[:5]:
            sections.append(f"- {i}")

    return "\n".join(sections)


def _format_financial_comparison(comparison: Optional[Dict]) -> str:
    """Format financial comparison table section."""
    if not comparison:
        return "*No financial comparison available*"

    # If markdown is already generated, use it directly
    if comparison.get("markdown"):
        return comparison["markdown"]

    # Otherwise, build from structured data
    sections = []

    company_name = comparison.get("company_name", "Company")
    as_of_date = comparison.get("as_of_date", "N/A")
    currency = comparison.get("currency", "USD")

    sections.append(f"**Company:** {company_name}")
    sections.append(f"**As of:** {as_of_date}")
    sections.append(f"**Currency:** {currency}")

    rows = comparison.get("rows", [])
    if rows:
        sections.append("\n### Financial Metrics Comparison\n")

        # Build table header
        competitors = comparison.get("competitors", [])
        header = "| Metric | " + company_name + " | " + " | ".join(competitors) + " |"
        separator = "|--------|" + "--------|" * (len(competitors) + 1)
        sections.append(header)
        sections.append(separator)

        # Build table rows
        for row in rows:
            metric_name = row.get("metric_name", "N/A")
            company_value = row.get("company_value", "N/A")
            competitor_values = row.get("competitor_values", [])
            comp_str = " | ".join(str(v) if v else "N/A" for v in competitor_values)
            sections.append(f"| {metric_name} | {company_value} | {comp_str} |")

    summary = comparison.get("summary", {})
    if summary:
        sections.append("\n### Summary")
        for key, value in summary.items():
            sections.append(f"- **{key.replace('_', ' ').title()}:** {value}")

    notes = comparison.get("data_quality_notes", [])
    if notes:
        sections.append("\n### Data Quality Notes")
        for note in notes:
            sections.append(f"- {note}")

    return "\n".join(sections)


def _format_risk_profile(profile: Optional[Dict]) -> str:
    """Format risk profile section."""
    if not profile:
        return "*No risk assessment available*"

    sections = [
        f"**Risk Grade:** {profile.get('grade', 'N/A')}",
        f"**Risk Score:** {profile.get('overall_score', 0):.1f}/100",
    ]

    category_scores = profile.get("category_scores", {})
    if category_scores:
        sections.append("\n### Risk by Category")
        for cat, score in category_scores.items():
            sections.append(f"- **{cat.replace('_', ' ').title()}:** {score:.1f}/100")

    risks = profile.get("risks", [])
    if risks:
        sections.append("\n### Key Risks")
        for r in risks[:5]:
            sections.append(f"- **{r.get('description', 'N/A')}** ({r.get('severity', 'Unknown')} severity)")
            if r.get("mitigation"):
                sections.append(f"  - *Mitigation:* {r.get('mitigation')}")

    return "\n".join(sections)


def _format_investment_thesis(thesis: Optional[Dict]) -> str:
    """Format investment thesis section."""
    if not thesis:
        return "*No investment thesis available*"

    # Confidence is stored as 0-1 decimal, convert to percentage
    confidence = thesis.get('confidence', 0)
    # If confidence > 1, it's already a percentage; otherwise convert
    confidence_pct = confidence if confidence > 1 else confidence * 100

    sections = [
        f"### Recommendation: **{thesis.get('recommendation', 'N/A')}**",
        f"**Confidence:** {confidence_pct:.0f}%",
        f"**Time Horizon:** {thesis.get('target_horizon', 'N/A')}",
    ]

    if thesis.get("summary"):
        sections.append(f"\n{thesis.get('summary')}")

    bull = thesis.get("bull_case", {})
    if bull:
        sections.append("\n### Bull Case")
        # Use correct key names from output_nodes.py
        headline = bull.get('headline') or bull.get('thesis', 'N/A')
        upside = bull.get('target_upside') or bull.get('upside_potential', 0)
        sections.append(f"**Thesis:** {headline}")
        sections.append(f"**Upside:** {upside:.1f}%")
        if bull.get('catalysts'):
            sections.append("**Catalysts:**")
            for cat in bull.get('catalysts', [])[:3]:
                sections.append(f"- {cat}")

    bear = thesis.get("bear_case", {})
    if bear:
        sections.append("\n### Bear Case")
        # Use correct key names from output_nodes.py
        headline = bear.get('headline') or bear.get('thesis', 'N/A')
        downside = bear.get('target_downside') or bear.get('downside_risk', 0)
        sections.append(f"**Thesis:** {headline}")
        sections.append(f"**Downside:** {downside:.1f}%")
        if bear.get('key_risks'):
            sections.append("**Key Risks:**")
            for risk in bear.get('key_risks', [])[:3]:
                sections.append(f"- {risk}")

    suitable = thesis.get("suitable_for", [])
    if suitable:
        sections.append(f"\n**Suitable For:** {', '.join(suitable)}")

    return "\n".join(sections)


def _format_sources_report(sources: List[Dict]) -> str:
    """Format sources section."""
    if not sources:
        return "*No sources available*"

    sections = []
    for i, s in enumerate(sources[:20], 1):
        sections.append(f"{i}. [{s.get('title', 'Unknown')}]({s.get('url', '#')})")

    return "\n".join(sections)
