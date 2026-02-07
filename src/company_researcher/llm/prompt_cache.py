"""
Prompt Caching for Anthropic API Calls.

Enables prompt caching to reduce costs by reusing large system prompts
across requests. Can achieve up to 25% cost reduction on repeated prompts.

Usage:
    from company_researcher.llm.prompt_cache import get_prompt_cache

    cache = get_prompt_cache()
    response = cache.create_cached_message(
        model="claude-sonnet-4-20250514",
        system_prompt="You are a financial analyst...",
        user_message="Analyze Tesla's financials"
    )
"""

from threading import Lock
from typing import Any, Dict, List, Optional

from anthropic import Anthropic

from .client_factory import get_anthropic_client


class PromptCache:
    """
    Manages cached prompts for cost optimization.

    Prompt caching allows reusing large system prompts across API calls,
    significantly reducing token costs for repeated analysis patterns.
    """

    def __init__(self, client: Optional[Anthropic] = None):
        """
        Initialize the prompt cache.

        Args:
            client: Optional Anthropic client. If not provided, uses the
                   singleton from client_factory.
        """
        self.client = client or get_anthropic_client()
        self._cache_stats = {"cache_hits": 0, "cache_misses": 0, "tokens_saved": 0}
        self._lock = Lock()

    def create_cached_message(
        self,
        model: str,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1000,
        temperature: float = 0.0,
        **kwargs,
    ) -> Any:
        """
        Create message with prompt caching enabled on system prompt.

        The system prompt is marked for caching, allowing subsequent
        requests with the same system prompt to reuse cached tokens.

        Args:
            model: Model to use (e.g., "claude-sonnet-4-20250514")
            system_prompt: System instructions to cache
            user_message: User message content
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            **kwargs: Additional parameters passed to messages.create

        Returns:
            Anthropic message response object
        """
        return self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=[
                {"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}
            ],
            messages=[{"role": "user", "content": user_message}],
            **kwargs,
        )

    def create_with_cached_context(
        self,
        model: str,
        cached_context: str,
        dynamic_content: str,
        max_tokens: int = 1000,
        temperature: float = 0.0,
        system: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """
        Create message with large context cached in user message.

        Use this when you have a large context (e.g., search results,
        documents) that remains constant across multiple queries.

        Args:
            model: Model to use
            cached_context: Large context to cache (e.g., search results)
            dynamic_content: Variable part of the query
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            system: Optional system prompt (not cached)
            **kwargs: Additional parameters

        Returns:
            Anthropic message response object
        """
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": cached_context,
                        "cache_control": {"type": "ephemeral"},
                    },
                    {"type": "text", "text": dynamic_content},
                ],
            }
        ]

        params = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
            **kwargs,
        }

        if system:
            params["system"] = system

        return self.client.messages.create(**params)

    def create_with_multi_turn_cache(
        self,
        model: str,
        system_prompt: str,
        conversation_history: List[Dict[str, str]],
        new_message: str,
        max_tokens: int = 1000,
        temperature: float = 0.0,
        **kwargs,
    ) -> Any:
        """
        Create message with conversation history cached.

        Useful for multi-turn conversations where you want to cache
        the conversation prefix.

        Args:
            model: Model to use
            system_prompt: System instructions
            conversation_history: List of previous messages
            new_message: New user message
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Returns:
            Anthropic message response object
        """
        # Build messages with cache breakpoint before new message
        messages = []

        for i, msg in enumerate(conversation_history):
            message = {"role": msg["role"], "content": msg["content"]}
            # Add cache control to the last history message
            if i == len(conversation_history) - 1:
                message["content"] = [
                    {"type": "text", "text": msg["content"], "cache_control": {"type": "ephemeral"}}
                ]
            messages.append(message)

        # Add new message
        messages.append({"role": "user", "content": new_message})

        return self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=[
                {"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}
            ],
            messages=messages,
            **kwargs,
        )

    def update_stats(self, response: Any) -> None:
        """
        Update cache statistics from response.

        Args:
            response: Anthropic message response
        """
        with self._lock:
            usage = response.usage
            if hasattr(usage, "cache_creation_input_tokens"):
                self._cache_stats["cache_misses"] += 1
            if hasattr(usage, "cache_read_input_tokens"):
                cached = getattr(usage, "cache_read_input_tokens", 0)
                if cached > 0:
                    self._cache_stats["cache_hits"] += 1
                    # Cached tokens cost ~90% less
                    self._cache_stats["tokens_saved"] += int(cached * 0.9)

    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache_hits, cache_misses, tokens_saved
        """
        with self._lock:
            return self._cache_stats.copy()

    def reset_stats(self) -> None:
        """Reset cache statistics."""
        with self._lock:
            self._cache_stats = {"cache_hits": 0, "cache_misses": 0, "tokens_saved": 0}


# Singleton instance
_prompt_cache: Optional[PromptCache] = None
_cache_lock = Lock()


def get_prompt_cache() -> PromptCache:
    """
    Get singleton prompt cache instance.

    Returns:
        PromptCache instance
    """
    global _prompt_cache
    if _prompt_cache is None:
        with _cache_lock:
            if _prompt_cache is None:
                _prompt_cache = PromptCache()
    return _prompt_cache


def create_cached_analysis_request(
    company_name: str,
    analysis_type: str,
    search_results: str,
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 1000,
) -> Any:
    """
    Convenience function for cached analysis requests.

    Creates a cached request with the analysis type prompt cached
    and dynamic company/search data as the variable part.

    Args:
        company_name: Company to analyze
        analysis_type: Type of analysis (financial, market, product)
        search_results: Formatted search results
        model: Model to use
        max_tokens: Maximum tokens

    Returns:
        Anthropic message response
    """
    cache = get_prompt_cache()

    # Analysis type prompts (these get cached)
    prompts = {
        "financial": """You are a financial analyst reviewing search results about a company.
Extract ALL financial data and metrics from these search results.

Focus on:
1. Revenue: Annual revenue, quarterly revenue, revenue growth
2. Funding: Total funding raised, valuation, recent rounds
3. Profitability: Operating income, net income, profit margins
4. Market Value: Market cap (if public), valuation (if private)
5. Financial Metrics: R&D spending, cash flow, any other metrics

Requirements:
- Be specific with numbers and dates
- Include sources for each data point
- Note if data is missing or unavailable
- Format as bullet points""",
        "market": """You are a market analyst reviewing search results about a company.
Extract ALL market positioning and competitive information.

Focus on:
1. Market Position: Market share, ranking in industry
2. Competitors: Direct and indirect competitors
3. Industry Trends: Market size, growth rates
4. Competitive Advantages: Unique strengths, moats
5. Market Challenges: Threats, weaknesses

Requirements:
- Be specific with market data
- Include competitor comparisons
- Note market trends and dynamics""",
        "product": """You are a product analyst reviewing search results about a company.
Extract ALL product and technology information.

Focus on:
1. Products/Services: Main offerings, features
2. Technology: Tech stack, innovations
3. Customers: Target market, key clients
4. Pricing: Business model, pricing structure
5. Roadmap: Upcoming features, strategic direction

Requirements:
- List all products and services
- Note technology differentiators
- Include customer segments""",
    }

    system_prompt = prompts.get(analysis_type, prompts["financial"])

    user_message = f"""Company: {company_name}

Search Results:
{search_results}

Extract the {analysis_type} data now:"""

    return cache.create_cached_message(
        model=model, system_prompt=system_prompt, user_message=user_message, max_tokens=max_tokens
    )
