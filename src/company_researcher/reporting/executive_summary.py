"""
Executive Summary Generator - AI-powered one-page summaries.

Provides:
- Key highlights extraction
- Metrics summarization
- Risk/opportunity callouts
- Formatted executive summaries
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from ..utils import utc_now


class SummarySection(str, Enum):
    """Sections in executive summary."""
    OVERVIEW = "overview"
    KEY_METRICS = "key_metrics"
    FINANCIALS = "financials"
    MARKET_POSITION = "market_position"
    OPPORTUNITIES = "opportunities"
    RISKS = "risks"
    OUTLOOK = "outlook"
    RECOMMENDATION = "recommendation"


class SentimentType(str, Enum):
    """Sentiment classification."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


@dataclass
class KeyMetric:
    """A key metric to highlight."""
    name: str
    value: Any
    unit: str = ""
    change: Optional[float] = None
    change_period: str = ""
    sentiment: SentimentType = SentimentType.NEUTRAL
    source: Optional[str] = None

    def formatted_value(self) -> str:
        """Get formatted value string."""
        if isinstance(self.value, float):
            if self.unit == "%":
                return f"{self.value:.1f}%"
            elif self.unit == "$":
                return self._format_currency(self.value)
            else:
                return f"{self.value:,.2f} {self.unit}".strip()
        return f"{self.value} {self.unit}".strip()

    def _format_currency(self, value: float) -> str:
        """Format currency values with appropriate suffix."""
        if abs(value) >= 1e12:
            return f"${value/1e12:.2f}T"
        elif abs(value) >= 1e9:
            return f"${value/1e9:.2f}B"
        elif abs(value) >= 1e6:
            return f"${value/1e6:.2f}M"
        elif abs(value) >= 1e3:
            return f"${value/1e3:.2f}K"
        else:
            return f"${value:,.2f}"

    def change_indicator(self) -> str:
        """Get change indicator symbol."""
        if self.change is None:
            return ""
        if self.change > 0:
            return f"+{self.change:.1f}%"
        elif self.change < 0:
            return f"{self.change:.1f}%"
        return "0%"


@dataclass
class Highlight:
    """A key highlight or insight."""
    text: str
    category: SummarySection
    sentiment: SentimentType = SentimentType.NEUTRAL
    importance: float = 1.0
    source: Optional[str] = None


@dataclass
class RiskOpportunity:
    """A risk or opportunity callout."""
    title: str
    description: str
    is_risk: bool
    severity: float = 0.5  # 0-1 scale
    likelihood: float = 0.5  # 0-1 scale
    timeframe: str = ""
    mitigation: Optional[str] = None

    @property
    def impact_score(self) -> float:
        """Calculate impact score."""
        return self.severity * self.likelihood


