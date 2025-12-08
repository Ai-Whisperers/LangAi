"""
API & Integration Layer (Phase 18).

REST and WebSocket API for company research:
- FastAPI-based REST endpoints
- WebSocket for real-time updates
- Authentication and rate limiting
- Webhook integrations
- Streaming results (SSE)

Usage:
    from src.company_researcher.api import create_app, run_server

    # Create FastAPI app
    app = create_app()

    # Run server
    run_server(host="0.0.0.0", port=8000)
"""

# Streaming (works without FastAPI)
from .streaming import (
    ProgressTracker,
    StreamEvent,
    EventType,
    StreamingResearchContext,
    stream_sse,
    create_progress_tracker,
    create_streaming_context,
)

# Check for FastAPI availability
try:
    from fastapi import FastAPI
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

if FASTAPI_AVAILABLE:
    from .app import (
        create_app,
        get_app,
    )
    from .routes import router as research_router
    from .websocket import WebSocketManager
    from .middleware import (
        RateLimitMiddleware,
        APIKeyMiddleware,
        RequestLoggingMiddleware,
    )
    from .models import (
        ResearchRequest,
        ResearchResponse,
        BatchRequest,
        BatchResponse,
        HealthResponse,
    )

    __all__ = [
        # Streaming (always available)
        "ProgressTracker",
        "StreamEvent",
        "EventType",
        "StreamingResearchContext",
        "stream_sse",
        "create_progress_tracker",
        "create_streaming_context",
        # App
        "create_app",
        "get_app",
        "FASTAPI_AVAILABLE",
        # Router
        "research_router",
        # WebSocket
        "WebSocketManager",
        # Middleware
        "RateLimitMiddleware",
        "APIKeyMiddleware",
        "RequestLoggingMiddleware",
        # Models
        "ResearchRequest",
        "ResearchResponse",
        "BatchRequest",
        "BatchResponse",
        "HealthResponse",
    ]
else:
    __all__ = [
        # Streaming (always available)
        "ProgressTracker",
        "StreamEvent",
        "EventType",
        "StreamingResearchContext",
        "stream_sse",
        "create_progress_tracker",
        "create_streaming_context",
        "FASTAPI_AVAILABLE",
    ]

    def create_app():
        raise ImportError("FastAPI not installed. Run: pip install fastapi uvicorn")

    def get_app():
        raise ImportError("FastAPI not installed. Run: pip install fastapi uvicorn")
