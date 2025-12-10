"""
Google Gemini API integration with search grounding.

Features:
- Native Google Search grounding with citations
- Up to 2M token context (largest available)
- Context caching (75% savings)
- Ultra-low cost Flash-8B model

Pricing (per 1M tokens):
- Flash-8B: $0.04 input, $0.15 output (best value)
- 1.5 Flash: $0.08 input, $0.30 output
- 1.5 Pro: $1.25 input, $5.00 output (2M context)
- Grounding: $35/1K queries (free during preview)

Usage:
    from company_researcher.llm.gemini_client import get_gemini_client

    client = get_gemini_client()

    # Search with grounding (returns citations)
    result = client.search_with_grounding("Tesla Q4 2024 earnings")
    print(result["sources"])

    # Long document analysis (up to 2M tokens)
    analysis = client.analyze_long_document(annual_report, "Summarize key financials")
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from threading import Lock
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

# Try to import google-generativeai
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Run: pip install google-generativeai")


# Pricing per 1M tokens
GEMINI_PRICING = {
    "gemini-1.5-flash-8b": {
        "input": 0.0375,
        "output": 0.15,
        "input_long": 0.075,  # >128K tokens
        "output_long": 0.30,
        "context_window": 1_000_000
    },
    "gemini-1.5-flash": {
        "input": 0.075,
        "output": 0.30,
        "input_long": 0.15,
        "output_long": 0.60,
        "context_window": 1_000_000
    },
    "gemini-1.5-pro": {
        "input": 1.25,
        "output": 5.00,
        "input_long": 2.50,
        "output_long": 10.00,
        "context_window": 2_000_000
    },
    "gemini-2.0-flash": {
        "input": 0.10,
        "output": 0.40,
        "input_long": 0.20,
        "output_long": 0.80,
        "context_window": 1_000_000
    },
    "grounding": {
        "per_1k_queries": 35.00  # Free during preview
    }
}


@dataclass
class GeminiSource:
    """Source from grounding."""
    title: str
    uri: str
    snippet: Optional[str] = None


@dataclass
class GeminiResponse:
    """Response from Gemini API."""
    content: str
    sources: List[GeminiSource] = field(default_factory=list)
    grounding_used: bool = False
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    cost: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "sources": [{"title": s.title, "uri": s.uri, "snippet": s.snippet} for s in self.sources],
            "grounding_used": self.grounding_used,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "model": self.model,
            "cost": self.cost
        }


class GeminiClient:
    """
    Gemini API client with search grounding.

    Best for:
    - Search with automatic citations
    - Long document analysis (up to 2M tokens)
    - High-volume, low-cost processing
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "gemini-1.5-flash-8b"
    ):
        """
        Initialize Gemini client.

        Args:
            api_key: Google API key (or GOOGLE_API_KEY env var)
            default_model: Default model to use
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("Google API key not found. Set GOOGLE_API_KEY env var.")
        else:
            genai.configure(api_key=self.api_key)

        self.default_model = default_model
        self._total_cost = 0.0
        self._total_calls = 0
        self._grounding_queries = 0
        self._lock = Lock()

    def _calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        grounding_used: bool = False
    ) -> float:
        """Calculate cost for a request."""
        pricing = GEMINI_PRICING.get(model, GEMINI_PRICING["gemini-1.5-flash-8b"])

        # Check if long context pricing applies (>128K tokens)
        if input_tokens > 128_000:
            input_price = pricing.get("input_long", pricing["input"])
            output_price = pricing.get("output_long", pricing["output"])
        else:
            input_price = pricing["input"]
            output_price = pricing["output"]

        cost = (input_tokens / 1_000_000) * input_price
        cost += (output_tokens / 1_000_000) * output_price

        # Grounding cost (free during preview, but track for future)
        if grounding_used:
            # Currently free, but will be $35/1K queries
            pass

        return cost

    def create_message(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.0
    ) -> GeminiResponse:
        """
        Create a completion without grounding.

        Args:
            prompt: User prompt
            system: System instruction
            model: Model to use
            max_tokens: Maximum output tokens
            temperature: Sampling temperature

        Returns:
            GeminiResponse
        """
        model_name = model or self.default_model
        model_instance = genai.GenerativeModel(
            model_name,
            system_instruction=system,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature
            }
        )

        response = model_instance.generate_content(prompt)

        # Get usage (approximate if not available)
        input_tokens = response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else len(prompt) // 4
        output_tokens = response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else len(response.text) // 4

        cost = self._calculate_cost(model_name, input_tokens, output_tokens)

        with self._lock:
            self._total_cost += cost
            self._total_calls += 1

        return GeminiResponse(
            content=response.text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model_name,
            cost=cost
        )

    def search_with_grounding(
        self,
        query: str,
        context: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4000
    ) -> GeminiResponse:
        """
        Search with Google grounding - returns citations.

        This enables Claude-like web search but with automatic
        source citations from Google Search.

        Args:
            query: Search query
            context: Additional context
            model: Model to use
            max_tokens: Maximum output tokens

        Returns:
            GeminiResponse with sources
        """
        model_name = model or self.default_model

        # Create model with Google Search tool
        model_instance = genai.GenerativeModel(
            model_name,
            tools=[genai.Tool(google_search=genai.GoogleSearch())],
            generation_config={"max_output_tokens": max_tokens}
        )

        prompt = query
        if context:
            prompt = f"{context}\n\nSearch for: {query}"

        prompt += "\n\nProvide your answer based on the search results. Cite your sources."

        response = model_instance.generate_content(prompt)

        # Extract grounding sources
        sources = []
        grounding_used = False

        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                grounding_used = True
                grounding = candidate.grounding_metadata

                # Extract search entry point if available
                if hasattr(grounding, 'grounding_chunks'):
                    for chunk in grounding.grounding_chunks:
                        if hasattr(chunk, 'web'):
                            sources.append(GeminiSource(
                                title=getattr(chunk.web, 'title', 'Unknown'),
                                uri=getattr(chunk.web, 'uri', ''),
                                snippet=getattr(chunk, 'text', None)
                            ))

        # Get usage
        input_tokens = response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else len(prompt) // 4
        output_tokens = response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else len(response.text) // 4

        cost = self._calculate_cost(model_name, input_tokens, output_tokens, grounding_used)

        with self._lock:
            self._total_cost += cost
            self._total_calls += 1
            if grounding_used:
                self._grounding_queries += 1

        return GeminiResponse(
            content=response.text,
            sources=sources,
            grounding_used=grounding_used,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model_name,
            cost=cost
        )

    def research_company_news(
        self,
        company_name: str,
        topics: Optional[List[str]] = None,
        days_back: int = 30,
        model: Optional[str] = None
    ) -> GeminiResponse:
        """
        Get latest news for a company with citations.

        Args:
            company_name: Company to research
            topics: Specific topics to focus on
            days_back: How many days back to search

        Returns:
            GeminiResponse with news and sources
        """
        topics_str = ", ".join(topics) if topics else "latest news and developments"
        query = f"{company_name} {topics_str} news last {days_back} days"

        context = f"""Research {company_name} focusing on recent news.
