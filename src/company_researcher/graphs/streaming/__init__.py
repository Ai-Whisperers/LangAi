"""
Streaming Package - Phase 13: Real-time Updates

This package provides streaming capabilities for LangGraph workflows:
- Stream workflow events (node completion, state updates)
- Stream LLM token output in real-time
- WebSocket integration for web applications
- Server-Sent Events (SSE) support

Usage:
    from company_researcher.graphs.streaming import (
        stream_research,
        stream_research_events,
        create_streaming_endpoint,
    )

    # Stream events
    async for event in stream_research("Tesla"):
        print(f"Node: {event['node']}, Status: {event['status']}")

    # Stream with token output
    async for event in stream_research_events("Tesla", include_tokens=True):
        if event['type'] == 'token':
            print(event['content'], end='')
"""

from .event_stream import (
    stream_research,
    stream_research_events,
    StreamEvent,
    StreamConfig,
)
from .websocket import (
    create_websocket_router,
    WebSocketManager,
    research_websocket_handler,
)

__all__ = [
    # Event streaming
    "stream_research",
    "stream_research_events",
    "StreamEvent",
    "StreamConfig",
    # WebSocket
    "create_websocket_router",
    "WebSocketManager",
    "research_websocket_handler",
]
