"""
Circuit Breaker Module - Phase 16

Implements the circuit breaker pattern for external service calls.

The circuit breaker prevents cascading failures by:
- Tracking failure rates
- Opening circuit when failures exceed threshold
- Allowing periodic recovery attempts
- Closing circuit when service recovers

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Circuit tripped, requests fail fast
- HALF_OPEN: Testing if service recovered

Usage:
    breaker = CircuitBreaker(
        failure_threshold=5,
        recovery_timeout=30.0
    )

    @breaker.protect
    def external_api_call():
        ...
"""

from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import functools
import threading
import time

from ...utils import get_logger, utc_now

logger = get_logger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit tripped, failing fast
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    # Failure thresholds
    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 3  # Successes to close from half-open

    # Timing
    recovery_timeout: float = 30.0  # Seconds before trying again
    window_size: float = 60.0  # Sliding window for failure counting

    # Behavior
    half_open_max_calls: int = 1  # Max calls in half-open state

    # Logging
    log_state_changes: bool = True


class CircuitBreakerError(Exception):
    """Raised when circuit is open."""

    def __init__(self, breaker_name: str, state: CircuitState):
        self.breaker_name = breaker_name
        self.state = state
        super().__init__(
            f"Circuit breaker '{breaker_name}' is {state.value}. "
            f"Service temporarily unavailable."
        )