Include:
1. Recent announcements and press releases
2. Financial results or guidance updates
3. Product launches or updates
4. Leadership changes
5. Market reactions

Prioritize information from the past {days_back} days.
Include specific dates for all news items."""

        return self.search_with_grounding(query, context, model)

    def analyze_long_document(
        self,
        document: str,
        analysis_prompt: str,
        model: str = "gemini-1.5-pro"
    ) -> GeminiResponse:
        """
        Analyze documents up to 2M tokens.

        Best for: Annual reports, large document sets, multiple files.

        Args:
            document: Document text (up to 2M tokens)
            analysis_prompt: What to analyze
            model: Model to use (default: 1.5 Pro for 2M context)

        Returns:
            GeminiResponse with analysis
        """
        model_instance = genai.GenerativeModel(
            model,
            generation_config={"max_output_tokens": 8000}
        )

        full_prompt = f"""{analysis_prompt}

Document:
{document}"""

        response = model_instance.generate_content(full_prompt)

        input_tokens = response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else len(full_prompt) // 4
        output_tokens = response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else len(response.text) // 4

        cost = self._calculate_cost(model, input_tokens, output_tokens)

        with self._lock:
            self._total_cost += cost
            self._total_calls += 1

        return GeminiResponse(
            content=response.text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            cost=cost
        )

    def get_competitive_intelligence(
        self,
        company_name: str,
        competitors: List[str],
        model: Optional[str] = None
    ) -> GeminiResponse:
        """
        Get competitive analysis with citations.

        Args:
            company_name: Target company
            competitors: List of competitor names

        Returns:
            GeminiResponse with competitive analysis
        """
        competitors_str = ", ".join(competitors)
        query = f"{company_name} vs {competitors_str} market share competition analysis"

        context = f"""Compare {company_name} with {competitors_str}:
1. Market Position (market share, trends)
2. Product/Service Comparison
3. Financial Comparison (if available)
4. Recent Strategic Moves
5. Analyst Perspectives

Use the most recent data available and cite all sources."""

        return self.search_with_grounding(query, context, model)

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        with self._lock:
            return {
                "total_calls": self._total_calls,
                "total_cost": self._total_cost,
                "grounding_queries": self._grounding_queries,
                "avg_cost_per_call": self._total_cost / self._total_calls if self._total_calls > 0 else 0
            }

    def reset_stats(self) -> None:
        """Reset usage statistics."""
        with self._lock:
            self._total_cost = 0.0
            self._total_calls = 0
            self._grounding_queries = 0


# Singleton instance
_gemini_client: Optional[GeminiClient] = None
_client_lock = Lock()


def get_gemini_client() -> GeminiClient:
    """Get singleton Gemini client instance."""
    global _gemini_client
    if _gemini_client is None:
        with _client_lock:
            if _gemini_client is None:
                _gemini_client = GeminiClient()
    return _gemini_client


def reset_gemini_client() -> None:
    """Reset Gemini client instance (for testing)."""
    global _gemini_client
    _gemini_client = None
