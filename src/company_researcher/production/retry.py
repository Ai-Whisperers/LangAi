"""
Retry Utilities (Phase 20.2).

Robust retry mechanisms:
- Configurable retry policies
- Exponential backoff
- Jitter for avoiding thundering herd
- Circuit breaker integration
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Optional, TypeVar

T = TypeVar("T")


# ============================================================================
# Configuration
# ============================================================================


@dataclass
class RetryConfig:
    """Retry configuration."""

    max_attempts: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    backoff_multiplier: float = 2.0
    jitter: bool = True
    jitter_range: float = 0.1  # ±10%
    retryable_exceptions: tuple = (Exception,)
    non_retryable_exceptions: tuple = ()

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for an attempt."""
        delay = self.initial_delay * (self.backoff_multiplier ** (attempt - 1))
        delay = min(delay, self.max_delay)

        if self.jitter:
            jitter = delay * self.jitter_range
            delay += random.uniform(-jitter, jitter)

        return max(0, delay)


# ============================================================================
# Retry Policy
# ============================================================================


class RetryPolicy:
    """
    Configurable retry policy.

    Usage:
        policy = RetryPolicy(max_attempts=3, backoff=2.0)

        @policy
        def flaky_operation():
            ...

        # Or call directly
        result = policy.execute(flaky_operation)
    """

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff: float = 2.0,
        jitter: bool = True,
        retryable: Optional[tuple] = None,
        non_retryable: Optional[tuple] = None,
        on_retry: Optional[Callable] = None,
    ):
        """
        Initialize retry policy.

        Args:
            max_attempts: Maximum retry attempts
            initial_delay: Initial delay between retries
            max_delay: Maximum delay between retries
            backoff: Backoff multiplier
            jitter: Add random jitter to delays
            retryable: Tuple of retryable exception types
            non_retryable: Tuple of non-retryable exception types
            on_retry: Callback on each retry
        """
        self._config = RetryConfig(
            max_attempts=max_attempts,
            initial_delay=initial_delay,
            max_delay=max_delay,
            backoff_multiplier=backoff,
            jitter=jitter,
            retryable_exceptions=retryable or (Exception,),
            non_retryable_exceptions=non_retryable or (),
        )
        self._on_retry = on_retry
        self._logger = logging.getLogger("retry")

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Use as decorator."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.execute(func, *args, **kwargs)

        return wrapper

    def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute function with retry.

        Args:
            func: Function to execute
            *args, **kwargs: Arguments to pass

        Returns:
            Function result

        Raises:
            Last exception if all retries fail
        """
        last_exception = None

        for attempt in range(1, self._config.max_attempts + 1):
            try:
                return func(*args, **kwargs)

            except self._config.non_retryable_exceptions:
                raise

            except self._config.retryable_exceptions as e:
                last_exception = e

                if attempt == self._config.max_attempts:
                    self._logger.error(
                        f"All {self._config.max_attempts} attempts failed for {func.__name__}"
                    )
                    raise

                delay = self._config.get_delay(attempt)
                self._logger.warning(
                    f"Attempt {attempt}/{self._config.max_attempts} failed: {e}. "
                    f"Retrying in {delay:.2f}s"
                )

                if self._on_retry:
                    self._on_retry(attempt, e, delay)

                time.sleep(delay)

        raise last_exception

    async def execute_async(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute async function with retry."""
        last_exception = None

        for attempt in range(1, self._config.max_attempts + 1):
            try:
                return await func(*args, **kwargs)

            except self._config.non_retryable_exceptions:
                raise

            except self._config.retryable_exceptions as e:
                last_exception = e

                if attempt == self._config.max_attempts:
                    raise

                delay = self._config.get_delay(attempt)
                self._logger.warning(
                    f"Async attempt {attempt} failed: {e}. Retrying in {delay:.2f}s"
                )

                if self._on_retry:
                    self._on_retry(attempt, e, delay)

                await asyncio.sleep(delay)

        raise last_exception


# ============================================================================
# Decorator Functions
# ============================================================================


def retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None,
):
    """
    Decorator for retry with exponential backoff.

    Usage:
        @retry(max_attempts=3, backoff=2.0)
        def flaky_api_call():
            ...
    """
    policy = RetryPolicy(
        max_attempts=max_attempts,
        initial_delay=initial_delay,
        backoff=backoff,
        retryable=exceptions,
        on_retry=on_retry,
    )

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return policy.execute(func, *args, **kwargs)

        return wrapper

    return decorator


def retry_async(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None,
):
    """
    Decorator for async retry with exponential backoff.

    Usage:
        @retry_async(max_attempts=3)
        async def flaky_api_call():
            ...
    """
    policy = RetryPolicy(
        max_attempts=max_attempts,
        initial_delay=initial_delay,
        backoff=backoff,
        retryable=exceptions,
        on_retry=on_retry,
    )

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await policy.execute_async(func, *args, **kwargs)

        return wrapper

    return decorator


# ============================================================================
# Retry with Circuit Breaker
# ============================================================================


def retry_with_breaker(breaker_name: str, max_attempts: int = 3, backoff: float = 2.0):
    """
    Combine retry with circuit breaker.

    Usage:
        @retry_with_breaker("api_service", max_attempts=3)
        def call_api():
            ...
    """
    from .circuit_breaker import CircuitOpenError, get_circuit_breaker

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        breaker = get_circuit_breaker(breaker_name)
        policy = RetryPolicy(
            max_attempts=max_attempts, backoff=backoff, non_retryable=(CircuitOpenError,)
        )

        @wraps(func)
        def wrapper(*args, **kwargs):
            return policy.execute(lambda: breaker.call(func, *args, **kwargs))

        return wrapper

    return decorator


# ============================================================================
# Factory Function
# ============================================================================


def create_retry_policy(
    max_attempts: int = 3, initial_delay: float = 1.0, backoff: float = 2.0
) -> RetryPolicy:
    """Create a retry policy instance."""
    return RetryPolicy(max_attempts=max_attempts, initial_delay=initial_delay, backoff=backoff)