class CircuitBreaker:
    """
    Circuit breaker implementation.

    Usage:
        breaker = CircuitBreaker(name="tavily_api")

        @breaker.protect
        def call_tavily():
            ...

        # Or manually
        if breaker.allow_request():
            try:
                result = call_tavily()
                breaker.record_success()
            except Exception as e:
                breaker.record_failure(e)
    """

    def __init__(
        self,
        name: str = "default",
        config: Optional[CircuitBreakerConfig] = None,
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()

        self._state = CircuitState.CLOSED
        self._failures: list = []  # List of failure timestamps
        self._successes_in_half_open: int = 0
        self._last_failure_time: Optional[datetime] = None
        self._opened_at: Optional[datetime] = None
        self._half_open_calls: int = 0

        self._lock = threading.RLock()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        with self._lock:
            self._check_state_transition()
            return self._state

    def _check_state_transition(self) -> None:
        """Check if state should transition."""
        now = utc_now()

        if self._state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self._opened_at:
                elapsed = (now - self._opened_at).total_seconds()
                if elapsed >= self.config.recovery_timeout:
                    self._transition_to(CircuitState.HALF_OPEN)

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        old_state = self._state
        self._state = new_state

        if new_state == CircuitState.HALF_OPEN:
            self._successes_in_half_open = 0
            self._half_open_calls = 0

        if self.config.log_state_changes:
            logger.info(
                f"[CIRCUIT] {self.name}: {old_state.value} -> {new_state.value}"
            )

    def allow_request(self) -> bool:
        """
        Check if a request should be allowed.

        Returns:
            True if request should proceed, False otherwise
        """
        with self._lock:
            self._check_state_transition()

            if self._state == CircuitState.CLOSED:
                return True

            elif self._state == CircuitState.OPEN:
                return False

            elif self._state == CircuitState.HALF_OPEN:
                # Allow limited calls in half-open
                if self._half_open_calls < self.config.half_open_max_calls:
                    self._half_open_calls += 1
                    return True
                return False

            return False

    def record_success(self) -> None:
        """Record a successful call."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._successes_in_half_open += 1

                if self._successes_in_half_open >= self.config.success_threshold:
                    self._transition_to(CircuitState.CLOSED)
                    self._failures.clear()

    def record_failure(self, error: Optional[Exception] = None) -> None:
        """Record a failed call."""
        with self._lock:
            now = utc_now()
            self._failures.append(now)
            self._last_failure_time = now

            # Remove old failures outside window
            cutoff = now - timedelta(seconds=self.config.window_size)
            self._failures = [f for f in self._failures if f > cutoff]

            if self._state == CircuitState.HALF_OPEN:
                # Any failure in half-open reopens circuit
                self._opened_at = now
                self._transition_to(CircuitState.OPEN)

            elif self._state == CircuitState.CLOSED:
                # Check if we should open
                if len(self._failures) >= self.config.failure_threshold:
                    self._opened_at = now
                    self._transition_to(CircuitState.OPEN)

            if error and self.config.log_state_changes:
                logger.warning(
                    f"[CIRCUIT] {self.name}: Recorded failure - {error}"
                )

    def protect(self, func: Callable) -> Callable:
        """
        Decorator to protect a function with circuit breaker.

        Args:
            func: Function to protect

        Returns:
            Protected function
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not self.allow_request():
                raise CircuitBreakerError(self.name, self._state)

            try:
                result = func(*args, **kwargs)
                self.record_success()
                return result

            except Exception as e:
                self.record_failure(e)
                raise

        return wrapper

    def reset(self) -> None:
        """Manually reset the circuit breaker."""
        with self._lock:
            self._failures.clear()
            self._successes_in_half_open = 0
            self._half_open_calls = 0
            self._opened_at = None
            self._transition_to(CircuitState.CLOSED)

    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status."""
        with self._lock:
            self._check_state_transition()

            return {
                "name": self.name,
                "state": self._state.value,
                "failure_count": len(self._failures),
                "failure_threshold": self.config.failure_threshold,
                "last_failure": self._last_failure_time.isoformat() if self._last_failure_time else None,
                "opened_at": self._opened_at.isoformat() if self._opened_at else None,
                "recovery_timeout": self.config.recovery_timeout,
            }


# ============================================================================
# Circuit Breaker Registry
# ============================================================================

class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers.

    Usage:
        registry = CircuitBreakerRegistry()
        tavily_breaker = registry.get_or_create("tavily")
        serper_breaker = registry.get_or_create("serper")

        # Get status of all breakers
        status = registry.get_all_status()
    """

    def __init__(self, default_config: Optional[CircuitBreakerConfig] = None):
        self.default_config = default_config or CircuitBreakerConfig()
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.RLock()

    def get_or_create(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
    ) -> CircuitBreaker:
        """Get existing breaker or create new one."""
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(
                    name=name,
                    config=config or self.default_config,
                )
            return self._breakers[name]

    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get a breaker by name."""
        return self._breakers.get(name)

    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all breakers."""
        with self._lock:
            return {
                name: breaker.get_status()
                for name, breaker in self._breakers.items()
            }

    def reset_all(self) -> None:
        """Reset all circuit breakers."""
        with self._lock:
            for breaker in self._breakers.values():
                breaker.reset()


# Global registry
circuit_registry = CircuitBreakerRegistry()


def get_circuit_breaker(name: str) -> CircuitBreaker:
    """Get or create a circuit breaker from global registry."""
    return circuit_registry.get_or_create(name)


# ============================================================================
# Node Protection
# ============================================================================

def protected_node(
    breaker_name: str,
    fallback_value: Optional[Dict[str, Any]] = None,
) -> Callable:
    """
    Decorator to protect a node with circuit breaker.

    Args:
        breaker_name: Name of circuit breaker to use
        fallback_value: Value to return when circuit is open

    Returns:
        Decorator function

    Usage:
        @protected_node("tavily", fallback_value={"search_results": []})
        def tavily_search_node(state):
            ...
    """
    def decorator(func: Callable) -> Callable:
        breaker = get_circuit_breaker(breaker_name)

        @functools.wraps(func)
        def wrapper(state):
            if not breaker.allow_request():
                logger.warning(
                    f"[CIRCUIT] {breaker_name} is open, using fallback"
                )
                if fallback_value is not None:
                    return {
                        **fallback_value,
                        "_circuit_breaker_triggered": True,
                        "_circuit_breaker": breaker_name,
                    }
                raise CircuitBreakerError(breaker_name, breaker.state)

            try:
                result = func(state)
                breaker.record_success()
                return result

            except Exception as e:
                breaker.record_failure(e)
                raise

        return wrapper

    return decorator
