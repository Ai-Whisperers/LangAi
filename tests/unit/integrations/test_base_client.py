"""Tests for base API client functionality."""

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from company_researcher.integrations.base_client import (
    APIError,
    RateLimitError,
    CircuitState,
    CircuitBreaker,
    RateLimiter,
    BaseAPIClient,
)


class TestAPIError:
    """Tests for APIError exception."""

    def test_api_error_is_exception(self):
        """APIError should inherit from Exception."""
        assert issubclass(APIError, Exception)

    def test_api_error_message(self):
        """APIError should store message."""
        error = APIError("Test error message")
        assert str(error) == "Test error message"

    def test_api_error_empty_message(self):
        """APIError should accept empty message."""
        error = APIError("")
        assert str(error) == ""


class TestRateLimitError:
    """Tests for RateLimitError exception."""

    def test_rate_limit_error_inherits_api_error(self):
        """RateLimitError should inherit from APIError."""
        assert issubclass(RateLimitError, APIError)

    def test_rate_limit_error_message(self):
        """RateLimitError should store message."""
        error = RateLimitError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"


class TestCircuitState:
    """Tests for CircuitState enum."""

    def test_circuit_states(self):
        """CircuitState should have correct values."""
        assert CircuitState.CLOSED.value == "closed"
        assert CircuitState.OPEN.value == "open"
        assert CircuitState.HALF_OPEN.value == "half_open"

    def test_circuit_state_count(self):
        """CircuitState should have 3 states."""
        assert len(CircuitState) == 3


class TestCircuitBreakerInit:
    """Tests for CircuitBreaker initialization."""

    def test_default_values(self):
        """CircuitBreaker should have sensible defaults."""
        cb = CircuitBreaker()
        assert cb.failure_threshold == 5
        assert cb.recovery_timeout == 60
        assert cb.success_threshold == 3
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.success_count == 0
        assert cb.last_failure_time is None

    def test_custom_thresholds(self):
        """CircuitBreaker should accept custom thresholds."""
        cb = CircuitBreaker(
            failure_threshold=10,
            recovery_timeout=120,
            success_threshold=5
        )
        assert cb.failure_threshold == 10
        assert cb.recovery_timeout == 120
        assert cb.success_threshold == 5


class TestCircuitBreakerRecordSuccess:
    """Tests for CircuitBreaker.record_success method."""

    def test_success_resets_failure_count(self):
        """record_success should reset failure count."""
        cb = CircuitBreaker()
        cb.failure_count = 3
        cb.record_success()
        assert cb.failure_count == 0

    def test_success_in_half_open_increments_counter(self):
        """record_success in HALF_OPEN should increment success count."""
        cb = CircuitBreaker()
        cb.state = CircuitState.HALF_OPEN
        cb.record_success()
        assert cb.success_count == 1

    def test_enough_successes_closes_circuit(self):
        """Enough successes in HALF_OPEN should close circuit."""
        cb = CircuitBreaker(success_threshold=2)
        cb.state = CircuitState.HALF_OPEN
        cb.success_count = 1
        cb.record_success()
        assert cb.state == CircuitState.CLOSED
        assert cb.success_count == 0

    def test_success_in_closed_state(self):
        """record_success in CLOSED should just reset failure count."""
        cb = CircuitBreaker()
        cb.failure_count = 2
        cb.record_success()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0


class TestCircuitBreakerRecordFailure:
    """Tests for CircuitBreaker.record_failure method."""

    def test_failure_increments_count(self):
        """record_failure should increment failure count."""
        cb = CircuitBreaker()
        cb.record_failure()
        assert cb.failure_count == 1

    def test_failure_updates_last_failure_time(self):
        """record_failure should update last_failure_time."""
        cb = CircuitBreaker()
        cb.record_failure()
        assert cb.last_failure_time is not None
        assert isinstance(cb.last_failure_time, datetime)

    def test_enough_failures_opens_circuit(self):
        """Enough failures should open the circuit."""
        cb = CircuitBreaker(failure_threshold=3)
        for _ in range(3):
            cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 3

    def test_fewer_failures_keeps_circuit_closed(self):
        """Fewer failures should keep circuit closed."""
        cb = CircuitBreaker(failure_threshold=5)
        for _ in range(4):
            cb.record_failure()
        assert cb.state == CircuitState.CLOSED