@dataclass
class ExecutiveSummary:
    """Complete executive summary."""
    company_name: str
    generated_at: datetime
    overview: str
    key_metrics: List[KeyMetric] = field(default_factory=list)
    highlights: List[Highlight] = field(default_factory=list)
    risks: List[RiskOpportunity] = field(default_factory=list)
    opportunities: List[RiskOpportunity] = field(default_factory=list)
    outlook: str = ""
    recommendation: str = ""
    overall_sentiment: SentimentType = SentimentType.NEUTRAL
    confidence_score: float = 0.0
    sources_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "company_name": self.company_name,
            "generated_at": self.generated_at.isoformat(),
            "overview": self.overview,
            "key_metrics": [
                {
                    "name": m.name,
                    "value": m.formatted_value(),
                    "change": m.change_indicator(),
                    "sentiment": m.sentiment.value
                }
                for m in self.key_metrics
            ],
            "highlights": [
                {
                    "text": h.text,
                    "category": h.category.value,
                    "sentiment": h.sentiment.value
                }
                for h in self.highlights
            ],
            "risks": [
                {
                    "title": r.title,
                    "description": r.description,
                    "severity": r.severity,
                    "impact_score": r.impact_score
                }
                for r in self.risks
            ],
            "opportunities": [
                {
                    "title": o.title,
                    "description": o.description,
                    "likelihood": o.likelihood,
                    "impact_score": o.impact_score
                }
                for o in self.opportunities
            ],
            "outlook": self.outlook,
            "recommendation": self.recommendation,
            "overall_sentiment": self.overall_sentiment.value,
            "confidence_score": self.confidence_score,
            "sources_count": self.sources_count
        }

    def to_markdown(self) -> str:
        """Generate markdown formatted summary."""
        lines = [
            f"# Executive Summary: {self.company_name}",
            f"*Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M UTC')}*",
            "",
            "## Overview",
            self.overview,
            "",
        ]

        # Key Metrics
        if self.key_metrics:
            lines.extend([
                "## Key Metrics",
                "",
                "| Metric | Value | Change |",
                "|--------|-------|--------|",
            ])
            for m in self.key_metrics[:6]:
                lines.append(f"| {m.name} | {m.formatted_value()} | {m.change_indicator()} |")
            lines.append("")

        # Highlights
        if self.highlights:
            lines.extend([
                "## Key Highlights",
                "",
            ])
            for h in sorted(self.highlights, key=lambda x: x.importance, reverse=True)[:5]:
                icon = self._sentiment_icon(h.sentiment)
                lines.append(f"- {icon} {h.text}")
            lines.append("")

        # Opportunities
        if self.opportunities:
            lines.extend([
                "## Opportunities",
                "",
            ])
            for o in sorted(self.opportunities, key=lambda x: x.impact_score, reverse=True)[:3]:
                lines.append(f"**{o.title}**: {o.description}")
                lines.append("")

        # Risks
        if self.risks:
            lines.extend([
                "## Risks",
                "",
            ])
            for r in sorted(self.risks, key=lambda x: x.impact_score, reverse=True)[:3]:
                lines.append(f"**{r.title}**: {r.description}")
                if r.mitigation:
                    lines.append(f"  - *Mitigation*: {r.mitigation}")
                lines.append("")

        # Outlook
        if self.outlook:
            lines.extend([
                "## Outlook",
                self.outlook,
                "",
            ])

        # Recommendation
        if self.recommendation:
            lines.extend([
                "## Recommendation",
                self.recommendation,
                "",
            ])

        # Footer
        sentiment_label = self.overall_sentiment.value.title()
        lines.extend([
            "---",
            f"*Overall Sentiment: {sentiment_label} | Confidence: {self.confidence_score:.0%} | Sources: {self.sources_count}*"
        ])

        return "\n".join(lines)

    def to_text(self) -> str:
        """Generate plain text summary."""
        lines = [
            f"EXECUTIVE SUMMARY: {self.company_name.upper()}",
            f"Generated: {self.generated_at.strftime('%Y-%m-%d')}",
            "=" * 60,
            "",
            "OVERVIEW",
            "-" * 40,
            self.overview,
            "",
        ]

        if self.key_metrics:
            lines.extend([
                "KEY METRICS",
                "-" * 40,
            ])
            for m in self.key_metrics[:6]:
                change = f" ({m.change_indicator()})" if m.change else ""
                lines.append(f"  {m.name}: {m.formatted_value()}{change}")
            lines.append("")

        if self.highlights:
            lines.extend([
                "KEY HIGHLIGHTS",
                "-" * 40,
            ])
            for h in sorted(self.highlights, key=lambda x: x.importance, reverse=True)[:5]:
                lines.append(f"  * {h.text}")
            lines.append("")

        if self.outlook:
            lines.extend([
                "OUTLOOK",
                "-" * 40,
                self.outlook,
                "",
            ])

        if self.recommendation:
            lines.extend([
                "RECOMMENDATION",
                "-" * 40,
                self.recommendation,
                "",
            ])

        return "\n".join(lines)

    def _sentiment_icon(self, sentiment: SentimentType) -> str:
        """Get icon for sentiment."""
        icons = {
            SentimentType.POSITIVE: "[+]",
            SentimentType.NEGATIVE: "[-]",
            SentimentType.NEUTRAL: "[=]",
            SentimentType.MIXED: "[~]"
        }
        return icons.get(sentiment, "[?]")


