"""
Claude Web Search Tool Integration.

Enables real-time web search via Claude API for up-to-date company information.

Cost: $10 per 1,000 searches (separate from token costs)
Results are processed through Claude for analysis and summarization.

Usage:
    from company_researcher.llm.web_search import get_claude_web_search

    search = get_claude_web_search()

    # Simple search
    result = search.search("Tesla Q4 2024 earnings")
    print(result["content"])
    print(result["sources"])

    # Company news
    news = search.research_company_news("Apple", topics=["iPhone", "AI"])

    # Competitive intelligence
    intel = search.get_competitive_intelligence("NVIDIA", ["AMD", "Intel"])
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
import logging

from anthropic import Anthropic

from .client_factory import get_anthropic_client
from .cost_tracker import get_cost_tracker

logger = logging.getLogger(__name__)


@dataclass
class WebSearchResult:
    """Result from a web search query."""
    query: str
    content: str
    sources: List[str] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    search_count: int = 1
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def estimated_cost(self) -> float:
        """Estimated cost for this search (search fee only)."""
        return self.search_count * 0.01  # $0.01 per search

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "content": self.content,
            "sources": self.sources,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "search_count": self.search_count,
            "estimated_cost": self.estimated_cost,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class ClaudeWebSearch:
    """
    Real-time web search via Claude API.

    Uses Claude's built-in web search tool to retrieve and analyze
    current information from the web.

    Cost: $10 per 1,000 searches ($0.01 per search)
    Note: Token costs are additional.

    Features:
    - Real-time web information
    - Automatic source citation
    - Integrated analysis
    - Usage tracking
    """

    def __init__(
        self,
        client: Optional[Anthropic] = None,
        default_model: str = "claude-sonnet-4-5-20250929",
        track_costs: bool = True
    ):
        """
        Initialize Claude Web Search.

        Args:
            client: Optional Anthropic client (uses shared if not provided)
            default_model: Default model for web search queries
            track_costs: Whether to track costs via CostTracker
        """
        self.client = client or get_anthropic_client()
        self.default_model = default_model
        self.track_costs = track_costs
        self._search_count = 0
        self._lock = Lock()

    def search(
        self,
        query: str,
        context: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 2000,
        company_name: Optional[str] = None
    ) -> WebSearchResult:
        """
        Perform a web search with Claude analysis.

        Args:
            query: Search query string
            context: Additional context for the search
            model: Model to use (defaults to instance default)
            max_tokens: Maximum response tokens
            company_name: Optional company name for cost tracking

        Returns:
            WebSearchResult with content and sources
        """
        model = model or self.default_model

        # Build the prompt
        prompt = f"Search the web for: {query}"
        if context:
            prompt += f"\n\nAdditional context: {context}"

        prompt += """

After searching, provide:
1. A clear summary of the findings
2. Key facts with specific dates/numbers
3. Source citations

Format sources as a list at the end."""

        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                tools=[{"type": "web_search"}],
                messages=[{"role": "user", "content": prompt}]
            )

            # Update search count
            with self._lock:
                self._search_count += 1

            # Extract content and sources
            content = ""
            sources = []

            for block in response.content:
                if hasattr(block, "text"):
                    content = block.text
                elif hasattr(block, "type") and block.type == "tool_use":
                    # Extract source URLs if available in tool response
                    if hasattr(block, "input"):
                        if isinstance(block.input, dict) and "urls" in block.input:
                            sources.extend(block.input["urls"])

            # Track costs
            if self.track_costs:
                tracker = get_cost_tracker()
                tracker.record_call(
                    model=model,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    agent_name="web_search",
                    company_name=company_name or "unknown"
                )

            result = WebSearchResult(
                query=query,
                content=content,
                sources=sources,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                metadata={"model": model, "context": context}
            )

            logger.info(f"[WebSearch] Query: {query[:50]}... | Sources: {len(sources)}")
            return result

        except Exception as e:
            logger.error(f"[WebSearch] Error: {e}")
            return WebSearchResult(
                query=query,
                content=f"Search failed: {str(e)}",
                metadata={"error": str(e)}
            )

    def research_company_news(
        self,
        company_name: str,
        topics: Optional[List[str]] = None,
        days_back: int = 30,
        model: Optional[str] = None
    ) -> WebSearchResult:
        """
        Get latest news for a company.

        Args:
            company_name: Company to research
            topics: Specific topics to focus on
            days_back: How many days back to search
            model: Model to use

        Returns:
            WebSearchResult with news analysis
        """
        topics_str = ", ".join(topics) if topics else "latest news and developments"

        query = f"{company_name} {topics_str} last {days_back} days"

        context = f"""Research {company_name} focusing on:
1. Recent announcements and press releases
2. Financial results or guidance updates
3. Product launches or updates
4. Leadership changes
5. Market reactions and analyst commentary

