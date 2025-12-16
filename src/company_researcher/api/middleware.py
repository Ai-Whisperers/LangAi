"""
API Middleware (Phase 18.2).

Custom middleware for:
- Rate limiting
- API key authentication
- Request logging
- CORS handling
"""

import asyncio
import hashlib
import hmac
import logging
import threading
import time
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional

try:
    from fastapi import Request, Response
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


# Common path constants
PATH_HEALTH = "/health"
PATH_DOCS = "/docs"
PATH_OPENAPI = "/openapi.json"
PATH_REDOC = "/redoc"

# Default excluded paths for various middleware
DEFAULT_EXCLUDED_PATHS = [PATH_HEALTH, PATH_DOCS, PATH_OPENAPI]
DEFAULT_AUTH_EXCLUDED_PATHS = [PATH_HEALTH, PATH_DOCS, PATH_OPENAPI, PATH_REDOC]

# Error message for missing FastAPI
ERR_FASTAPI_REQUIRED = "FastAPI required"


# ============================================================================
# Rate Limiting
# ============================================================================


class RateLimiter:
    """
    In-memory rate limiter using sliding window.

    Thread-safe implementation using threading.RLock for synchronous access
    and optional asyncio.Lock for async contexts.
    """

    def __init__(
        self, requests_per_minute: int = 60, requests_per_hour: int = 1000, burst_limit: int = 10
    ):
        self._rpm = requests_per_minute
        self._rph = requests_per_hour
        self._burst = burst_limit

        # Track requests per client
        self._minute_windows: Dict[str, List[float]] = defaultdict(list)
        self._hour_windows: Dict[str, List[float]] = defaultdict(list)

        # Thread safety locks
        self._sync_lock = threading.RLock()
        self._async_lock: Optional[asyncio.Lock] = None

    def _get_async_lock(self) -> asyncio.Lock:
        """Get or create async lock (must be created in event loop context)."""
        if self._async_lock is None:
            self._async_lock = asyncio.Lock()
        return self._async_lock

    def is_allowed(self, client_id: str) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed (synchronous, thread-safe).

        Returns:
            Tuple of (allowed, info_dict)
        """
        with self._sync_lock:
            return self._check_rate_limit(client_id)

    async def is_allowed_async(self, client_id: str) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed (async, non-blocking).

        Returns:
            Tuple of (allowed, info_dict)
        """
        async with self._get_async_lock():
            return self._check_rate_limit(client_id)

    def _check_rate_limit(self, client_id: str) -> tuple[bool, Dict[str, Any]]:
        """Internal rate limit check (must be called with lock held)."""
        now = time.time()
        minute_ago = now - 60
        hour_ago = now - 3600

        # Clean old entries
        self._minute_windows[client_id] = [
            t for t in self._minute_windows[client_id] if t > minute_ago
        ]
        self._hour_windows[client_id] = [t for t in self._hour_windows[client_id] if t > hour_ago]

        minute_count = len(self._minute_windows[client_id])
        hour_count = len(self._hour_windows[client_id])

        info = {
            "limit_minute": self._rpm,
            "remaining_minute": max(0, self._rpm - minute_count),
            "limit_hour": self._rph,
            "remaining_hour": max(0, self._rph - hour_count),
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
            exclude_paths: Optional[List[str]] = None,
        ):
            super().__init__(app)
            self._limiter = RateLimiter(
                requests_per_minute=requests_per_minute, requests_per_hour=requests_per_hour
            )
            self._exclude_paths = exclude_paths or DEFAULT_EXCLUDED_PATHS

        async def dispatch(self, request: Request, call_next: Callable) -> Response:
            # Skip excluded paths
            if request.url.path in self._exclude_paths:
                return await call_next(request)

            # Get client identifier
            client_id = self._get_client_id(request)

            # Check rate limit (use async version to avoid blocking event loop)
            allowed, info = await self._limiter.is_allowed_async(client_id)

            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "retry_after": info.get("retry_after", 60),
                        "limit": info.get("limit_minute"),
                        "remaining": 0,
                    },
                    headers={
                        "Retry-After": str(info.get("retry_after", 60)),
                        "X-RateLimit-Limit": str(info.get("limit_minute")),
                        "X-RateLimit-Remaining": "0",
                    },
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
            exclude_paths: Optional[List[str]] = None,
        ):
            super().__init__(app)
            self._api_keys = api_keys or {}
            self._require_auth = require_auth
            self._exclude_paths = exclude_paths or DEFAULT_AUTH_EXCLUDED_PATHS

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
                    content={"error": "API key required", "detail": "Include X-API-Key header"},
                )

            # Validate API key
            if api_key not in self._api_keys:
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "Invalid API key",
                        "detail": "The provided API key is not valid",
                    },
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
            exclude_paths: Optional[List[str]] = None,
        ):
            super().__init__(app)
            self._logger = logger or logging.getLogger("api.requests")
            self._log_body = log_body
            self._exclude_paths = exclude_paths or [PATH_HEALTH]

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
                    f"[{request_id}] {response.status_code} " f"duration={duration_ms:.2f}ms"
                )

                # Add request ID to response
                response.headers["X-Request-ID"] = request_id

                return response

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                self._logger.error(
                    f"[{request_id}] ERROR: {str(e)} " f"duration={duration_ms:.2f}ms"
                )
                raise

        def _generate_request_id(self) -> str:
            """Generate unique request ID."""
            import uuid

            return str(uuid.uuid4())[:8]


