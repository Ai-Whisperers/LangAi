"""
ESG Agent Module.

Main ESG analysis agent implementation.
"""

import re
from typing import Any, Awaitable, Callable, Dict, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage

from ...utils import get_logger

logger = get_logger(__name__)

from .models import (
    ESGCategory,
    ControversySeverity,
    ESGMetric,
    Controversy,
    ESGAnalysis,
)
from .scorer import ESGScorer


class ESGAgent:
    """
    Agent for ESG (Environmental, Social, Governance) analysis.

    Usage:
        agent = ESGAgent(llm_client, search_tool)

        # Full ESG analysis
        result = await agent.analyze("Tesla")

        # Get ESG score
        score = result.score

        # Access specific metrics
        environmental = [m for m in result.metrics if m.category == ESGCategory.ENVIRONMENTAL]
    """

    # Type alias for async search tool: takes query string, returns list of dicts
    SearchToolType = Callable[[str], Awaitable[List[Dict[str, Any]]]]

    def __init__(
        self,
        llm_client: Any,
        search_tool: Optional[SearchToolType] = None,
        enable_controversy_detection: bool = True
    ):
        """
        Initialize ESG agent.

        Args:
            llm_client: LLM client for analysis
            search_tool: Optional async search tool for data gathering
            enable_controversy_detection: Whether to detect controversies
        """
        self.llm = llm_client
        self.search_tool: Optional[ESGAgent.SearchToolType] = search_tool
        self.enable_controversy_detection = enable_controversy_detection
        self.scorer = ESGScorer()

    async def analyze(self, company_name: str) -> ESGAnalysis:
        """
        Perform comprehensive ESG analysis.

        Args:
            company_name: Company to analyze

        Returns:
            ESGAnalysis result
        """
        # Gather data
        search_results = await self._search_esg_data(company_name)

        # Extract metrics
        metrics = await self._extract_metrics(company_name, search_results)

        # Detect controversies
        controversies = []
        if self.enable_controversy_detection:
            controversies = await self._detect_controversies(company_name, search_results)

        # Calculate scores
        score = self.scorer.calculate_score(metrics, controversies)

        # Generate summaries
        env_summary = await self._generate_summary(
            company_name, ESGCategory.ENVIRONMENTAL, metrics, search_results
        )
        social_summary = await self._generate_summary(
            company_name, ESGCategory.SOCIAL, metrics, search_results
        )
        gov_summary = await self._generate_summary(
            company_name, ESGCategory.GOVERNANCE, metrics, search_results
        )

        # Identify strengths and risks
        strengths, risks = self.scorer.identify_strengths_risks(metrics, controversies)

        # Generate recommendations
        recommendations = self.scorer.generate_recommendations(metrics, score, risks)

        return ESGAnalysis(
            company_name=company_name,
            score=score,
            metrics=metrics,
            controversies=controversies,
            environmental_summary=env_summary,
            social_summary=social_summary,
            governance_summary=gov_summary,
            strengths=strengths,
            risks=risks,
            recommendations=recommendations,
            data_sources=[r.get("url", "") for r in search_results[:10]]
        )

    async def _search_esg_data(self, company_name: str) -> List[Dict]:
        """Search for ESG-related data."""
        if not self.search_tool:
            return []

        queries = [
            f"{company_name} ESG report sustainability",
            f"{company_name} environmental carbon emissions",
            f"{company_name} diversity inclusion workforce",
            f"{company_name} corporate governance board",
            f"{company_name} sustainability initiatives",
            f"{company_name} ESG rating score"
        ]

        all_results = []
        for query in queries:
            try:
                results = await self.search_tool(query)
                if isinstance(results, list):
                    all_results.extend(results)
            except Exception as e:
                logger.debug(f"ESG search query failed: {query[:50]}... - {e}")
                continue

        return all_results

    async def _extract_metrics(
        self,
        company_name: str,
        search_results: List[Dict]
    ) -> List[ESGMetric]:
        """Extract ESG metrics from search results."""
        metrics = []

        # Use LLM to extract metrics
        context = "\n".join(
            r.get("content", r.get("snippet", ""))[:500]
            for r in search_results[:10]
        )

        if not context.strip():
            return metrics

        prompt = f"""Analyze the following information about {company_name} and extract ESG metrics.

Context:
{context}

For each metric found, provide:
- Name
- Category (environmental, social, or governance)
- Value
- Unit
- Year (if available)
- Trend (improving, stable, declining)

Focus on quantitative metrics like:
- Carbon emissions (tCO2e)
- Renewable energy percentage
- Employee diversity percentages
- Board independence percentage
- Safety incident rates

Return ONLY the metrics found with factual data. Do not estimate or make up numbers."""

        try:
            if hasattr(self.llm, 'ainvoke'):
                response = await self.llm.ainvoke([
                    SystemMessage(content="You are an ESG analyst extracting metrics from reports."),
                    HumanMessage(content=prompt)
                ])
                metrics_text = response.content
                metrics = self._parse_metrics_response(metrics_text)
        except Exception as e:
            logger.warning(f"Failed to extract ESG metrics for {company_name}: {e}")

        return metrics

    def _parse_metrics_response(self, response: str) -> List[ESGMetric]:
        """Parse metrics from LLM response."""
        metrics = []

        lines = response.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try to identify category
            category = ESGCategory.ENVIRONMENTAL
            if any(w in line.lower() for w in ["social", "employee", "diversity", "safety"]):
                category = ESGCategory.SOCIAL
            elif any(w in line.lower() for w in ["governance", "board", "ethics"]):
                category = ESGCategory.GOVERNANCE

            # Look for percentage values
            pct_match = re.search(r'(\d+(?:\.\d+)?)\s*%', line)
            if pct_match:
                metrics.append(ESGMetric(
                    name=line[:50],
                    category=category,
                    value=float(pct_match.group(1)),
                    unit="%",
                    source="research"
                ))

        return metrics[:20]  # Limit to 20 metrics

    async def _detect_controversies(
        self,
        company_name: str,
        search_results: List[Dict]
    ) -> List[Controversy]:
        """Detect ESG controversies."""
        controversies = []

        # Search for controversies
        controversy_queries = [
            f"{company_name} lawsuit scandal",
            f"{company_name} environmental violation fine",
            f"{company_name} labor dispute controversy",
            f"{company_name} ethics investigation"
        ]

        controversy_results = []
        if self.search_tool:
            for query in controversy_queries:
                try:
                    results = await self.search_tool(query)
                    if isinstance(results, list):
                        controversy_results.extend(results)
                except Exception as e:
                    logger.debug(f"Controversy search failed: {query[:50]}... - {e}")
                    continue

        if not controversy_results:
            return controversies

        # Analyze for controversies
        context = "\n".join(
            r.get("content", r.get("snippet", ""))[:300]
            for r in controversy_results[:10]
        )

        prompt = f"""Identify any ESG controversies for {company_name} from this information:

{context}

For each controversy found, identify:
1. Title
2. Brief description
3. Category (environmental, social, or governance)
4. Severity (severe, high, moderate, low)
5. Whether it has been resolved

Only report factual controversies with evidence. Do not speculate."""

        try:
            if hasattr(self.llm, 'ainvoke'):
                response = await self.llm.ainvoke([
                    SystemMessage(content="You are an ESG analyst identifying company controversies."),
                    HumanMessage(content=prompt)
                ])
                controversies = self._parse_controversies(response.content)
        except Exception as e:
            logger.warning(f"Failed to detect controversies for {company_name}: {e}")

        return controversies

    def _parse_controversies(self, response: str) -> List[Controversy]:
        """Parse controversies from LLM response."""
        controversies = []

        sections = response.split("\n\n")
        for section in sections[:5]:
            if len(section) < 20:
                continue

            # Determine category
            category = ESGCategory.GOVERNANCE
            if any(w in section.lower() for w in ["environment", "emission", "pollution"]):
                category = ESGCategory.ENVIRONMENTAL
            elif any(w in section.lower() for w in ["labor", "employee", "discrimination"]):
                category = ESGCategory.SOCIAL

            # Determine severity
            severity = ControversySeverity.MODERATE
            if any(w in section.lower() for w in ["severe", "major", "significant"]):
                severity = ControversySeverity.HIGH

            controversies.append(Controversy(
                title=section.split("\n")[0][:100],
                description=section[:300],
                category=category,
                severity=severity
            ))

        return controversies

    async def _generate_summary(
        self,
        company_name: str,
        category: ESGCategory,
        metrics: List[ESGMetric],
        search_results: List[Dict]
    ) -> str:
        """Generate summary for ESG category."""
        category_metrics = [m for m in metrics if m.category == category]

        if not category_metrics:
            return f"Limited {category.value} data available for {company_name}."

        metrics_text = "\n".join(
            f"- {m.name}: {m.value} {m.unit}" for m in category_metrics
        )

        prompt = f"""Summarize {company_name}'s {category.value} ESG performance in 2-3 sentences.

Metrics:
{metrics_text}

Be factual and concise."""

        try:
            if hasattr(self.llm, 'ainvoke'):
                response = await self.llm.ainvoke([
                    SystemMessage(content="You are an ESG analyst writing concise summaries."),
                    HumanMessage(content=prompt)
                ])
                return response.content[:500]
        except Exception as e:
            logger.warning(f"Failed to generate {category.value} summary for {company_name}: {e}")

        return f"{company_name} has {len(category_metrics)} {category.value} metrics tracked."


# ============================================================================
# LangGraph Node Function
# ============================================================================

async def esg_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node for ESG analysis.

    Args:
        state: Current workflow state

    Returns:
        State update with ESG analysis
    """
    from langchain_anthropic import ChatAnthropic

    llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)

    # Get search tool from state if available
    search_tool = state.get("tools", {}).get("search")

    agent = ESGAgent(llm, search_tool)

    company_name = state.get("company_name", "")
    if not company_name:
        return {"agent_outputs": {"esg": {"error": "No company name provided"}}}

    try:
        analysis = await agent.analyze(company_name)
        return {
            "agent_outputs": {
                "esg": analysis.to_dict()
            }
        }
    except Exception as e:
        return {
            "agent_outputs": {
                "esg": {"error": str(e)}
            }
        }


# ============================================================================
# Factory Function
# ============================================================================

def create_esg_agent(
    llm_client: Any,
    search_tool: Optional[ESGAgent.SearchToolType] = None
) -> ESGAgent:
    """Create an ESG agent."""
    return ESGAgent(llm_client, search_tool)