Prioritize information from the past {days_back} days.
Include specific dates for all news items.
Cite sources for all claims."""

        return self.search(
            query=query,
            context=context,
            model=model,
            max_tokens=3000,
            company_name=company_name
        )

    def get_competitive_intelligence(
        self,
        company_name: str,
        competitors: List[str],
        aspects: Optional[List[str]] = None,
        model: Optional[str] = None
    ) -> WebSearchResult:
        """
        Get competitive analysis from recent sources.

        Args:
            company_name: Target company
            competitors: List of competitor names
            aspects: Specific aspects to compare
            model: Model to use

        Returns:
            WebSearchResult with competitive analysis
        """
        competitors_str = ", ".join(competitors)
        aspects_str = ", ".join(aspects) if aspects else "market share, products, strategy"

        query = f"{company_name} vs {competitors_str} comparison {aspects_str}"

        context = f"""Compare {company_name} with {competitors_str}:

1. Market Position
   - Market share estimates
   - Recent market share changes
   - Geographic presence

2. Product/Service Comparison
   - Key offerings
   - Recent launches
   - Competitive advantages

3. Financial Comparison
   - Revenue/growth comparison
   - Profitability metrics
   - Investment levels

4. Strategic Moves
   - Recent acquisitions
   - Partnerships
   - Strategic pivots

5. Analyst Perspectives
   - Recent analyst opinions
   - Market sentiment

Use the most recent data available.
Cite all sources with dates."""

        return self.search(
            query=query,
            context=context,
            model=model,
            max_tokens=4000,
            company_name=company_name
        )

    def get_financial_updates(
        self,
        company_name: str,
        ticker: Optional[str] = None,
        model: Optional[str] = None
    ) -> WebSearchResult:
        """
        Get latest financial information for a company.

        Args:
            company_name: Company name
            ticker: Optional stock ticker
            model: Model to use

        Returns:
            WebSearchResult with financial updates
        """
        ticker_str = f" ({ticker})" if ticker else ""
        query = f"{company_name}{ticker_str} latest financial results earnings guidance"

        context = f"""Find the latest financial information for {company_name}:

1. Most Recent Earnings
   - Quarter and year
   - Revenue figures
   - EPS (actual vs expected)
   - Key highlights

2. Guidance
   - Forward guidance
   - Updated forecasts

3. Key Metrics
   - Growth rates
   - Margins
   - Notable changes

4. Market Reaction
   - Stock price movement
   - Analyst reactions

Focus on official company releases and reputable financial sources.
Include specific numbers and dates."""

        return self.search(
            query=query,
            context=context,
            model=model,
            max_tokens=2500,
            company_name=company_name
        )

    def get_industry_trends(
        self,
        industry: str,
        company_context: Optional[str] = None,
        model: Optional[str] = None
    ) -> WebSearchResult:
        """
        Get current trends for an industry.

        Args:
            industry: Industry name (e.g., "electric vehicles", "AI chips")
            company_context: Optional company for context
            model: Model to use

        Returns:
            WebSearchResult with industry analysis
        """
        query = f"{industry} industry trends market analysis 2024 2025"

        context_str = f" in context of {company_context}" if company_context else ""
        context = f"""Analyze current trends in the {industry} industry{context_str}:

1. Market Size & Growth
   - Current market size
   - Growth projections
   - Key drivers

2. Major Trends
   - Technology trends
   - Regulatory changes
   - Consumer behavior shifts

3. Key Players
   - Market leaders
   - Emerging challengers
   - Recent M&A activity

4. Challenges & Risks
   - Industry headwinds
   - Disruption risks

5. Outlook
   - Short-term outlook
   - Long-term projections

Use recent market research and analyst reports."""

        return self.search(
            query=query,
            context=context,
            model=model,
            max_tokens=3000,
            company_name=company_context
        )

    def get_search_stats(self) -> Dict[str, Any]:
        """
        Get web search usage statistics.

        Returns:
            Dictionary with usage stats
        """
        with self._lock:
            return {
                "total_searches": self._search_count,
                "estimated_cost": self._search_count * 0.01,  # $0.01 per search
                "cost_per_1k": 10.0  # $10 per 1,000 searches
            }

    def reset_stats(self) -> None:
        """Reset search statistics."""
        with self._lock:
            self._search_count = 0


# Singleton instance
_web_search: Optional[ClaudeWebSearch] = None
_search_lock = Lock()


def get_claude_web_search() -> ClaudeWebSearch:
    """
    Get singleton ClaudeWebSearch instance.

    Returns:
        ClaudeWebSearch instance
    """
    global _web_search
    if _web_search is None:
        with _search_lock:
            if _web_search is None:
                _web_search = ClaudeWebSearch()
    return _web_search


def reset_web_search() -> None:
    """Reset web search instance (for testing)."""
    global _web_search
    _web_search = None
