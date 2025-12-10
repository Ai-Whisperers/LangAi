"""
Synthesizer Agent - Aggregates insights from all specialized agents.

This agent is responsible for:
- Combining outputs from Financial, Market, and Product agents
- Resolving conflicts between agents
- Generating comprehensive company overview
- Formatting structured data for final report
- Integrating historical trend analysis and forecasts
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from ...config import get_config
from ...llm.client_factory import get_anthropic_client, calculate_cost, safe_extract_text
from ...state import OverallState

# Import trend analyst with fallback
try:
    from ..research.trend_analyst import (
        TrendAnalystAgent,
        create_trend_analyst,
        TrendDirection,
        TrendAnalysis,
    )
    TREND_ANALYST_AVAILABLE = True
except ImportError:
    TREND_ANALYST_AVAILABLE = False
    logger.warning("Trend analyst not available - historical trends disabled")


class SynthesizerAgent:
    """Synthesizer agent for combining specialist analyses."""

    def __init__(self, llm_client: Optional[Any] = None):
        self.llm_client = llm_client or get_anthropic_client()

    def synthesize(
        self,
        company_name: str,
        agent_outputs: Dict[str, Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synthesize insights from multiple specialist agents.

        Note: This method is sync because the underlying node function is sync.
        The LangGraph workflow does not use async operations.
        """
        state = {
            "company_name": company_name,
            "agent_outputs": agent_outputs or {}
        }
        return synthesizer_agent_node(state)


def create_synthesizer_agent(llm_client: Any = None) -> SynthesizerAgent:
    """Factory function to create a SynthesizerAgent."""
    return SynthesizerAgent(llm_client=llm_client)


SYNTHESIS_PROMPT = """You are a senior research analyst synthesizing insights from multiple specialized analysts.

Company: {company_name}

You have received analysis from three specialist teams:

## Financial Analysis
{financial_analysis}

## Market Analysis
{market_analysis}

## Product Analysis
{product_analysis}

{trend_section}

Task: Create a comprehensive, well-structured research report by synthesizing these specialized analyses.

Generate the following sections:

## Company Overview
A 2-3 sentence summary combining insights from all analysts about what the company does and its significance.

## Key Metrics
Extract and list all financial metrics in bullet format:
- Revenue: [from financial analysis]
- Founded: [if mentioned]
- Market Share: [from market analysis]
- Employees: [if mentioned]
- Valuation/Market Cap: [from financial analysis]
- Any other relevant metrics

## Main Products/Services
List the company's products/services from the product analysis (bullet points)

## Competitors
List main competitors from market analysis

{trend_instructions}

## Key Insights
List 3-4 most important insights combining perspectives from all three analyses:
- Financial health/performance
- Market position
- Product/technology strengths
- Strategic positioning
{trend_insight_instruction}

Requirements:
- Synthesize, don't just concatenate
- Resolve any contradictions intelligently
- Maintain factual accuracy
- Keep formatting clean and consistent
- If information is missing, note "Not available in research"

Generate the synthesized report now:"""

TREND_SECTION_TEMPLATE = """## Historical Trend Analysis
{trend_summary}

### Detected Trends
{trends_list}

### Forecasts (Next 4 Periods)
{forecasts_list}

### Opportunities
{opportunities_list}

### Threats
{threats_list}
"""

TREND_INSTRUCTIONS = """## Historical Trends & Outlook
Based on the trend analysis above, summarize:
- Key metrics trajectory (growth, decline, stability)
- Forecast outlook with confidence levels
- Opportunities identified from positive trends
- Risks from declining metrics"""

TREND_INSIGHT_INSTRUCTION = """- Include trend-based strategic recommendations if trend analysis is available"""


def _format_trend_analysis(trend_analysis: Optional["TrendAnalysis"]) -> Dict[str, str]:
    """Format trend analysis results for the synthesis prompt."""
    if not trend_analysis or not TREND_ANALYST_AVAILABLE:
        return {
            "trend_section": "",
            "trend_instructions": "",
            "trend_insight_instruction": ""
        }

    # Format trends list
    trends_list = []
    for trend in trend_analysis.trends[:5]:  # Limit to top 5
        direction_emoji = {
            "strong_up": "📈",
            "up": "↗️",
            "stable": "➡️",
            "down": "↘️",
            "strong_down": "📉",
            "volatile": "📊"
        }.get(trend.direction.value, "•")
        trends_list.append(
            f"{direction_emoji} {trend.metric}: {trend.change_percent:+.1f}% "
            f"({trend.strength.value} trend)"
        )

    # Format forecasts
    forecasts_list = []
    for forecast in trend_analysis.forecasts[:4]:  # Next 4 periods
        period_str = forecast.period.strftime("%b %Y") if hasattr(forecast.period, 'strftime') else str(forecast.period)
        forecasts_list.append(
            f"- {forecast.metric} ({period_str}): "
            f"${forecast.predicted_value:,.0f} "
            f"(confidence: {forecast.confidence_level:.0%})"
        )

    # Format opportunities
    opportunities_list = [f"- {opp}" for opp in trend_analysis.opportunities[:3]]

    # Format threats
    threats_list = [f"- {threat}" for threat in trend_analysis.threats[:3]]

    trend_section = TREND_SECTION_TEMPLATE.format(
        trend_summary=trend_analysis.summary,
        trends_list="\n".join(trends_list) if trends_list else "No significant trends detected",
        forecasts_list="\n".join(forecasts_list) if forecasts_list else "Insufficient data for forecasting",
        opportunities_list="\n".join(opportunities_list) if opportunities_list else "- No specific opportunities identified",
        threats_list="\n".join(threats_list) if threats_list else "- No specific threats identified"
    )

    return {
        "trend_section": trend_section,
        "trend_instructions": TREND_INSTRUCTIONS,
        "trend_insight_instruction": TREND_INSIGHT_INSTRUCTION
    }


