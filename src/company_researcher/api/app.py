"""
FastAPI Application (Phase 18.5).

Main application setup and configuration:
- FastAPI app creation
- Middleware registration
- Route mounting
- WebSocket setup
- Server startup
"""

from typing import Dict, Any, Optional, List, Set
from datetime import datetime
import logging
import os
import re

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from contextlib import asynccontextmanager
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Security: Default allowed origins (can be overridden via environment)
DEFAULT_CORS_ORIGINS: Set[str] = {
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
}

# Security: Origin validation pattern
ORIGIN_PATTERN = re.compile(r'^https?://[a-zA-Z0-9][-a-zA-Z0-9.]*[a-zA-Z0-9](:\d+)?$')


def _get_allowed_origins(cors_origins: Optional[List[str]] = None) -> List[str]:
    """
    Get validated list of allowed CORS origins.

    Security: Never returns wildcard when credentials are enabled.
    """
    # Check environment variable first
    env_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    if env_origins:
        origins = [o.strip() for o in env_origins.split(",") if o.strip()]
    elif cors_origins:
        origins = cors_origins
    else:
        origins = list(DEFAULT_CORS_ORIGINS)

    # Validate and filter origins
    validated = []
    for origin in origins:
        # Reject wildcard - security risk with credentials
        if origin == "*":
            logging.warning(
                "CORS wildcard origin rejected for security. "
                "Specify explicit origins or set CORS_ALLOWED_ORIGINS env var."
            )
            continue
        # Validate origin format
        if ORIGIN_PATTERN.match(origin):
            validated.append(origin)
        else:
            logging.warning(f"Invalid CORS origin rejected: {origin}")

    return validated if validated else list(DEFAULT_CORS_ORIGINS)


# ============================================================================
# Application Singleton
# ============================================================================

_app: Optional["FastAPI"] = None
_ws_manager = None


def get_app() -> "FastAPI":
    """Get the FastAPI application instance."""
    global _app
    if _app is None:
        _app = create_app()
    return _app


def get_ws_manager():
    """Get WebSocket manager instance."""
    global _ws_manager
    if _ws_manager is None:
        from .websocket import WebSocketManager
        _ws_manager = WebSocketManager()
    return _ws_manager


# ============================================================================
# Application Factory
# ============================================================================

def create_app(
    title: str = "Company Researcher API",
    version: str = "1.0.0",
    enable_cors: bool = True,
    cors_origins: Optional[List[str]] = None,
    enable_rate_limiting: bool = True,
    rate_limit_rpm: int = 60,
    enable_logging: bool = True,
    api_keys: Optional[Dict[str, str]] = None,
    require_auth: bool = False
) -> "FastAPI":
    """
    Create and configure the FastAPI application.

    Args:
        title: API title
        version: API version
        enable_cors: Enable CORS middleware
        cors_origins: Allowed CORS origins
        enable_rate_limiting: Enable rate limiting
        rate_limit_rpm: Requests per minute limit
        enable_logging: Enable request logging
        api_keys: API keys for authentication
        require_auth: Require API key authentication

    Returns:
        Configured FastAPI application
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI not installed. Run: pip install fastapi uvicorn")

    # Lifespan context
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        logging.info("Starting Company Researcher API...")
        yield
        # Shutdown
        logging.info("Shutting down Company Researcher API...")

    # Create app
    app = FastAPI(
        title=title,
        version=version,
        description="""
# Company Researcher API

AI-powered company research and analysis platform.

## Features

- **Single Company Research**: Deep-dive analysis of individual companies
- **Batch Processing**: Research multiple companies in parallel
- **Real-time Updates**: WebSocket support for live progress
- **Multiple Depth Levels**: Quick, Standard, and Comprehensive research

## Research Agents

- Financial Analysis
- Market Analysis
- Competitive Intelligence
- News & Sentiment
- Brand Audit
- Social Media Analysis
- Sales Intelligence
- Investment Analysis

## Authentication

Include your API key in the `X-API-Key` header.
        """,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # Configure CORS (with security validation)
    if enable_cors:
        validated_origins = _get_allowed_origins(cors_origins)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=validated_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Request-ID"],
        )
        logging.info(f"CORS enabled for origins: {validated_origins}")

    # Add rate limiting
    if enable_rate_limiting:
        from .middleware import RateLimitMiddleware
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=rate_limit_rpm
        )

    # Add request logging
    if enable_logging:
        from .middleware import RequestLoggingMiddleware
        app.add_middleware(RequestLoggingMiddleware)

    # Add authentication
    if require_auth and api_keys:
        from .middleware import APIKeyMiddleware
        app.add_middleware(
            APIKeyMiddleware,
            api_keys=api_keys,
            require_auth=True
        )

    # Mount routes
    from .routes import router as research_router
    app.include_router(research_router)

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """API root endpoint."""
        return {
            "name": title,
            "version": version,
            "status": "running",
            "docs": "/docs",
            "timestamp": datetime.now().isoformat()
        }

    # WebSocket endpoint
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time updates."""
        ws_manager = get_ws_manager()
        connection_id = await ws_manager.connect(websocket)

        try:
            while True:
                data = await websocket.receive_json()
                await ws_manager.handle_message(websocket, data)
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket)
        except Exception as e:
            logging.error(f"WebSocket error: {e}")
            ws_manager.disconnect(websocket)

    # Error handlers
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not found",
                "path": str(request.url.path),
                "timestamp": datetime.now().isoformat()
            }
        )

    @app.exception_handler(500)
    async def server_error_handler(request, exc):
        logging.error(f"Server error: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "timestamp": datetime.now().isoformat()
            }
        )

    return app


# ============================================================================
# Server Runner
# ============================================================================

def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    workers: int = 1,
    log_level: str = "info"
):
    """
    Run the API server.

    Args:
        host: Host to bind to
        port: Port to listen on
        reload: Enable auto-reload (development)
        workers: Number of worker processes
        log_level: Logging level
    """
    try:
        import uvicorn
    except ImportError:
        raise ImportError("uvicorn not installed. Run: pip install uvicorn")

    app = get_app()

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        log_level=log_level
    )


def run_server_async(
    host: str = "0.0.0.0",
    port: int = 8000,
    log_level: str = "info"
):
    """
    Run server asynchronously (for embedding in async apps).
    """
    try:
        import uvicorn
    except ImportError:
        raise ImportError("uvicorn not installed. Run: pip install uvicorn")

    config = uvicorn.Config(
        get_app(),
        host=host,
        port=port,
        log_level=log_level
    )
    server = uvicorn.Server(config)
    return server


# ============================================================================
# CLI Entry Point
# ============================================================================

def main():
    """CLI entry point for running the server."""
    import argparse

    parser = argparse.ArgumentParser(description="Company Researcher API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--workers", type=int, default=1, help="Number of workers")
    parser.add_argument("--log-level", default="info", help="Log level")

    args = parser.parse_args()

    run_server(
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level=args.log_level
    )


if __name__ == "__main__":
    main()