class ExecutiveSummaryGenerator:
    """
    Generates executive summaries from research results.

    Usage:
        generator = ExecutiveSummaryGenerator(llm_client)

        # Generate from research result
        summary = await generator.generate(research_result)

        # Get formatted output
        markdown = summary.to_markdown()
        text = summary.to_text()
    """

    def __init__(
        self,
        llm_client: Any = None,
        max_highlights: int = 5,
        max_risks: int = 3,
        max_opportunities: int = 3
    ):
        self.llm_client = llm_client
        self.max_highlights = max_highlights
        self.max_risks = max_risks
        self.max_opportunities = max_opportunities

    async def generate(
        self,
        research_result: Dict[str, Any],
        company_name: str = None
    ) -> ExecutiveSummary:
        """
        Generate executive summary from research result.

        Args:
            research_result: Full research result dictionary
            company_name: Override company name

        Returns:
            ExecutiveSummary object
        """
        company = company_name or research_result.get("company_name", "Unknown")

        # Extract data from research result
        overview = await self._generate_overview(research_result)
        metrics = self._extract_key_metrics(research_result)
        highlights = self._extract_highlights(research_result)
        risks = self._extract_risks(research_result)
        opportunities = self._extract_opportunities(research_result)
        outlook = await self._generate_outlook(research_result)
        recommendation = await self._generate_recommendation(research_result)

        # Calculate overall sentiment
        sentiment = self._calculate_overall_sentiment(highlights, risks, opportunities)

        # Calculate confidence
        confidence = self._calculate_confidence(research_result)

        return ExecutiveSummary(
            company_name=company,
            generated_at=utc_now(),
            overview=overview,
            key_metrics=metrics[:6],
            highlights=highlights[:self.max_highlights],
            risks=risks[:self.max_risks],
            opportunities=opportunities[:self.max_opportunities],
            outlook=outlook,
            recommendation=recommendation,
            overall_sentiment=sentiment,
            confidence_score=confidence,
            sources_count=self._count_sources(research_result)
        )

    async def _generate_overview(self, result: Dict[str, Any]) -> str:
        """Generate overview paragraph."""
        if self.llm_client:
            prompt = self._build_overview_prompt(result)
            response = await self.llm_client.generate(prompt)
            return response.strip()

        # Fallback: extract from existing data
        agent_outputs = result.get("agent_outputs", {})
        if "synthesizer" in agent_outputs:
            return agent_outputs["synthesizer"].get("summary", "")[:500]
        return "Research overview not available."

    def _extract_key_metrics(self, result: Dict[str, Any]) -> List[KeyMetric]:
        """Extract key metrics from research result."""
        metrics = []
        agent_outputs = result.get("agent_outputs", {})

        # Financial metrics
        financial = agent_outputs.get("financial", {})
        if financial:
            if "revenue" in financial:
                metrics.append(KeyMetric(
                    name="Revenue",
                    value=financial["revenue"],
                    unit="$",
                    change=financial.get("revenue_growth"),
                    change_period="YoY"
                ))
            if "market_cap" in financial:
                metrics.append(KeyMetric(
                    name="Market Cap",
                    value=financial["market_cap"],
                    unit="$"
                ))
            if "profit_margin" in financial:
                metrics.append(KeyMetric(
                    name="Profit Margin",
                    value=financial["profit_margin"] * 100,
                    unit="%"
                ))

        # Market metrics
        market = agent_outputs.get("market", {})
        if market:
            if "market_share" in market:
                metrics.append(KeyMetric(
                    name="Market Share",
                    value=market["market_share"] * 100,
                    unit="%"
                ))
            if "growth_rate" in market:
                metrics.append(KeyMetric(
                    name="Market Growth",
                    value=market["growth_rate"] * 100,
                    unit="%"
                ))

        # Employee count
        company_info = result.get("company_info", {})
        if "employees" in company_info:
            metrics.append(KeyMetric(
                name="Employees",
                value=company_info["employees"],
                unit=""
            ))

        return metrics

    def _extract_highlights(self, result: Dict[str, Any]) -> List[Highlight]:
        """Extract key highlights from research result."""
        highlights = []
        agent_outputs = result.get("agent_outputs", {})

        for agent_name, output in agent_outputs.items():
            if isinstance(output, dict):
                # Look for findings, insights, highlights
                for key in ["findings", "insights", "highlights", "key_points"]:
                    if key in output and isinstance(output[key], list):
                        for item in output[key][:3]:
                            text = item if isinstance(item, str) else item.get("text", str(item))
                            highlights.append(Highlight(
                                text=text,
                                category=self._map_agent_to_section(agent_name),
                                importance=0.8
                            ))

        # Sort by importance and deduplicate
        seen = set()
        unique = []
        for h in sorted(highlights, key=lambda x: x.importance, reverse=True):
            if h.text not in seen:
                seen.add(h.text)
                unique.append(h)

        return unique

    def _extract_risks(self, result: Dict[str, Any]) -> List[RiskOpportunity]:
        """Extract risks from research result."""
        risks = []
        agent_outputs = result.get("agent_outputs", {})

        for agent_name, output in agent_outputs.items():
            if isinstance(output, dict):
                for key in ["risks", "threats", "challenges", "concerns"]:
                    if key in output and isinstance(output[key], list):
                        for item in output[key][:2]:
                            if isinstance(item, dict):
                                risks.append(RiskOpportunity(
                                    title=item.get("title", "Risk"),
                                    description=item.get("description", str(item)),
                                    is_risk=True,
                                    severity=item.get("severity", 0.5)
                                ))
                            else:
                                risks.append(RiskOpportunity(
                                    title="Identified Risk",
                                    description=str(item),
                                    is_risk=True
                                ))

        return sorted(risks, key=lambda x: x.impact_score, reverse=True)

    def _extract_opportunities(self, result: Dict[str, Any]) -> List[RiskOpportunity]:
        """Extract opportunities from research result."""
        opportunities = []
        agent_outputs = result.get("agent_outputs", {})

        for agent_name, output in agent_outputs.items():
            if isinstance(output, dict):
                for key in ["opportunities", "growth_areas", "strengths", "advantages"]:
                    if key in output and isinstance(output[key], list):
                        for item in output[key][:2]:
                            if isinstance(item, dict):
                                opportunities.append(RiskOpportunity(
                                    title=item.get("title", "Opportunity"),
                                    description=item.get("description", str(item)),
                                    is_risk=False,
                                    likelihood=item.get("likelihood", 0.5)
                                ))
                            else:
                                opportunities.append(RiskOpportunity(
                                    title="Identified Opportunity",
                                    description=str(item),
                                    is_risk=False
                                ))

        return sorted(opportunities, key=lambda x: x.impact_score, reverse=True)

    async def _generate_outlook(self, result: Dict[str, Any]) -> str:
        """Generate outlook statement."""
        if self.llm_client:
            prompt = self._build_outlook_prompt(result)
            response = await self.llm_client.generate(prompt)
            return response.strip()

        agent_outputs = result.get("agent_outputs", {})
        if "analyst" in agent_outputs:
            return agent_outputs["analyst"].get("outlook", "")
        return ""

    async def _generate_recommendation(self, result: Dict[str, Any]) -> str:
        """Generate recommendation statement."""
        if self.llm_client:
            prompt = self._build_recommendation_prompt(result)
            response = await self.llm_client.generate(prompt)
            return response.strip()

        return ""

    def _calculate_overall_sentiment(
        self,
        highlights: List[Highlight],
        risks: List[RiskOpportunity],
        opportunities: List[RiskOpportunity]
    ) -> SentimentType:
        """Calculate overall sentiment."""
        positive_score = sum(1 for h in highlights if h.sentiment == SentimentType.POSITIVE)
        negative_score = sum(1 for h in highlights if h.sentiment == SentimentType.NEGATIVE)

        positive_score += len(opportunities) * 0.5
        negative_score += len(risks) * 0.5

        total = positive_score + negative_score
        if total == 0:
            return SentimentType.NEUTRAL

        ratio = positive_score / total
        if ratio > 0.6:
            return SentimentType.POSITIVE
        elif ratio < 0.4:
            return SentimentType.NEGATIVE
        else:
            return SentimentType.MIXED

    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence score."""
        quality_score = result.get("quality_score", 0.5)
        sources = self._count_sources(result)
        source_factor = min(sources / 20, 1.0)

        return (quality_score * 0.7 + source_factor * 0.3)

    def _count_sources(self, result: Dict[str, Any]) -> int:
        """Count unique sources."""
        sources = set()
        search_results = result.get("search_results", {})

        for agent_results in search_results.values():
            if isinstance(agent_results, list):
                for item in agent_results:
                    if isinstance(item, dict) and "url" in item:
                        sources.add(item["url"])

        return len(sources)

    def _map_agent_to_section(self, agent_name: str) -> SummarySection:
        """Map agent name to summary section."""
        mapping = {
            "financial": SummarySection.FINANCIALS,
            "enhanced_financial": SummarySection.FINANCIALS,
            "market": SummarySection.MARKET_POSITION,
            "competitor": SummarySection.MARKET_POSITION,
            "product": SummarySection.OVERVIEW,
            "brand": SummarySection.OVERVIEW,
            "analyst": SummarySection.OUTLOOK,
            "synthesizer": SummarySection.OVERVIEW
        }
        return mapping.get(agent_name, SummarySection.OVERVIEW)

    def _build_overview_prompt(self, result: Dict[str, Any]) -> str:
        """Build prompt for overview generation."""
        return f"""Generate a concise 2-3 sentence executive overview for {result.get('company_name', 'this company')}.

