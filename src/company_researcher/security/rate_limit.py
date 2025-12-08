"""
Rate Limiting - Request throttling and abuse prevention.

Provides:
- Token bucket algorithm
- Sliding window rate limiting
- Per-user and per-IP limits
- Configurable windows and limits
"""

import functools
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: float = 0,
        limit: int = 0,
        remaining: int = 0
    ):
        super().__init__(message)
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_size: int = 10  # Max burst requests
    window_seconds: int = 60  # Sliding window size
    block_duration_seconds: int = 300  # Block duration after exceeding


@dataclass
class RateLimitState:
    """State for a rate-limited entity."""
    key: str
    requests: List[float] = field(default_factory=list)
    tokens: float = 0
    last_refill: float = field(default_factory=time.time)
    blocked_until: Optional[float] = None
    last_activity: float = field(default_factory=time.time)  # For TTL cleanup


class RateLimiter:
    """
    Rate limiter using token bucket and sliding window algorithms.

    Usage:
        limiter = RateLimiter(requests_per_minute=60)

        # Check rate limit
        try:
            limiter.check("user123")
            # proceed with request
        except RateLimitExceeded as e:
            # handle rate limit
            print(f"Retry after {e.retry_after} seconds")

        # Use as decorator
        @limiter.limit("api")
        def api_endpoint(user_id):
            ...

        # Get limit info
        info = limiter.get_limit_info("user123")
    """

    def __init__(
        self,
        config: RateLimitConfig = None,
        requests_per_minute: int = None,
        requests_per_hour: int = None,
        burst_size: int = None,
        state_ttl_seconds: int = 3600,  # 1 hour default TTL
        cleanup_interval_seconds: int = 300  # 5 minutes
    ):
        self.config = config or RateLimitConfig()

        if requests_per_minute:
            self.config.requests_per_minute = requests_per_minute
        if requests_per_hour:
            self.config.requests_per_hour = requests_per_hour
        if burst_size:
            self.config.burst_size = burst_size

        self._states: Dict[str, RateLimitState] = {}
        self._lock = threading.RLock()

        # Calculate refill rate (tokens per second)
        self._refill_rate = self.config.requests_per_minute / 60.0

        # TTL-based cleanup settings
        self._state_ttl = state_ttl_seconds
        self._cleanup_interval = cleanup_interval_seconds
        self._last_cleanup = time.time()

    def check(self, key: str, cost: int = 1) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed.

        Args:
            key: Identifier (user ID, IP address, etc.)
            cost: Cost of this request in tokens

        Returns:
            Tuple of (allowed, info_dict)

        Raises:
            RateLimitExceeded if rate limit exceeded
        """
        # Trigger cleanup if needed
        self._maybe_cleanup_stale_states()

        with self._lock:
            state = self._get_or_create_state(key)
            now = time.time()

            # Update last activity
            state.last_activity = now

            # Check if blocked
            if state.blocked_until and now < state.blocked_until:
                retry_after = state.blocked_until - now
                # Security: Don't expose the key in error message
                raise RateLimitExceeded(
                    "Rate limit exceeded. Please try again later.",
                    retry_after=retry_after,
                    limit=self.config.requests_per_minute,
                    remaining=0
                )

            # Refill tokens (token bucket)
            self._refill_tokens(state, now)

            # Check sliding window
            self._cleanup_old_requests(state, now)

            # Check limits
            if not self._check_limits(state, cost):
                # Block the key
                state.blocked_until = now + self.config.block_duration_seconds
                retry_after = self.config.block_duration_seconds
                # Security: Don't expose the key in error message
                raise RateLimitExceeded(
                    "Rate limit exceeded. Please try again later.",
                    retry_after=retry_after,
                    limit=self.config.requests_per_minute,
                    remaining=0
                )

            # Consume tokens
            state.tokens -= cost
            state.requests.append(now)

            return True, self._get_limit_info_dict(state)

    def _get_or_create_state(self, key: str) -> RateLimitState:
        """Get or create state for a key."""
        if key not in self._states:
            self._states[key] = RateLimitState(
                key=key,
                tokens=float(self.config.burst_size),
                last_refill=time.time()
            )
        return self._states[key]

    def _refill_tokens(self, state: RateLimitState, now: float) -> None:
        """Refill tokens based on time elapsed."""
        elapsed = now - state.last_refill
        tokens_to_add = elapsed * self._refill_rate
        state.tokens = min(
            state.tokens + tokens_to_add,
            float(self.config.burst_size)
        )
        state.last_refill = now

    def _cleanup_old_requests(self, state: RateLimitState, now: float) -> None:
        """Remove requests older than window."""
        window_start = now - self.config.window_seconds
        state.requests = [r for r in state.requests if r > window_start]

    def _check_limits(self, state: RateLimitState, cost: int) -> bool:
        """Check if request is within limits."""
        now = time.time()

        # Token bucket check (burst protection)
        if state.tokens < cost:
            return False

        # Sliding window checks
        window_count = len(state.requests)

        # Per-minute limit
        if window_count >= self.config.requests_per_minute:
            return False

        # Per-hour limit (approximate)
        hour_requests = len([r for r in state.requests if r > now - 3600])
        if hour_requests >= self.config.requests_per_hour:
            return False

        return True

    def _get_limit_info_dict(self, state: RateLimitState) -> Dict[str, Any]:
        """Get current limit info as dictionary."""
        return {
            "limit": self.config.requests_per_minute,
            "remaining": max(0, int(state.tokens)),
            "reset_at": datetime.now(timezone.utc) + timedelta(seconds=60),
            "window_requests": len(state.requests)
        }

    def get_limit_info(self, key: str) -> Dict[str, Any]:
        """
        Get rate limit info for a key.

        Args:
            key: Identifier

        Returns:
            Dictionary with limit info
        """
        with self._lock:
            state = self._get_or_create_state(key)
            self._refill_tokens(state, time.time())
            self._cleanup_old_requests(state, time.time())
            return self._get_limit_info_dict(state)

    def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        with self._lock:
            if key in self._states:
                del self._states[key]

    def unblock(self, key: str) -> None:
        """Unblock a rate-limited key."""
        with self._lock:
            if key in self._states:
                self._states[key].blocked_until = None

    def is_blocked(self, key: str) -> bool:
        """Check if a key is currently blocked."""
        with self._lock:
            state = self._states.get(key)
            if state and state.blocked_until:
                return time.time() < state.blocked_until
            return False

    def _maybe_cleanup_stale_states(self) -> None:
        """
        Clean up stale rate limit states if cleanup interval has passed.

        This prevents unbounded memory growth from inactive keys.
        """
        now = time.time()

        # Only cleanup periodically
        if now - self._last_cleanup < self._cleanup_interval:
            return

        with self._lock:
            # Double-check inside lock
            if now - self._last_cleanup < self._cleanup_interval:
                return

            # Find stale states (no activity within TTL)
            stale_keys = [
                key for key, state in self._states.items()
                if now - state.last_activity > self._state_ttl
                and (state.blocked_until is None or state.blocked_until < now)
            ]

            for key in stale_keys:
                del self._states[key]

            if stale_keys:
                logger.debug(f"Cleaned up {len(stale_keys)} stale rate limit states")

            self._last_cleanup = now

    def get_state_count(self) -> int:
        """Get count of currently tracked rate limit states."""
        with self._lock:
            return len(self._states)

    def force_cleanup(self) -> int:
        """
        Force cleanup of stale rate limit states.

        Returns:
            Number of states cleaned up
        """
        now = time.time()
        cleaned = 0

        with self._lock:
            stale_keys = [
                key for key, state in self._states.items()
                if now - state.last_activity > self._state_ttl
                and (state.blocked_until is None or state.blocked_until < now)
            ]

            for key in stale_keys:
                del self._states[key]
                cleaned += 1

            self._last_cleanup = now

        return cleaned

    def limit(
        self,
        key_func: Callable[..., str] = None,
        cost: int = 1
    ) -> Callable:
        """
        Decorator to apply rate limiting.

        Args:
            key_func: Function to extract key from arguments
            cost: Cost per request

        Usage:
            @limiter.limit(lambda user_id: f"user:{user_id}")
            def api_call(user_id):
                ...

            # Or with default key extraction
            @limiter.limit()
            def api_call(user_id):  # Uses first arg as key
                ...
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Extract key
                if key_func:
                    key = key_func(*args, **kwargs)
                elif args:
                    key = str(args[0])
                elif 'user_id' in kwargs:
                    key = str(kwargs['user_id'])
                else:
                    key = func.__name__

                # Check rate limit
                self.check(key, cost)

                return func(*args, **kwargs)

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                if key_func:
                    key = key_func(*args, **kwargs)
                elif args:
                    key = str(args[0])
                elif 'user_id' in kwargs:
                    key = str(kwargs['user_id'])
                else:
                    key = func.__name__

                self.check(key, cost)
                return await func(*args, **kwargs)

            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return wrapper
        return decorator


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter for more precise limiting.

    Uses a sliding log algorithm for accuracy.
    """

    def __init__(
        self,
        limit: int,
        window_seconds: int = 60,
        state_ttl_seconds: int = 3600,
        cleanup_interval_seconds: int = 300
    ):
        self.limit = limit
        self.window_seconds = window_seconds
        self._logs: Dict[str, List[float]] = {}
        self._last_activity: Dict[str, float] = {}
        self._lock = threading.RLock()

        # TTL cleanup settings
        self._state_ttl = state_ttl_seconds
        self._cleanup_interval = cleanup_interval_seconds
        self._last_cleanup = time.time()

    def check(self, key: str) -> bool:
        """Check if request is allowed."""
        self._maybe_cleanup()

        with self._lock:
            now = time.time()
            window_start = now - self.window_seconds

            # Get or create log
            if key not in self._logs:
                self._logs[key] = []

            # Update last activity
            self._last_activity[key] = now

            # Clean old entries
            self._logs[key] = [t for t in self._logs[key] if t > window_start]

            # Check limit
            if len(self._logs[key]) >= self.limit:
                return False

            # Record request
            self._logs[key].append(now)
            return True

    def get_remaining(self, key: str) -> int:
        """Get remaining requests for key."""
        with self._lock:
            now = time.time()
            window_start = now - self.window_seconds

            if key not in self._logs:
                return self.limit

            recent = len([t for t in self._logs[key] if t > window_start])
            return max(0, self.limit - recent)

    def _maybe_cleanup(self) -> None:
        """Clean up stale entries if cleanup interval has passed."""
        now = time.time()

        if now - self._last_cleanup < self._cleanup_interval:
            return

        with self._lock:
            if now - self._last_cleanup < self._cleanup_interval:
                return

            stale_keys = [
                key for key, last in self._last_activity.items()
                if now - last > self._state_ttl
            ]

            for key in stale_keys:
                self._logs.pop(key, None)
                self._last_activity.pop(key, None)

            if stale_keys:
                logger.debug(f"SlidingWindowRateLimiter cleaned up {len(stale_keys)} stale entries")

            self._last_cleanup = now


class FixedWindowRateLimiter:
    """
    Fixed window rate limiter.

    Simpler but less precise than sliding window.
    """

    def __init__(
        self,
        limit: int,
        window_seconds: int = 60,
        state_ttl_windows: int = 60,  # Number of windows to keep state
        cleanup_interval_seconds: int = 300
    ):
        self.limit = limit
        self.window_seconds = window_seconds
        self._windows: Dict[str, Tuple[int, int]] = {}  # key -> (window_id, count)
        self._lock = threading.RLock()

        # TTL cleanup settings
        self._state_ttl_windows = state_ttl_windows
        self._cleanup_interval = cleanup_interval_seconds
        self._last_cleanup = time.time()

    def _get_window_id(self) -> int:
        """Get current window ID."""
        return int(time.time() / self.window_seconds)

    def check(self, key: str) -> bool:
        """Check if request is allowed."""
        self._maybe_cleanup()

        with self._lock:
            window_id = self._get_window_id()

            if key not in self._windows:
                self._windows[key] = (window_id, 0)

            current_window, count = self._windows[key]

            # New window
            if current_window != window_id:
                self._windows[key] = (window_id, 1)
                return True

            # Check limit
            if count >= self.limit:
                return False

            # Increment
            self._windows[key] = (window_id, count + 1)
            return True

    def _maybe_cleanup(self) -> None:
        """Clean up stale entries if cleanup interval has passed."""
        now = time.time()

        if now - self._last_cleanup < self._cleanup_interval:
            return

        with self._lock:
            if now - self._last_cleanup < self._cleanup_interval:
                return

            current_window_id = self._get_window_id()
            stale_threshold = current_window_id - self._state_ttl_windows

            stale_keys = [
                key for key, (window_id, _) in self._windows.items()
                if window_id < stale_threshold
            ]

            for key in stale_keys:
                del self._windows[key]

            if stale_keys:
                logger.debug(f"FixedWindowRateLimiter cleaned up {len(stale_keys)} stale entries")

            self._last_cleanup = now


# Convenience functions


def create_rate_limiter(
    requests_per_minute: int = 60,
    burst_size: int = 10
) -> RateLimiter:
    """Create a rate limiter."""
    return RateLimiter(
        requests_per_minute=requests_per_minute,
        burst_size=burst_size
    )
