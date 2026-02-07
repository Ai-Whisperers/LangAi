"""
Retry Module - Phase 16

Provides automatic retry capabilities for workflow nodes.

Features:
- Configurable retry attempts
- Exponential backoff
- Jitter to prevent thundering herd
- Specific exception handling

Usage:
    @with_retry(max_attempts=3, backoff_base=2.0)
    def search_node(state):
        # May fail, will be retried
        ...

    # With specific exceptions
    @with_retry(
        max_attempts=3,
        retry_exceptions=(ConnectionError, TimeoutError)
    )
    def api_call_node(state):
        ...
"""

import asyncio
import functools
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional, Tuple, Type

from ...state.workflow import OverallState
from ...utils import get_logger

logger = get_logger(__name__)


class RetryStrategy(str, Enum):
    """Retry backoff strategies."""

    CONSTANT = "constant"  # Same delay each time
    LINEAR = "linear"  # Delay increases linearly
    EXPONENTIAL = "exponential"  # Delay doubles each time
    EXPONENTIAL_JITTER = "exponential_jitter"  # Exponential with random jitter


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    # Retry limits
    max_attempts: int = 3

    # Backoff settings
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_JITTER
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    backoff_multiplier: float = 2.0

    # Jitter
    jitter_factor: float = 0.1  # 10% jitter

    # Exception handling
    retry_exceptions: Tuple[Type[Exception], ...] = (Exception,)
    fatal_exceptions: Tuple[Type[Exception], ...] = (KeyboardInterrupt, SystemExit)

    # Logging
    log_retries: bool = True


def calculate_delay(
    attempt: int,
    config: RetryConfig,
) -> float:
    """
    Calculate delay before next retry attempt.

    Args:
        attempt: Current attempt number (1-indexed)
        config: Retry configuration

    Returns:
        Delay in seconds
    """
    if config.strategy == RetryStrategy.CONSTANT:
        delay = config.initial_delay

    elif config.strategy == RetryStrategy.LINEAR:
        delay = config.initial_delay * attempt

    elif config.strategy == RetryStrategy.EXPONENTIAL:
        delay = config.initial_delay * (config.backoff_multiplier ** (attempt - 1))

    elif config.strategy == RetryStrategy.EXPONENTIAL_JITTER:
        base_delay = config.initial_delay * (config.backoff_multiplier ** (attempt - 1))
        jitter = base_delay * config.jitter_factor * random.random()
        delay = base_delay + jitter

    else:
        delay = config.initial_delay

    return min(delay, config.max_delay)


def with_retry(
    max_attempts: int = 3,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_JITTER,
    initial_delay: float = 1.0,
    retry_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    config: Optional[RetryConfig] = None,
) -> Callable:
    """
    Decorator to add retry logic to a node function.

    Args:
        max_attempts: Maximum number of attempts
        strategy: Backoff strategy
        initial_delay: Initial delay between retries
        retry_exceptions: Exceptions that trigger retry
        config: Full configuration (overrides other args)

    Returns:
        Decorated function with retry logic

    Usage:
        @with_retry(max_attempts=3)
        def my_node(state: OverallState) -> Dict[str, Any]:
            ...
    """
    if config is None:
        config = RetryConfig(
            max_attempts=max_attempts,
            strategy=strategy,
            initial_delay=initial_delay,
            retry_exceptions=retry_exceptions,
        )

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(state: OverallState) -> Dict[str, Any]:
            last_exception = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(state)

                except config.fatal_exceptions:
                    raise

                except config.retry_exceptions as e:
                    last_exception = e

                    if attempt < config.max_attempts:
                        delay = calculate_delay(attempt, config)

                        if config.log_retries:
                            logger.warning(
                                f"[RETRY] {func.__name__} failed (attempt {attempt}/{config.max_attempts}): {e}. "
                                f"Retrying in {delay:.1f}s..."
                            )

                        time.sleep(delay)
                    else:
                        if config.log_retries:
                            logger.error(
                                f"[RETRY] {func.__name__} failed after {config.max_attempts} attempts: {e}"
                            )

            # All retries exhausted
            if last_exception:
                raise last_exception

            return {}

        @functools.wraps(func)
        async def async_wrapper(state: OverallState) -> Dict[str, Any]:
            last_exception = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(state)
                    else:
                        return func(state)

                except config.fatal_exceptions:
                    raise

                except config.retry_exceptions as e:
                    last_exception = e

                    if attempt < config.max_attempts:
                        delay = calculate_delay(attempt, config)

                        if config.log_retries:
                            logger.warning(
                                f"[RETRY] {func.__name__} failed (attempt {attempt}/{config.max_attempts}): {e}. "
                                f"Retrying in {delay:.1f}s..."
                            )

                        await asyncio.sleep(delay)
                    else:
                        if config.log_retries:
                            logger.error(
                                f"[RETRY] {func.__name__} failed after {config.max_attempts} attempts: {e}"
                            )

            if last_exception:
                raise last_exception

            return {}

        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def retry_node(
    node_func: Callable,
    config: Optional[RetryConfig] = None,
) -> Callable:
    """
    Wrap a node function with retry logic.

    Alternative to decorator when you can't modify the function.

    Args:
        node_func: Node function to wrap
        config: Retry configuration

    Returns:
        Wrapped function with retry logic
    """
    if config is None:
        config = RetryConfig()

    @functools.wraps(node_func)
    def wrapper(state: OverallState) -> Dict[str, Any]:
        last_exception = None

        for attempt in range(1, config.max_attempts + 1):
            try:
                return node_func(state)

            except config.fatal_exceptions:
                raise

            except config.retry_exceptions as e:
                last_exception = e

                if attempt < config.max_attempts:
                    delay = calculate_delay(attempt, config)
                    logger.warning(
                        f"[RETRY] {node_func.__name__} failed (attempt {attempt}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(f"[RETRY] {node_func.__name__} exhausted retries: {e}")

        if last_exception:
            raise last_exception

        return {}

    return wrapper


# ============================================================================
# Retry Context Manager
# ============================================================================


class RetryContext:
    """
    Context manager for retry logic.

    Usage:
        with RetryContext(max_attempts=3) as retry:
            for attempt in retry:
                try:
                    result = risky_operation()
                    break
                except Exception as e:
                    retry.record_failure(e)
    """

    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.attempt = 0
        self.last_exception = None
        self.succeeded = False

    def __enter__(self) -> "RetryContext":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and not self.succeeded:
            logger.error(f"[RETRY] All attempts failed: {exc_val}")
        return False

    def __iter__(self):
        for self.attempt in range(1, self.config.max_attempts + 1):
            yield self.attempt

            if self.succeeded:
                break

            if self.attempt < self.config.max_attempts and self.last_exception:
                delay = calculate_delay(self.attempt, self.config)
                time.sleep(delay)

    def record_failure(self, exception: Exception) -> None:
        """Record a failed attempt."""
        self.last_exception = exception
        logger.warning(
            f"[RETRY] Attempt {self.attempt}/{self.config.max_attempts} failed: {exception}"
        )

    def record_success(self) -> None:
        """Record a successful attempt."""
        self.succeeded = True
