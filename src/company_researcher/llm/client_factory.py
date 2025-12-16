"""
Centralized LLM Client Factory.

This module provides a singleton pattern for LLM clients to eliminate
duplication across 22+ agent files. Also provides access to enhanced
features like prompt caching, streaming, and cost tracking.

Usage:
    from company_researcher.llm import get_anthropic_client, get_tavily_client

    # Get shared client instances
    anthropic = get_anthropic_client()
    tavily = get_tavily_client()

    # Enhanced features
    from company_researcher.llm import (
        get_prompt_cache,      # Prompt caching for cost reduction
        get_streaming_client,  # Real-time streaming responses
        get_cost_tracker,      # Detailed cost tracking
        safe_extract_text,     # Safe response text extraction
    )

    # Or use the factory for more control
    factory = LLMClientFactory()
    client = factory.get_anthropic()
"""

import threading
from typing import Any, Optional

import httpx

from ..utils import get_logger

logger = get_logger(__name__)

from anthropic import Anthropic


class LLMClientFactory:
    """
    Factory for creating and managing LLM client instances.

    Implements singleton pattern with thread-safety for client reuse.
    Eliminates duplicated client initialization across agent files.
    """

    _instance: Optional["LLMClientFactory"] = None
    _lock = threading.Lock()

    # Client instances
    _anthropic_client: Optional[Anthropic] = None
    _tavily_client: Optional[Any] = None

    def __new__(cls) -> "LLMClientFactory":
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize factory (only runs once due to singleton)."""
        # Lazy import to avoid circular dependencies
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._config = None

    @property
    def config(self):
        """Lazy load config to avoid circular imports."""
        if self._config is None:
            from ..config import get_config

            self._config = get_config()
        return self._config

    def get_anthropic(self, api_key: Optional[str] = None) -> Anthropic:
        """
        Get Anthropic client instance.

        Args:
            api_key: Optional API key override. If None, uses config.

        Returns:
            Anthropic client instance
        """
        # Create timeout configuration
        timeout = httpx.Timeout(
            timeout=self.config.api_timeout_seconds, connect=self.config.api_connect_timeout_seconds
        )

        if api_key:
            # Custom key - create new instance with timeout
            return Anthropic(api_key=api_key, timeout=timeout)

        # Use shared instance
        if self._anthropic_client is None:
            with self._lock:
                if self._anthropic_client is None:
                    self._anthropic_client = Anthropic(
                        api_key=self.config.anthropic_api_key, timeout=timeout
                    )
        return self._anthropic_client

    def get_tavily(self, api_key: Optional[str] = None) -> Any:
        """
        Get Tavily client instance for web search.

        Args:
            api_key: Optional API key override. If None, uses config.

        Returns:
            TavilyClient instance

        Note:
            Tavily SDK uses httpx internally. While it doesn't expose
            timeout configuration directly, the search_timeout_seconds
            config is available for wrapper implementations.
        """
        from tavily import TavilyClient

        if api_key:
            return TavilyClient(api_key=api_key)

        if self._tavily_client is None:
            with self._lock:
                if self._tavily_client is None:
                    self._tavily_client = TavilyClient(api_key=self.config.tavily_api_key)
        return self._tavily_client

    def search_with_timeout(self, query: str, **kwargs) -> Any:
        """
        Perform a Tavily search with timeout protection.

        Args:
            query: Search query
            **kwargs: Additional arguments for TavilyClient.search()

        Returns:
            Search results

        Raises:
            TimeoutError: If search exceeds configured timeout
        """
        import concurrent.futures

        client = self.get_tavily()
        timeout = self.config.search_timeout_seconds

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(client.search, query, **kwargs)
            try:
                return future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                raise TimeoutError(f"Tavily search timed out after {timeout} seconds")

    def create_message(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system: Optional[str] = None,
    ) -> Any:
        """
        Convenience method to create an Anthropic message.

        Args:
            prompt: User message content
            model: Model to use (default from config)
            max_tokens: Max output tokens (default from config)
            temperature: Temperature (default from config)
            system: Optional system message

        Returns:
            Anthropic message response
        """
        client = self.get_anthropic()

        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": model or self.config.llm_model,
            "max_tokens": max_tokens or self.config.llm_max_tokens,
            "temperature": temperature if temperature is not None else self.config.llm_temperature,
            "messages": messages,
        }

        if system:
            kwargs["system"] = system

        return client.messages.create(**kwargs)

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost for token usage.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        return self.config.calculate_llm_cost(input_tokens, output_tokens)

    def reset(self) -> None:
        """Reset all client instances (useful for testing)."""
        with self._lock:
            self._anthropic_client = None
            self._tavily_client = None
            self._config = None


# ============================================================================
# Module-level convenience functions
# ============================================================================

_factory: Optional[LLMClientFactory] = None


def get_factory() -> LLMClientFactory:
    """Get the global factory instance."""
    global _factory
    if _factory is None:
        _factory = LLMClientFactory()
    return _factory


def get_anthropic_client(api_key: Optional[str] = None) -> Anthropic:
    """
    Get Anthropic client instance.

    This is the primary function to use instead of:
        client = Anthropic(api_key=config.anthropic_api_key)

    Args:
        api_key: Optional API key override

    Returns:
        Anthropic client instance
    """
    return get_factory().get_anthropic(api_key)


def get_tavily_client(api_key: Optional[str] = None) -> Any:
    """
    Get Tavily client instance.

    This is the primary function to use instead of:
        client = TavilyClient(api_key=config.tavily_api_key)

    Args:
        api_key: Optional API key override

    Returns:
        TavilyClient instance
    """
    return get_factory().get_tavily(api_key)


def create_message(
    prompt: str,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    system: Optional[str] = None,
) -> Any:
    """
    Create an Anthropic message with default config.

    Simplifies the common pattern of:
        config = get_config()
        client = Anthropic(api_key=config.anthropic_api_key)
        response = client.messages.create(
            model=config.llm_model,
            max_tokens=config.llm_max_tokens,
            temperature=config.llm_temperature,
            messages=[{"role": "user", "content": prompt}]
        )

    To:
        response = create_message(prompt)
    """
    return get_factory().create_message(
        prompt=prompt, model=model, max_tokens=max_tokens, temperature=temperature, system=system
    )


def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculate cost for token usage."""
    return get_factory().calculate_cost(input_tokens, output_tokens)


