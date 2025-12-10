"""
Base API Client with common functionality.

Provides:
- Async HTTP requests with aiohttp
- TTL caching
- Rate limiting
- Circuit breaker pattern
- Error handling
"""

import asyncio
import logging
import os
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional

import aiohttp
from cachetools import TTLCache

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base exception for API errors."""
    pass


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""
    pass


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreaker:
    """
    Circuit breaker for API fault tolerance.

    Prevents cascading failures by temporarily blocking requests
    to a failing service.
    """
    failure_threshold: int = 5
    recovery_timeout: int = 60
    success_threshold: int = 3

    state: CircuitState = field(default=CircuitState.CLOSED)
    failure_count: int = field(default=0)
    success_count: int = field(default=0)
    last_failure_time: Optional[datetime] = field(default=None)

    def record_success(self) -> None:
        """Record successful request."""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0
                logger.info("Circuit breaker closed - service recovered")

    def record_failure(self) -> None:
        """Record failed request."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

    def can_execute(self) -> bool:
        """Check if requests should be allowed."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if self.last_failure_time and \
               datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout):
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.info("Circuit breaker half-open - testing recovery")
                return True
            return False

        return True  # HALF_OPEN allows requests


class RateLimiter:
    """
    Simple rate limiter using token bucket algorithm.
    """

    def __init__(self, calls: int, period: float):
        """
        Initialize rate limiter.

        Args:
            calls: Maximum calls allowed in period
            period: Time period in seconds
        """
        self.calls = calls
        self.period = period
        self.tokens = calls
        self.last_update = datetime.now()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until a request can be made."""
        async with self._lock:
            now = datetime.now()
            elapsed = (now - self.last_update).total_seconds()

            # Refill tokens
            self.tokens = min(
                self.calls,
                self.tokens + (elapsed * self.calls / self.period)
            )
            self.last_update = now

            if self.tokens < 1:
                wait_time = (1 - self.tokens) * self.period / self.calls
                logger.debug(f"Rate limit: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                self.tokens = 1

            self.tokens -= 1


class BaseAPIClient(ABC):
    """
    Base class for all API clients.

    Provides common functionality:
    - Async HTTP requests
    - Caching with TTL
    - Rate limiting
    - Circuit breaker
    - Error handling
    """

    BASE_URL: str = ""

    def __init__(
        self,
        api_key: Optional[str] = None,
        env_var: Optional[str] = None,
        cache_ttl: int = 3600,
        cache_maxsize: int = 100,
        rate_limit_calls: int = 60,
        rate_limit_period: float = 60.0
    ):
        """
        Initialize the API client.

        Args:
            api_key: API key (or loaded from env_var)
            env_var: Environment variable name for API key
            cache_ttl: Cache time-to-live in seconds
            cache_maxsize: Maximum cache entries
            rate_limit_calls: Max calls per period
            rate_limit_period: Rate limit period in seconds
        """
        self.api_key = api_key or (os.getenv(env_var) if env_var else None)
        self._session: Optional[aiohttp.ClientSession] = None
        self._cache: TTLCache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)
        self._rate_limiter = RateLimiter(rate_limit_calls, rate_limit_period)
        self._circuit_breaker = CircuitBreaker()

    def is_available(self) -> bool:
        """Check if API is configured and available."""
        return bool(self.api_key)

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self._session = aiohttp.ClientSession(
                headers=self._get_headers(),
                timeout=timeout
            )
        return self._session

    def _get_headers(self) -> Dict[str, str]:
        """Get default headers. Override in subclasses."""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        method: str = "GET",
        use_cache: bool = True,
        json_data: Optional[Dict] = None
    ) -> Any:
        """
        Make API request with caching and error handling.

        Args:
            endpoint: API endpoint (appended to BASE_URL)
            params: Query parameters
            method: HTTP method
            use_cache: Whether to use cache
            json_data: JSON body for POST requests

        Returns:
            Parsed JSON response

        Raises:
            RateLimitError: If rate limit exceeded
            APIError: For other API errors
        """
        # Check circuit breaker
        if not self._circuit_breaker.can_execute():
            raise APIError(f"Circuit breaker open for {self.__class__.__name__}")

        # Check cache
        cache_key = f"{method}:{endpoint}:{params}"
        if use_cache and method == "GET" and cache_key in self._cache:
            logger.debug(f"Cache hit: {cache_key}")
            return self._cache[cache_key]

        # Rate limiting
        await self._rate_limiter.acquire()

        # Build URL
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}" if self.BASE_URL else endpoint

        try:
            session = await self._get_session()

            async with session.request(
                method,
                url,
                params=params,
                json=json_data
            ) as response:

                if response.status == 429:
                    self._circuit_breaker.record_failure()
                    raise RateLimitError(
                        f"Rate limit exceeded for {self.__class__.__name__}"
                    )

                if response.status >= 400:
                    self._circuit_breaker.record_failure()
                    text = await response.text()
                    raise APIError(
                        f"{self.__class__.__name__} error {response.status}: {text[:200]}"
                    )

                data = await response.json()
                self._circuit_breaker.record_success()

                # Cache successful GET responses
                if use_cache and method == "GET":
                    self._cache[cache_key] = data

                return data

        except aiohttp.ClientError as e:
            self._circuit_breaker.record_failure()
            raise APIError(f"Request failed: {e}") from e

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