class TestCircuitBreakerCanExecute:
    """Tests for CircuitBreaker.can_execute method."""

    def test_closed_circuit_allows_execution(self):
        """CLOSED circuit should allow execution."""
        cb = CircuitBreaker()
        assert cb.can_execute() is True

    def test_open_circuit_blocks_execution(self):
        """OPEN circuit should block execution."""
        cb = CircuitBreaker()
        cb.state = CircuitState.OPEN
        cb.last_failure_time = datetime.now(timezone.utc)
        assert cb.can_execute() is False

    def test_open_circuit_transitions_to_half_open_after_timeout(self):
        """OPEN circuit should transition to HALF_OPEN after timeout."""
        cb = CircuitBreaker(recovery_timeout=1)
        cb.state = CircuitState.OPEN
        cb.last_failure_time = datetime.now(timezone.utc) - timedelta(seconds=2)
        assert cb.can_execute() is True
        assert cb.state == CircuitState.HALF_OPEN

    def test_half_open_circuit_allows_execution(self):
        """HALF_OPEN circuit should allow execution."""
        cb = CircuitBreaker()
        cb.state = CircuitState.HALF_OPEN
        assert cb.can_execute() is True


class TestRateLimiterInit:
    """Tests for RateLimiter initialization."""

    def test_initialization(self):
        """RateLimiter should initialize with correct values."""
        rl = RateLimiter(calls=10, period=60.0)
        assert rl.calls == 10
        assert rl.period == 60.0
        assert rl.tokens == 10

    def test_default_tokens_equal_calls(self):
        """Initial tokens should equal calls."""
        rl = RateLimiter(calls=5, period=10.0)
        assert rl.tokens == rl.calls


class TestRateLimiterAcquire:
    """Tests for RateLimiter.acquire method."""

    @pytest.mark.asyncio
    async def test_acquire_decrements_tokens(self):
        """acquire should decrement tokens."""
        rl = RateLimiter(calls=10, period=60.0)
        initial_tokens = rl.tokens
        await rl.acquire()
        assert rl.tokens < initial_tokens

    @pytest.mark.asyncio
    async def test_acquire_multiple_times(self):
        """Multiple acquires should decrement tokens."""
        rl = RateLimiter(calls=10, period=60.0)
        for _ in range(5):
            await rl.acquire()
        assert rl.tokens < 6  # Started at 10, used 5

    @pytest.mark.asyncio
    async def test_tokens_refill_over_time(self):
        """Tokens should refill over time."""
        rl = RateLimiter(calls=10, period=1.0)  # Fast refill
        # Use all tokens
        for _ in range(10):
            await rl.acquire()
        # Wait for refill
        await asyncio.sleep(0.2)
        # Should have some tokens back
        await rl.acquire()  # Should not block long


class TestBaseAPIClientInit:
    """Tests for BaseAPIClient initialization."""

    def test_initialization_with_api_key(self):
        """BaseAPIClient should store api_key."""
        class TestClient(BaseAPIClient):
            pass

        client = TestClient(api_key="test_key")
        assert client.api_key == "test_key"

    def test_initialization_without_api_key(self):
        """BaseAPIClient should accept no api_key."""
        class TestClient(BaseAPIClient):
            pass

        client = TestClient()
        assert client.api_key is None

    def test_cache_parameters(self):
        """BaseAPIClient should initialize cache with parameters."""
        class TestClient(BaseAPIClient):
            pass

        client = TestClient(cache_ttl=7200, cache_maxsize=500)
        assert client._cache.maxsize == 500
        assert client._cache.ttl == 7200


class TestBaseAPIClientIsAvailable:
    """Tests for BaseAPIClient.is_available method."""

    def test_available_with_api_key(self):
        """is_available should return True with api_key."""
        class TestClient(BaseAPIClient):
            pass

        client = TestClient(api_key="key")
        assert client.is_available() is True

    def test_not_available_without_api_key(self):
        """is_available should return False without api_key."""
        class TestClient(BaseAPIClient):
            pass

        client = TestClient()
        assert client.is_available() is False


class TestBaseAPIClientHeaders:
    """Tests for BaseAPIClient._get_headers method."""

    def test_default_headers(self):
        """_get_headers should return default JSON headers."""
        class TestClient(BaseAPIClient):
            pass

        client = TestClient()
        headers = client._get_headers()
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"

    def test_custom_headers(self):
        """_get_headers can be overridden in subclass."""
        class TestClient(BaseAPIClient):
            def _get_headers(self):
                return {"Authorization": f"Bearer {self.api_key}"}

        client = TestClient(api_key="my_key")
        headers = client._get_headers()
        assert headers["Authorization"] == "Bearer my_key"