def reset_clients() -> None:
    """Reset all client instances."""
    global _factory
    if _factory:
        _factory.reset()
    _factory = None


def search_with_timeout(query: str, **kwargs) -> Any:
    """
    Perform a Tavily search with timeout protection.

    Args:
        query: Search query
        **kwargs: Additional arguments for TavilyClient.search()

    Returns:
        Search results

    Raises:
        TimeoutError: If search exceeds configured timeout
    """
    return get_factory().search_with_timeout(query, **kwargs)


# ============================================================================
# Enhanced Feature Imports (lazy loaded)
# ============================================================================


def get_prompt_cache():
    """
    Get the prompt cache for cost-optimized API calls.

    Prompt caching can reduce costs by up to 25% by reusing
    large system prompts across requests.

    Returns:
        PromptCache instance

    Example:
        cache = get_prompt_cache()
        response = cache.create_cached_message(
            model="claude-sonnet-4-20250514",
            system_prompt="You are a financial analyst...",
            user_message="Analyze Tesla's financials"
        )
    """
    from .prompt_cache import get_prompt_cache as _get_prompt_cache

    return _get_prompt_cache()


def get_streaming_client():
    """
    Get the streaming client for real-time responses.

    Streaming provides better UX by showing results as they're generated.

    Returns:
        StreamingClient instance

    Example:
        client = get_streaming_client()
        result = client.stream_message(
            model="claude-sonnet-4-20250514",
            messages=[{"role": "user", "content": "Analyze Tesla"}],
            on_text=lambda chunk: print(chunk, end="", flush=True)
        )
    """
    from .streaming import get_streaming_client as _get_streaming_client

    return _get_streaming_client()


def get_cost_tracker():
    """
    Get the cost tracker for detailed API cost monitoring.

    Tracks costs per agent, per company, and per research run.

    Returns:
        CostTracker instance

    Example:
        tracker = get_cost_tracker()
        cost = tracker.record_call(
            model="claude-sonnet-4-20250514",
            input_tokens=1000,
            output_tokens=500,
            agent_name="financial"
        )
        summary = tracker.get_summary()
    """
    from .cost_tracker import get_cost_tracker as _get_cost_tracker

    return _get_cost_tracker()


