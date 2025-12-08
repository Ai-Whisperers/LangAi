"""
API Middleware (Phase 18.2).

Custom middleware for:
- Rate limiting
- API key authentication
- Request logging
- CORS handling
"""

from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
import time
import hashlib
import hmac
import logging
from collections import defaultdict

try:
    from fastapi import Request, Response, HTTPException
    from fastapi.responses import JSONResponse
    from starlette.middleware.base import BaseHTTPMiddleware
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Stubs for when FastAPI not available
    class BaseHTTPMiddleware:
        pass
    class Request:
        pass
    class Response:
        pass


# ============================================================================
# Rate Limiting
# ============================================================================

class RateLimiter:
    """In-memory rate limiter using sliding window."""

    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_limit: int = 10
    ):
        self._rpm = requests_per_minute
        self._rph = requests_per_hour
        self._burst = burst_limit

        # Track requests per client
        self._minute_windows: Dict[str, List[float]] = defaultdict(list)
        self._hour_windows: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_id: str) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed.

        Returns:
            Tuple of (allowed, info_dict)
        """
        now = time.time()
        minute_ago = now - 60
        hour_ago = now - 3600

        # Clean old entries
        self._minute_windows[client_id] = [
            t for t in self._minute_windows[client_id] if t > minute_ago
        ]
        self._hour_windows[client_id] = [
            t for t in self._hour_windows[client_id] if t > hour_ago
        ]

        minute_count = len(self._minute_windows[client_id])
        hour_count = len(self._hour_windows[client_id])

        info = {
            "limit_minute": self._rpm,
            "remaining_minute": max(0, self._rpm - minute_count),
            "limit_hour": self._rph,
            "remaining_hour": max(0, self._rph - hour_count)
        }

        # Check limits
        if minute_count >= self._rpm:
            oldest = min(self._minute_windows[client_id])
            info["retry_after"] = int(oldest + 60 - now)
            return False, info

        if hour_count >= self._rph:
            oldest = min(self._hour_windows[client_id])
            info["retry_after"] = int(oldest + 3600 - now)
            return False, info

        # Check burst
        recent = [t for t in self._minute_windows[client_id] if t > now - 1]
        if len(recent) >= self._burst:
            info["retry_after"] = 1
            return False, info

        # Record request
        self._minute_windows[client_id].append(now)
        self._hour_windows[client_id].append(now)

        return True, info


if FASTAPI_AVAILABLE:
    class RateLimitMiddleware(BaseHTTPMiddleware):
        """Rate limiting middleware."""

        def __init__(
            self,
            app,
            requests_per_minute: int = 60,
            requests_per_hour: int = 1000,
            exclude_paths: Optional[List[str]] = None
        ):
            super().__init__(app)
            self._limiter = RateLimiter(
                requests_per_minute=requests_per_minute,
                requests_per_hour=requests_per_hour
            )
            self._exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json"]

        async def dispatch(self, request: Request, call_next: Callable) -> Response:
            # Skip excluded paths
            if request.url.path in self._exclude_paths:
                return await call_next(request)

            # Get client identifier
            client_id = self._get_client_id(request)

            # Check rate limit
            allowed, info = self._limiter.is_allowed(client_id)

            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "retry_after": info.get("retry_after", 60),
                        "limit": info.get("limit_minute"),
                        "remaining": 0
                    },
                    headers={
                        "Retry-After": str(info.get("retry_after", 60)),
                        "X-RateLimit-Limit": str(info.get("limit_minute")),
                        "X-RateLimit-Remaining": "0"
                    }
                )

            # Process request
            response = await call_next(request)

            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(info.get("limit_minute"))
            response.headers["X-RateLimit-Remaining"] = str(info.get("remaining_minute"))

            return response

        def _get_client_id(self, request: Request) -> str:
            """Get client identifier from request."""
            # Try API key first
            api_key = request.headers.get("X-API-Key")
            if api_key:
                return f"key:{api_key[:8]}"

            # Fall back to IP
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                return f"ip:{forwarded.split(',')[0].strip()}"

            return f"ip:{request.client.host if request.client else 'unknown'}"


# ============================================================================
# API Key Authentication
# ============================================================================

    class APIKeyMiddleware(BaseHTTPMiddleware):
        """API key authentication middleware."""

        def __init__(
            self,
            app,
            api_keys: Optional[Dict[str, str]] = None,
            require_auth: bool = True,
            exclude_paths: Optional[List[str]] = None
        ):
            super().__init__(app)
            self._api_keys = api_keys or {}
            self._require_auth = require_auth
            self._exclude_paths = exclude_paths or [
                "/health", "/docs", "/openapi.json", "/redoc"
            ]

        async def dispatch(self, request: Request, call_next: Callable) -> Response:
            # Skip excluded paths
            if request.url.path in self._exclude_paths:
                return await call_next(request)

            # Skip if auth not required
            if not self._require_auth:
                return await call_next(request)

            # Get API key
            api_key = request.headers.get("X-API-Key")

            if not api_key:
                return JSONResponse(
                    status_code=401,
                    content={
                        "error": "API key required",
                        "detail": "Include X-API-Key header"
                    }
                )

            # Validate API key
            if api_key not in self._api_keys:
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "Invalid API key",
                        "detail": "The provided API key is not valid"
                    }
                )

            # Add user info to request state
            request.state.api_key = api_key
            request.state.user_id = self._api_keys.get(api_key, "unknown")

            return await call_next(request)

        def add_api_key(self, key: str, user_id: str):
            """Add an API key."""
            self._api_keys[key] = user_id

        def revoke_api_key(self, key: str):
            """Revoke an API key."""
            self._api_keys.pop(key, None)


# ============================================================================
# Request Logging
# ============================================================================

    class RequestLoggingMiddleware(BaseHTTPMiddleware):
        """Request logging middleware."""

        def __init__(
            self,
            app,
            logger: Optional[logging.Logger] = None,
            log_body: bool = False,
            exclude_paths: Optional[List[str]] = None
        ):
            super().__init__(app)
            self._logger = logger or logging.getLogger("api.requests")
            self._log_body = log_body
            self._exclude_paths = exclude_paths or ["/health"]

        async def dispatch(self, request: Request, call_next: Callable) -> Response:
            # Skip excluded paths
            if request.url.path in self._exclude_paths:
                return await call_next(request)

            start_time = time.time()
            request_id = self._generate_request_id()

            # Log request
            self._logger.info(
                f"[{request_id}] {request.method} {request.url.path} "
                f"client={request.client.host if request.client else 'unknown'}"
            )

            # Add request ID to state
            request.state.request_id = request_id

            try:
                response = await call_next(request)
                duration_ms = (time.time() - start_time) * 1000

                # Log response
                self._logger.info(
                    f"[{request_id}] {response.status_code} "
                    f"duration={duration_ms:.2f}ms"
                )

                # Add request ID to response
                response.headers["X-Request-ID"] = request_id

                return response

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                self._logger.error(
                    f"[{request_id}] ERROR: {str(e)} "
                    f"duration={duration_ms:.2f}ms"
                )
                raise

        def _generate_request_id(self) -> str:
            """Generate unique request ID."""
            import uuid
            return str(uuid.uuid4())[:8]


# ============================================================================
# Webhook Signature Verification
# ============================================================================

class WebhookSigner:
    """Sign and verify webhook payloads."""

    def __init__(self, secret: str):
        self._secret = secret.encode()

    def sign(self, payload: bytes, timestamp: int) -> str:
        """Sign a webhook payload."""
        message = f"{timestamp}.{payload.decode()}".encode()
        signature = hmac.new(self._secret, message, hashlib.sha256).hexdigest()
        return f"v1={signature}"

    def verify(
        self,
        payload: bytes,
        signature: str,
        timestamp: int,
        tolerance_seconds: int = 300
    ) -> bool:
        """Verify a webhook signature."""
        # Check timestamp
        now = int(time.time())
        if abs(now - timestamp) > tolerance_seconds:
            return False

        # Verify signature
        expected = self.sign(payload, timestamp)
        return hmac.compare_digest(expected, signature)


# ============================================================================
# CORS Configuration
# ============================================================================

def get_cors_config(
    allow_origins: Optional[List[str]] = None,
    allow_credentials: bool = True,
    allow_methods: Optional[List[str]] = None,
    allow_headers: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Get CORS configuration dictionary."""
    return {
        "allow_origins": allow_origins or ["*"],
        "allow_credentials": allow_credentials,
        "allow_methods": allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": allow_headers or ["*"],
    }


if not FASTAPI_AVAILABLE:
    # Stubs when FastAPI not available
    class RateLimitMiddleware:
        def __init__(self, *args, **kwargs):
            raise ImportError("FastAPI required")

    class APIKeyMiddleware:
        def __init__(self, *args, **kwargs):
            raise ImportError("FastAPI required")

    class RequestLoggingMiddleware:
        def __init__(self, *args, **kwargs):
            raise ImportError("FastAPI required")