def _extract_historical_data(state: Dict[str, Any]) -> Dict[str, List[Dict]]:
    """Extract historical data from state for trend analysis."""
    historical_data = {}

    # Check for explicit historical_data in state
    if "historical_data" in state:
        return state["historical_data"]

    # Try to extract from agent outputs
    agent_outputs = state.get("agent_outputs", {})

    # Extract from financial analysis
    financial = agent_outputs.get("financial", {})
    if "revenue_history" in financial:
        historical_data["revenue"] = financial["revenue_history"]
    if "earnings_history" in financial:
        historical_data["earnings"] = financial["earnings_history"]

    # Extract from market analysis
    market = agent_outputs.get("market", {})
    if "market_share_history" in market:
        historical_data["market_share"] = market["market_share_history"]

    return historical_data


def synthesizer_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Synthesizer Agent Node: Aggregate all specialized agent outputs.

    This agent combines insights from Financial, Market, and Product
    specialists into a comprehensive, coherent research report.
    Now includes historical trend analysis when data is available.

    Args:
        state: Current workflow state

    Returns:
        State update with synthesized overview
    """
    logger.info("Synthesizer agent starting - aggregating specialist insights")

    config = get_config()
    client = get_anthropic_client()

    company_name = state["company_name"]
    agent_outputs = state.get("agent_outputs", {})

    # Get outputs from each specialist
    financial = agent_outputs.get("financial", {}).get("analysis", "No financial analysis available")
    market = agent_outputs.get("market", {}).get("analysis", "No market analysis available")
    product = agent_outputs.get("product", {}).get("analysis", "No product analysis available")

    logger.debug(f"Combining insights - Financial: {len(financial)} chars, Market: {len(market)} chars, Product: {len(product)} chars")

    # Perform trend analysis if available
    trend_analysis = None
    trend_formatting = {"trend_section": "", "trend_instructions": "", "trend_insight_instruction": ""}

    if TREND_ANALYST_AVAILABLE:
        try:
            historical_data = _extract_historical_data(state)
            if historical_data:
                logger.info(f"Running trend analysis on {len(historical_data)} metrics")
                analyst = create_trend_analyst(company_name=company_name)

                for metric, data in historical_data.items():
                    analyst.add_historical_data(metric, data)

                trend_analysis = analyst.analyze_trends()
                trend_formatting = _format_trend_analysis(trend_analysis)
                logger.info(f"Trend analysis complete: {len(trend_analysis.trends)} trends, {len(trend_analysis.forecasts)} forecasts")
            else:
                logger.debug("No historical data available for trend analysis")
        except Exception as e:
            logger.warning(f"Trend analysis failed: {e}")

    # Create synthesis prompt
    prompt = SYNTHESIS_PROMPT.format(
        company_name=company_name,
        financial_analysis=financial,
        market_analysis=market,
        product_analysis=product,
        **trend_formatting
    )

    # Call Claude for synthesis
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=config.synthesizer_max_tokens,
        temperature=config.synthesizer_temperature,
        messages=[{"role": "user", "content": prompt}]
    )

    synthesized_overview = safe_extract_text(response, agent_name="synthesizer")
    cost = calculate_cost(
        response.usage.input_tokens,
        response.usage.output_tokens
    )

    logger.info(f"Synthesizer agent complete - cost: ${cost:.4f}")

    # Track agent output
    agent_output = {
        "synthesis": synthesized_overview,
        "specialists_combined": 3,
        "trend_analysis_included": trend_analysis is not None,
        "cost": cost,
        "tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }

    # Include trend data in output if available
    if trend_analysis:
        agent_output["trends"] = {
            "summary": trend_analysis.summary,
            "confidence": trend_analysis.confidence,
            "trend_count": len(trend_analysis.trends),
            "forecast_count": len(trend_analysis.forecasts),
            "opportunities": trend_analysis.opportunities,
            "threats": trend_analysis.threats
        }

    # Return only this agent's contribution
    # Reducers will handle merging/accumulation automatically
    return {
        "company_overview": synthesized_overview,
        "notes": [synthesized_overview],  # For quality check
        "agent_outputs": {"synthesizer": agent_output},
        "total_cost": cost,
        "total_tokens": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
    }