class TestBaseAPIClientContextManager:
    """Tests for BaseAPIClient context manager."""

    @pytest.mark.asyncio
    async def test_context_manager_entry(self):
        """Context manager should return client on entry."""
        class TestClient(BaseAPIClient):
            pass

        async with TestClient() as client:
            assert isinstance(client, TestClient)

    @pytest.mark.asyncio
    async def test_context_manager_closes_session(self):
        """Context manager should close session on exit."""
        class TestClient(BaseAPIClient):
            pass

        client = TestClient()
        mock_session = MagicMock()
        mock_session.closed = False
        mock_session.close = AsyncMock()
        client._session = mock_session

        async with client:
            pass

        mock_session.close.assert_called_once()


class TestBaseAPIClientClose:
    """Tests for BaseAPIClient.close method."""

    @pytest.mark.asyncio
    async def test_close_with_session(self):
        """close should close active session."""
        class TestClient(BaseAPIClient):
            pass

        client = TestClient()
        mock_session = MagicMock()
        mock_session.closed = False
        mock_session.close = AsyncMock()
        client._session = mock_session

        await client.close()
        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_without_session(self):
        """close should handle no session gracefully."""
        class TestClient(BaseAPIClient):
            pass

        client = TestClient()
        await client.close()  # Should not raise


class TestBaseAPIClientRequest:
    """Tests for BaseAPIClient._request method."""

    @pytest.mark.asyncio
    async def test_request_uses_circuit_breaker(self):
        """_request should check circuit breaker."""
        class TestClient(BaseAPIClient):
            BASE_URL = "https://api.example.com"

        client = TestClient(api_key="key")
        client._circuit_breaker.state = CircuitState.OPEN
        client._circuit_breaker.last_failure_time = datetime.now(timezone.utc)

        with pytest.raises(APIError) as exc:
            await client._request("test")
        assert "Circuit breaker open" in str(exc.value)

    @pytest.mark.asyncio
    async def test_request_cache_hit(self):
        """_request should return cached data for GET."""
        class TestClient(BaseAPIClient):
            BASE_URL = "https://api.example.com"

        client = TestClient()
        cache_key = "GET:test:{}"
        client._cache[cache_key] = {"cached": True}

        result = await client._request("test", params={})
        assert result == {"cached": True}

    @pytest.mark.asyncio
    async def test_request_builds_correct_url(self):
        """_request should build correct URL from BASE_URL and endpoint."""
        class TestClient(BaseAPIClient):
            BASE_URL = "https://api.example.com"

        client = TestClient()

        with patch.object(client, '_rate_limiter') as mock_limiter:
            mock_limiter.acquire = AsyncMock()
            with patch.object(client, '_get_session') as mock_get_session:
                mock_session = MagicMock()
                mock_response = MagicMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value={"data": "test"})

                mock_context = MagicMock()
                mock_context.__aenter__ = AsyncMock(return_value=mock_response)
                mock_context.__aexit__ = AsyncMock(return_value=None)
                mock_session.request = MagicMock(return_value=mock_context)
                mock_get_session.return_value = mock_session

                await client._request("/endpoint")

                mock_session.request.assert_called_once()
                call_args = mock_session.request.call_args
                assert "https://api.example.com/endpoint" in str(call_args)


class TestCircuitBreakerIntegration:
    """Integration tests for circuit breaker behavior."""

    def test_failure_recovery_cycle(self):
        """Circuit should go through full failure/recovery cycle."""
        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=1,
            success_threshold=2
        )

        # Start closed
        assert cb.state == CircuitState.CLOSED
        assert cb.can_execute() is True

        # Record failures until open
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

        # Initially blocked
        assert cb.can_execute() is False

        # Simulate timeout passing
        cb.last_failure_time = datetime.now(timezone.utc) - timedelta(seconds=2)

        # Now should transition to half-open
        assert cb.can_execute() is True
        assert cb.state == CircuitState.HALF_OPEN

        # Record successes to close
        cb.record_success()
        cb.record_success()
        assert cb.state == CircuitState.CLOSED

    def test_half_open_failure_reopens_circuit(self):
        """Failure in HALF_OPEN should reopen circuit."""
        cb = CircuitBreaker(failure_threshold=1)
        cb.state = CircuitState.HALF_OPEN
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