class LLMResponseError(Exception):
    """Raised when LLM response extraction fails."""


def safe_extract_text(
    response: Any, default: Optional[str] = None, agent_name: str = "unknown"
) -> str:
    """
    Safely extract text from an Anthropic message response.

    This function handles the common pattern of accessing response.content[0].text
    with proper error handling to prevent crashes from empty or malformed responses.

    Args:
        response: Anthropic message response object
        default: Default value to return if extraction fails. If None, raises exception.
        agent_name: Name of the calling agent for logging purposes

    Returns:
        Extracted text content

    Raises:
        LLMResponseError: If extraction fails and no default provided

    Example:
        response = client.messages.create(...)
        text = safe_extract_text(response, agent_name="financial")
    """
    try:
        # Check if response has content attribute
        if not hasattr(response, "content"):
            raise LLMResponseError("Response has no 'content' attribute")

        # Check if content is not empty
        if not response.content:
            raise LLMResponseError("Response content is empty")

        # Check if first content block exists and has text
        first_block = response.content[0]
        if not hasattr(first_block, "text"):
            raise LLMResponseError(
                f"First content block has no 'text' attribute. "
                f"Block type: {type(first_block).__name__}"
            )

        text = first_block.text
        if not isinstance(text, str):
            raise LLMResponseError(f"Content text is not a string: {type(text).__name__}")

        return text

    except (IndexError, AttributeError, TypeError) as e:
        error_msg = f"[{agent_name}] Failed to extract text from LLM response: {e}"
        logger.warning(error_msg)

        if default is not None:
            logger.info(f"[{agent_name}] Using default value for response")
            return default

        raise LLMResponseError(error_msg) from e

    except LLMResponseError:
        if default is not None:
            logger.warning(f"[{agent_name}] LLM response error, using default value")
            return default
        raise


def safe_extract_json(
    response: Any, default: Optional[Any] = None, agent_name: str = "unknown"
) -> Any:
    """
    Safely extract and parse JSON from an Anthropic message response.

    Handles common patterns:
    - JSON wrapped in ```json code blocks
    - JSON wrapped in ``` code blocks
    - Raw JSON responses
    - JSON embedded in text

    Args:
        response: Anthropic message response object
        default: Default value if extraction/parsing fails
        agent_name: Name of the calling agent for logging

    Returns:
        Parsed JSON object (dict or list)

    Raises:
        LLMResponseError: If extraction/parsing fails and no default provided
    """
    import json

    try:
        text = safe_extract_text(response, agent_name=agent_name)

        # Try to extract JSON from code blocks
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        text = text.strip()

        # Try to find JSON object boundaries
        start_idx = text.find("{")
        end_idx = text.rfind("}")

        if start_idx >= 0 and end_idx > start_idx:
            json_str = text[start_idx : end_idx + 1]
            return json.loads(json_str)

        # Try parsing as array
        start_idx = text.find("[")
        end_idx = text.rfind("]")

        if start_idx >= 0 and end_idx > start_idx:
            json_str = text[start_idx : end_idx + 1]
            return json.loads(json_str)

        # Try parsing entire text
        return json.loads(text)

    except (json.JSONDecodeError, LLMResponseError) as e:
        error_msg = f"[{agent_name}] Failed to extract JSON from response: {e}"
        logger.warning(error_msg)

        if default is not None:
            logger.info(f"[{agent_name}] Using default value for JSON extraction")
            return default

        raise LLMResponseError(error_msg) from e


def track_api_call(
    model: str,
    input_tokens: int,
    output_tokens: int,
    agent_name: str = "",
    company_name: str = "",
    cached_tokens: int = 0,
) -> float:
    """
    Convenience function to track an API call and return cost.

    Args:
        model: Model used
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        agent_name: Name of agent making the call
        company_name: Company being researched
        cached_tokens: Number of cached tokens

    Returns:
        Calculated cost in USD
    """
    tracker = get_cost_tracker()
    return tracker.record_call(
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        agent_name=agent_name,
        company_name=company_name,
        cached_tokens=cached_tokens,
    )
