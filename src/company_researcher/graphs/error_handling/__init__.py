"""
Error Handling Package - Phase 16

This package provides robust error handling for LangGraph workflows:
- Automatic retry with exponential backoff
- Fallback node implementations
- Error boundaries for graceful degradation
- Circuit breaker for external services

Usage:
    from company_researcher.graphs.error_handling import (
        with_retry,
        with_fallback,
        create_error_boundary,
        CircuitBreaker,
    )

    # Wrap node with retry
    @with_retry(max_attempts=3)
    def my_node(state):
        ...

    # Create node with fallback
    safe_node = with_fallback(primary_node, fallback_node)
"""

from .retry import (
    with_retry,
    RetryConfig,
    RetryStrategy,
)
from .fallback import (
    with_fallback,
    create_error_boundary,
    FallbackConfig,
)
from .circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    CircuitBreakerConfig,
)

__all__ = [
    # Retry
    "with_retry",
    "RetryConfig",
    "RetryStrategy",
    # Fallback
    "with_fallback",
    "create_error_boundary",
    "FallbackConfig",
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitState",
    "CircuitBreakerConfig",
]