Research Data:
{self._summarize_result(result)}

Focus on: core business, market position, and current state.
Be factual and objective. Maximum 100 words."""

    def _build_outlook_prompt(self, result: Dict[str, Any]) -> str:
        """Build prompt for outlook generation."""
        return f"""Generate a brief outlook statement for {result.get('company_name', 'this company')}.

Research Data:
{self._summarize_result(result)}

Focus on: near-term prospects, growth trajectory, key factors.
Be balanced and evidence-based. Maximum 75 words."""

    def _build_recommendation_prompt(self, result: Dict[str, Any]) -> str:
        """Build prompt for recommendation generation."""
        return f"""Generate a brief recommendation for {result.get('company_name', 'this company')}.

Research Data:
{self._summarize_result(result)}

Provide actionable insight. Be objective. Maximum 50 words."""

    def _summarize_result(self, result: Dict[str, Any]) -> str:
        """Summarize research result for prompts."""
        import json
        summary = {
            "company": result.get("company_name"),
            "quality_score": result.get("quality_score"),
            "agent_outputs": {
                k: str(v)[:200] for k, v in result.get("agent_outputs", {}).items()
            }
        }
        return json.dumps(summary, indent=2)[:2000]


# Convenience functions

def create_executive_summary_generator(
    llm_client: Any = None
) -> ExecutiveSummaryGenerator:
    """Create an executive summary generator."""
    return ExecutiveSummaryGenerator(llm_client=llm_client)


async def generate_executive_summary(
    research_result: Dict[str, Any],
    llm_client: Any = None
) -> ExecutiveSummary:
    """Generate executive summary from research result."""
    generator = ExecutiveSummaryGenerator(llm_client=llm_client)
    return await generator.generate(research_result)
