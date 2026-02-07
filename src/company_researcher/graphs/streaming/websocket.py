"""
WebSocket Integration - Phase 13

Provides WebSocket support for real-time research streaming.

Features:
- FastAPI WebSocket router
- Connection management
- Broadcast to multiple clients
- Reconnection support

Usage:
    from fastapi import FastAPI
    from company_researcher.graphs.streaming import create_websocket_router

    app = FastAPI()
    ws_router = create_websocket_router()
    app.include_router(ws_router, prefix="/ws")

    # Client connects to: ws://localhost:8000/ws/research/Tesla
"""

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from ...utils import get_logger
from .event_stream import StreamConfig, StreamEvent, stream_research

logger = get_logger(__name__)


@dataclass
class WebSocketConnection:
    """Represents a WebSocket connection."""

    connection_id: str
    company_name: Optional[str] = None
    is_active: bool = True


class WebSocketManager:
    """
    Manage WebSocket connections for research streaming.

    Features:
    - Track active connections
    - Broadcast events to all connected clients
    - Handle disconnections gracefully
    """

    def __init__(self):
        self.active_connections: Dict[str, Any] = {}  # connection_id -> websocket
        self.company_subscriptions: Dict[str, Set[str]] = {}  # company -> connection_ids

    async def connect(self, websocket: Any, connection_id: str) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        logger.info(f"[WS] Connected: {connection_id}")

    def disconnect(self, connection_id: str) -> None:
        """Remove a WebSocket connection."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

        # Remove from all subscriptions
        for company, subscribers in self.company_subscriptions.items():
            subscribers.discard(connection_id)

        logger.info(f"[WS] Disconnected: {connection_id}")

    def subscribe(self, connection_id: str, company_name: str) -> None:
        """Subscribe connection to company research updates."""
        if company_name not in self.company_subscriptions:
            self.company_subscriptions[company_name] = set()
        self.company_subscriptions[company_name].add(connection_id)
        logger.info(f"[WS] {connection_id} subscribed to {company_name}")

    async def send_personal_message(self, message: Dict[str, Any], connection_id: str) -> None:
        """Send message to specific connection."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"[WS] Failed to send to {connection_id}: {e}")
                self.disconnect(connection_id)

    async def broadcast_to_company(self, message: Dict[str, Any], company_name: str) -> None:
        """Broadcast message to all connections subscribed to a company."""
        if company_name not in self.company_subscriptions:
            return

        disconnected = []
        for connection_id in self.company_subscriptions[company_name]:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"[WS] Failed to broadcast to {connection_id}: {e}")
                    disconnected.append(connection_id)

        # Clean up disconnected
        for conn_id in disconnected:
            self.disconnect(conn_id)

    async def broadcast_all(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all active connections."""
        disconnected = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"[WS] Failed to broadcast to {connection_id}: {e}")
                disconnected.append(connection_id)

        for conn_id in disconnected:
            self.disconnect(conn_id)


# Global manager instance
ws_manager = WebSocketManager()


async def research_websocket_handler(
    websocket: Any,
    company_name: str,
    connection_id: Optional[str] = None,
) -> None:
    """
    Handle WebSocket connection for research streaming.

    This function:
    1. Accepts the WebSocket connection
    2. Starts research workflow
    3. Streams events to the client
    4. Handles disconnection

    Args:
        websocket: FastAPI WebSocket instance
        company_name: Company to research
        connection_id: Optional connection identifier
    """
    import uuid

    if connection_id is None:
        connection_id = f"ws_{uuid.uuid4().hex[:8]}"

    await ws_manager.connect(websocket, connection_id)
    ws_manager.subscribe(connection_id, company_name)

    try:
        # Send initial message
        await websocket.send_json(
            {
                "type": "connected",
                "connection_id": connection_id,
                "company_name": company_name,
                "message": f"Starting research for {company_name}",
            }
        )

        # Stream research events
        async for event in stream_research(company_name):
            await websocket.send_json(event.to_dict())

            # Small delay to prevent overwhelming client
            await asyncio.sleep(0.05)

    except Exception as e:
        logger.error(f"[WS] Error in handler: {e}")
        try:
            await websocket.send_json(
                {
                    "type": "error",
                    "error": str(e),
                }
            )
        except Exception:
            pass  # Connection might be closed

    finally:
        ws_manager.disconnect(connection_id)


def create_websocket_router():
    """
    Create FastAPI router with WebSocket endpoints.

    Returns:
        APIRouter with WebSocket routes

    Usage:
        from fastapi import FastAPI
        from company_researcher.graphs.streaming import create_websocket_router

        app = FastAPI()
        app.include_router(create_websocket_router(), prefix="/ws")
    """
    try:
        from fastapi import APIRouter, WebSocket, WebSocketDisconnect
    except ImportError:
        logger.error("[WS] FastAPI not installed. Install with: pip install fastapi")
        raise ImportError("FastAPI required for WebSocket support")

    router = APIRouter()

    @router.websocket("/research/{company_name}")
    async def websocket_research(websocket: WebSocket, company_name: str):
        """
        WebSocket endpoint for research streaming.

        Connect to: ws://host/ws/research/{company_name}

        Events sent:
        - connected: Initial connection confirmed
        - workflow_start: Research begins
        - node_start: Node begins processing
        - node_complete: Node finishes
        - state_update: State changes
        - workflow_complete: Research finished
        - workflow_error: Error occurred
        """
        import uuid

        connection_id = f"ws_{uuid.uuid4().hex[:8]}"

        await ws_manager.connect(websocket, connection_id)
        ws_manager.subscribe(connection_id, company_name)

        try:
            await websocket.send_json(
                {
                    "type": "connected",
                    "connection_id": connection_id,
                    "company_name": company_name,
                }
            )

            # Start research and stream
            async for event in stream_research(company_name):
                await websocket.send_json(event.to_dict())
                await asyncio.sleep(0.01)

        except WebSocketDisconnect:
            logger.info(f"[WS] Client disconnected: {connection_id}")
        except Exception as e:
            logger.error(f"[WS] Error: {e}")
            try:
                await websocket.send_json({"type": "error", "error": str(e)})
            except Exception:
                pass
        finally:
            ws_manager.disconnect(connection_id)

    @router.websocket("/status")
    async def websocket_status(websocket: WebSocket):
        """
        WebSocket endpoint for status updates.

        Sends periodic status of active research.
        """
        import uuid

        connection_id = f"status_{uuid.uuid4().hex[:8]}"

        await ws_manager.connect(websocket, connection_id)

        try:
            await websocket.send_json(
                {
                    "type": "connected",
                    "connection_id": connection_id,
                }
            )

            # Keep connection alive with periodic status
            while True:
                status = {
                    "type": "status",
                    "active_connections": len(ws_manager.active_connections),
                    "subscriptions": {
                        k: len(v) for k, v in ws_manager.company_subscriptions.items()
                    },
                }
                await websocket.send_json(status)
                await asyncio.sleep(5)  # Status every 5 seconds

        except WebSocketDisconnect:
            logger.info(f"[WS] Status client disconnected")
        except Exception as e:
            logger.error(f"[WS] Status error: {e}")
        finally:
            ws_manager.disconnect(connection_id)

    return router


# ============================================================================
# Server-Sent Events (SSE) Support
# ============================================================================


async def sse_research_generator(company_name: str):
    """
    Generator for Server-Sent Events streaming.

    Usage with FastAPI:
        from fastapi.responses import StreamingResponse

        @app.get("/sse/research/{company_name}")
        async def sse_research(company_name: str):
            return StreamingResponse(
                sse_research_generator(company_name),
                media_type="text/event-stream"
            )
    """
    async for event in stream_research(company_name):
        data = json.dumps(event.to_dict())
        yield f"event: {event.type}\ndata: {data}\n\n"


def create_sse_router():
    """
    Create FastAPI router with SSE endpoints.

    Returns:
        APIRouter with SSE routes
    """
    try:
        from fastapi import APIRouter
        from fastapi.responses import StreamingResponse
    except ImportError:
        logger.error("[SSE] FastAPI not installed")
        raise ImportError("FastAPI required for SSE support")

    router = APIRouter()

    @router.get("/research/{company_name}")
    async def sse_research(company_name: str):
        """
        Server-Sent Events endpoint for research streaming.

        Connect to: GET /sse/research/{company_name}

        Response is text/event-stream with events:
        - workflow_start
        - node_complete
        - state_update
        - workflow_complete
        - workflow_error
        """
        return StreamingResponse(
            sse_research_generator(company_name),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    return router
