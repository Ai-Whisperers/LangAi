"""
Centralized LLM Client Factory.

This module provides a singleton pattern for LLM clients to eliminate
duplication across 22+ agent files.

Usage:
    from company_researcher.llm import get_anthropic_client, get_tavily_client

    # Get shared client instances
    anthropic = get_anthropic_client()
    tavily = get_tavily_client()

    # Or use the factory for more control
    factory = LLMClientFactory()
    client = factory.get_anthropic()
"""

from typing import Optional, Any, Dict
from functools import lru_cache
import threading

from anthropic import Anthropic


class LLMClientFactory:
    """
    Factory for creating and managing LLM client instances.

    Implements singleton pattern with thread-safety for client reuse.
    Eliminates duplicated client initialization across agent files.
    """

    _instance: Optional['LLMClientFactory'] = None
    _lock = threading.Lock()

    # Client instances
    _anthropic_client: Optional[Anthropic] = None
    _tavily_client: Optional[Any] = None

    def __new__(cls) -> 'LLMClientFactory':
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize factory (only runs once due to singleton)."""
        # Lazy import to avoid circular dependencies
        if not hasattr(self, '_initialized'):
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
        if api_key:
            # Custom key - create new instance
            return Anthropic(api_key=api_key)

        # Use shared instance
        if self._anthropic_client is None:
            with self._lock:
                if self._anthropic_client is None:
                    self._anthropic_client = Anthropic(
                        api_key=self.config.anthropic_api_key
                    )
        return self._anthropic_client

    def get_tavily(self, api_key: Optional[str] = None) -> Any:
        """
        Get Tavily client instance for web search.

        Args:
            api_key: Optional API key override. If None, uses config.

        Returns:
            TavilyClient instance
        """
        from tavily import TavilyClient

        if api_key:
            return TavilyClient(api_key=api_key)

        if self._tavily_client is None:
            with self._lock:
                if self._tavily_client is None:
                    self._tavily_client = TavilyClient(
                        api_key=self.config.tavily_api_key
                    )
        return self._tavily_client

    def create_message(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system: Optional[str] = None
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
            "messages": messages
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
    system: Optional[str] = None
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
        prompt=prompt,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system
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