# ============================================================================
# Request Size Limits
# ============================================================================

if FASTAPI_AVAILABLE:

    class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
        """
        Middleware to limit request body size.

        Prevents denial-of-service attacks via large request bodies.
        """

        # Default limits
        DEFAULT_MAX_BODY_SIZE = 10 * 1024 * 1024  # 10 MB
        DEFAULT_MAX_JSON_SIZE = 1 * 1024 * 1024  # 1 MB

        def __init__(
            self,
            app,
            max_body_size: int = None,
            max_json_size: int = None,
            exclude_paths: Optional[List[str]] = None,
        ):
            """
            Initialize request size limit middleware.

            Args:
                app: FastAPI app
                max_body_size: Maximum body size in bytes (default 10MB)
                max_json_size: Maximum JSON body size in bytes (default 1MB)
                exclude_paths: Paths to exclude from size checks
            """
            super().__init__(app)
            self._max_body_size = max_body_size or self.DEFAULT_MAX_BODY_SIZE
            self._max_json_size = max_json_size or self.DEFAULT_MAX_JSON_SIZE
            self._exclude_paths = exclude_paths or DEFAULT_EXCLUDED_PATHS
            self._logger = logging.getLogger("api.sizelimit")

        async def dispatch(self, request: Request, call_next: Callable) -> Response:
            # Skip excluded paths
            if request.url.path in self._exclude_paths:
                return await call_next(request)

            # Skip requests without body
            if request.method in ["GET", "HEAD", "OPTIONS"]:
                return await call_next(request)

            # Check Content-Length header
            content_length = request.headers.get("Content-Length")
            if content_length:
                try:
                    size = int(content_length)

                    # Check against appropriate limit based on content type
                    content_type = request.headers.get("Content-Type", "")
                    if "application/json" in content_type:
                        max_size = self._max_json_size
                        size_type = "JSON"
                    else:
                        max_size = self._max_body_size
                        size_type = "Request body"

                    if size > max_size:
                        self._logger.warning(
                            f"Request too large: {size} bytes exceeds {max_size} limit "
                            f"from {request.client.host if request.client else 'unknown'}"
                        )
                        return JSONResponse(
                            status_code=413,
                            content={
                                "error": "Request entity too large",
                                "detail": f"{size_type} size ({size} bytes) exceeds limit ({max_size} bytes)",
                                "max_size": max_size,
                            },
                        )
                except ValueError:
                    pass

            return await call_next(request)

    # ============================================================================
    # CSRF Protection
    # ============================================================================

    class CSRFProtectionMiddleware(BaseHTTPMiddleware):
        """
        CSRF protection middleware using origin validation.

        For JSON APIs, validates Origin/Referer headers against allowed origins.
        This is appropriate for APIs that use cookies or authentication.
        """

        def __init__(
            self,
            app,
            allowed_origins: Optional[List[str]] = None,
            exclude_paths: Optional[List[str]] = None,
            safe_methods: Optional[List[str]] = None,
        ):
            super().__init__(app)
            self._allowed_origins = set(
                allowed_origins
                or [
                    "http://localhost:3000",
                    "http://localhost:8000",
                    "http://127.0.0.1:3000",
                    "http://127.0.0.1:8000",
                ]
            )
            self._exclude_paths = exclude_paths or DEFAULT_AUTH_EXCLUDED_PATHS
            # Safe methods don't require CSRF validation
            self._safe_methods = safe_methods or ["GET", "HEAD", "OPTIONS"]

        async def dispatch(self, request: Request, call_next: Callable) -> Response:
            # Skip excluded paths
            if request.url.path in self._exclude_paths:
                return await call_next(request)

            # Skip safe methods
            if request.method in self._safe_methods:
                return await call_next(request)

            # Validate origin for state-changing requests
            origin = request.headers.get("Origin")
            referer = request.headers.get("Referer")

            if not self._validate_origin(origin, referer):
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "CSRF validation failed",
                        "detail": "Invalid or missing Origin header",
                    },
                )

            return await call_next(request)

        def _validate_origin(self, origin: Optional[str], referer: Optional[str]) -> bool:
            """Validate origin or referer header."""
            # Check Origin header first
            if origin:
                return origin in self._allowed_origins

            # Fall back to Referer if no Origin
            if referer:
                # Extract origin from referer URL
                from urllib.parse import urlparse

                parsed = urlparse(referer)
                referer_origin = f"{parsed.scheme}://{parsed.netloc}"
                return referer_origin in self._allowed_origins

            # If neither present, deny for state-changing requests
            return False

        def add_allowed_origin(self, origin: str):
            """Add an allowed origin."""
            self._allowed_origins.add(origin)


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
        self, payload: bytes, signature: str, timestamp: int, tolerance_seconds: int = 300
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
    allow_headers: Optional[List[str]] = None,
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
            raise ImportError(ERR_FASTAPI_REQUIRED)

    class APIKeyMiddleware:
        def __init__(self, *args, **kwargs):
            raise ImportError(ERR_FASTAPI_REQUIRED)

    class RequestLoggingMiddleware:
        def __init__(self, *args, **kwargs):
            raise ImportError(ERR_FASTAPI_REQUIRED)

    class CSRFProtectionMiddleware:
        def __init__(self, *args, **kwargs):
            raise ImportError(ERR_FASTAPI_REQUIRED)
