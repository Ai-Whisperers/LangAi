"""
Circuit Breaker (Phase 20.1).

Prevent cascading failures:
- Automatic failure detection
- Fast fail when circuit is open
- Gradual recovery with half-open state
"""

import logging
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar

from ..utils import utc_now

# ============================================================================
# Types and Enums
# ============================================================================

T = TypeVar("T")


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitOpenError(Exception):
    """Raised when circuit is open."""

    def __init__(self, breaker_name: str, retry_after: float):
        self.breaker_name = breaker_name
        self.retry_after = retry_after
        super().__init__(f"Circuit '{breaker_name}' is open. Retry after {retry_after:.1f}s")


# ============================================================================
# Circuit Breaker
# ============================================================================


@dataclass
class CircuitStats:
    """Circuit breaker statistics."""

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    state_changes: int = 0

    @property
    def failure_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.failed_calls / self.total_calls

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "rejected_calls": self.rejected_calls,
            "failure_rate": round(self.failure_rate, 2),
            "state_changes": self.state_changes,
        }


class CircuitBreaker:
    """
    Circuit breaker for external service calls.

    States:
    - CLOSED: Normal operation, failures are tracked
    - OPEN: Failing fast, requests rejected immediately
    - HALF_OPEN: Testing if service has recovered

    Usage:
        breaker = CircuitBreaker("external_api")

        @breaker
        def call_api():
            return requests.get("https://api.example.com")

        # Or use as context manager
        with breaker:
            result = call_api()

        # Or call manually
        result = breaker.call(call_api)
    """

    def __init__(
        self,
        name: str = "default",
        failure_threshold: int = 5,
        success_threshold: int = 3,
        timeout_seconds: float = 30.0,
        half_open_timeout: float = 10.0,
        excluded_exceptions: Optional[tuple] = None,
    ):
        """
        Initialize circuit breaker.

        Args:
            name: Breaker identifier
            failure_threshold: Failures before opening
            success_threshold: Successes in half-open to close
            timeout_seconds: Time before trying half-open
            half_open_timeout: Time to wait in half-open
            excluded_exceptions: Exceptions that don't count as failures
        """
        self.name = name
        self._failure_threshold = failure_threshold
        self._success_threshold = success_threshold
        self._timeout = timeout_seconds
        self._half_open_timeout = half_open_timeout
        self._excluded_exceptions = excluded_exceptions or ()

        # State
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._opened_at: Optional[datetime] = None

        # Stats
        self._stats = CircuitStats()

        # Thread safety
        self._lock = threading.RLock()

        # Logger
        self._logger = logging.getLogger(f"circuit_breaker.{name}")

        # Callbacks
        self._on_state_change: list = []

    @property
    def state(self) -> CircuitState:
        """Get current state, checking for automatic transitions."""
        with self._lock:
            if self._state == CircuitState.OPEN:
                # Check if timeout has passed
                if self._should_try_reset():
                    self._transition_to(CircuitState.HALF_OPEN)
            return self._state

    @property
    def stats(self) -> CircuitStats:
        """Get circuit statistics."""
        return self._stats

    def _should_try_reset(self) -> bool:
        """Check if enough time has passed to try reset."""
        if not self._opened_at:
            return True
        return utc_now() - self._opened_at >= timedelta(seconds=self._timeout)

    # ==========================================================================
    # Decorator Interface
    # ==========================================================================

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Use as decorator."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)

        return wrapper

    # ==========================================================================
    # Context Manager Interface
    # ==========================================================================

    def __enter__(self):
        """Enter context - check if circuit allows operation."""
        with self._lock:
            state = self.state

            if state == CircuitState.OPEN:
                self._stats.rejected_calls += 1
                retry_after = self._timeout - (utc_now() - self._opened_at).total_seconds()
                raise CircuitOpenError(self.name, max(0, retry_after))

            self._stats.total_calls += 1
            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - record result."""
        if exc_type is None:
            self._record_success()
        elif not isinstance(exc_val, self._excluded_exceptions):
            self._record_failure()
        return False

    # ==========================================================================
    # Manual Call Interface
    # ==========================================================================

    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Call a function through the circuit breaker.

        Args:
            func: Function to call
            *args, **kwargs: Arguments to pass

        Returns:
            Function result

        Raises:
            CircuitOpenError: If circuit is open
        """
        with self:
            return func(*args, **kwargs)

    async def call_async(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Async version of call."""
        with self._lock:
            state = self.state

            if state == CircuitState.OPEN:
                self._stats.rejected_calls += 1
                retry_after = self._timeout - (utc_now() - self._opened_at).total_seconds()
                raise CircuitOpenError(self.name, max(0, retry_after))

            self._stats.total_calls += 1

        try:
            result = await func(*args, **kwargs)
            self._record_success()
            return result
        except self._excluded_exceptions:
            raise
        except Exception:
            self._record_failure()
            raise

    # ==========================================================================
    # State Management
    # ==========================================================================

    def _record_success(self):
        """Record a successful call."""
        with self._lock:
            self._stats.successful_calls += 1
            self._stats.last_success_time = utc_now()

            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self._success_threshold:
                    self._transition_to(CircuitState.CLOSED)
            else:
                self._failure_count = max(0, self._failure_count - 1)

    def _record_failure(self):
        """Record a failed call."""
        with self._lock:
            self._stats.failed_calls += 1
            self._stats.last_failure_time = utc_now()
            self._failure_count += 1
            self._last_failure_time = utc_now()

            if self._state == CircuitState.HALF_OPEN:
                # Immediate transition back to open
                self._transition_to(CircuitState.OPEN)
            elif self._state == CircuitState.CLOSED:
                if self._failure_count >= self._failure_threshold:
                    self._transition_to(CircuitState.OPEN)

    def _transition_to(self, new_state: CircuitState):
        """Transition to a new state."""
        old_state = self._state
        self._state = new_state
        self._stats.state_changes += 1

        if new_state == CircuitState.OPEN:
            self._opened_at = utc_now()
            self._logger.warning(
                f"Circuit '{self.name}' OPENED after {self._failure_count} failures"
            )
        elif new_state == CircuitState.HALF_OPEN:
            self._success_count = 0
            self._logger.info(f"Circuit '{self.name}' entering HALF_OPEN state")
        elif new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
            self._logger.info(f"Circuit '{self.name}' CLOSED - recovered")

        # Notify callbacks
        for callback in self._on_state_change:
            try:
                callback(self.name, old_state, new_state)
            except Exception as e:
                self._logger.warning(f"Circuit state change callback error: {e}")

    def reset(self):
        """Manually reset the circuit to closed state."""
        with self._lock:
            self._transition_to(CircuitState.CLOSED)

    def force_open(self):
        """Manually force the circuit open."""
        with self._lock:
            self._transition_to(CircuitState.OPEN)

    # ==========================================================================
    # Callbacks
    # ==========================================================================

    def on_state_change(self, callback: Callable):
        """Register callback for state changes."""
        self._on_state_change.append(callback)

    # ==========================================================================
    # Export
    # ==========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Export circuit state as dict."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "stats": self._stats.to_dict(),
        }


# ============================================================================
# Factory Function
# ============================================================================


def create_circuit_breaker(
    name: str = "default", failure_threshold: int = 5, timeout_seconds: float = 30.0
) -> CircuitBreaker:
    """Create a circuit breaker instance."""
    return CircuitBreaker(
        name=name, failure_threshold=failure_threshold, timeout_seconds=timeout_seconds
    )


# ============================================================================
# Global Registry
# ============================================================================

_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str) -> CircuitBreaker:
    """Get or create a circuit breaker by name."""
    if name not in _breakers:
        _breakers[name] = CircuitBreaker(name=name)
    return _breakers[name]
