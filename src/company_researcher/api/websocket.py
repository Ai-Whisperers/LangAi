"""
WebSocket Manager (Phase 18.3).

Real-time updates via WebSocket:
- Task progress updates
- Research completion notifications
- Live agent status
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import asyncio
import json
import logging

try:
    from fastapi import WebSocket, WebSocketDisconnect
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    class WebSocket:
        pass


# ============================================================================
# WebSocket Manager
# ============================================================================

class WebSocketManager:
    """
    Manager for WebSocket connections.

    Features:
    - Connection management
    - Task subscription
    - Broadcast capabilities
    - Heartbeat monitoring

    Usage:
        manager = WebSocketManager()

        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await manager.connect(websocket)
            try:
                while True:
                    data = await websocket.receive_json()
                    await manager.handle_message(websocket, data)
            except WebSocketDisconnect:
                manager.disconnect(websocket)

        # Send update from research task
        await manager.send_task_update(task_id, {"status": "running"})
    """

    def __init__(self, heartbeat_interval: int = 30):
        """
        Initialize WebSocket manager.

        Args:
            heartbeat_interval: Seconds between heartbeats
        """
        self._connections: Dict[str, WebSocket] = {}
        self._subscriptions: Dict[str, Set[str]] = {}  # task_id -> connection_ids
        self._connection_tasks: Dict[str, Set[str]] = {}  # connection_id -> task_ids
        self._heartbeat_interval = heartbeat_interval
        self._logger = logging.getLogger("api.websocket")
        self._connection_counter = 0

    async def connect(self, websocket: WebSocket) -> str:
        """
        Accept new WebSocket connection.

        Returns:
            Connection ID
        """
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI required for WebSocket support")

        await websocket.accept()

        self._connection_counter += 1
        connection_id = f"ws_{self._connection_counter}"

        self._connections[connection_id] = websocket
        self._connection_tasks[connection_id] = set()

        self._logger.info(f"WebSocket connected: {connection_id}")

        # Send welcome message
        await self._send_to_connection(connection_id, {
            "type": "connected",
            "connection_id": connection_id,
            "timestamp": datetime.now().isoformat()
        })

        return connection_id

    def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection."""
        # Find connection ID
        connection_id = None
        for cid, ws in self._connections.items():
            if ws == websocket:
                connection_id = cid
                break

        if connection_id:
            # Clean up subscriptions
            for task_id in self._connection_tasks.get(connection_id, set()):
                if task_id in self._subscriptions:
                    self._subscriptions[task_id].discard(connection_id)

            # Remove connection
            self._connections.pop(connection_id, None)
            self._connection_tasks.pop(connection_id, None)

            self._logger.info(f"WebSocket disconnected: {connection_id}")

    async def handle_message(
        self,
        websocket: WebSocket,
        message: Dict[str, Any]
    ):
        """
        Handle incoming WebSocket message.

        Message types:
        - subscribe: Subscribe to task updates
        - unsubscribe: Unsubscribe from task
        - ping: Heartbeat ping
        """
        msg_type = message.get("type")
        connection_id = self._get_connection_id(websocket)

        if not connection_id:
            return

        if msg_type == "subscribe":
            task_id = message.get("task_id")
            if task_id:
                await self._subscribe(connection_id, task_id)

        elif msg_type == "unsubscribe":
            task_id = message.get("task_id")
            if task_id:
                await self._unsubscribe(connection_id, task_id)

        elif msg_type == "ping":
            await self._send_to_connection(connection_id, {
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            })

        elif msg_type == "list_subscriptions":
            tasks = list(self._connection_tasks.get(connection_id, set()))
            await self._send_to_connection(connection_id, {
                "type": "subscriptions",
                "task_ids": tasks
            })

    async def _subscribe(self, connection_id: str, task_id: str):
        """Subscribe connection to task updates."""
        if task_id not in self._subscriptions:
            self._subscriptions[task_id] = set()

        self._subscriptions[task_id].add(connection_id)
        self._connection_tasks[connection_id].add(task_id)

        await self._send_to_connection(connection_id, {
            "type": "subscribed",
            "task_id": task_id
        })

        self._logger.debug(f"{connection_id} subscribed to {task_id}")

    async def _unsubscribe(self, connection_id: str, task_id: str):
        """Unsubscribe connection from task updates."""
        if task_id in self._subscriptions:
            self._subscriptions[task_id].discard(connection_id)

        if connection_id in self._connection_tasks:
            self._connection_tasks[connection_id].discard(task_id)

        await self._send_to_connection(connection_id, {
            "type": "unsubscribed",
            "task_id": task_id
        })

    # ==========================================================================
    # Sending Updates
    # ==========================================================================

    async def send_task_update(
        self,
        task_id: str,
        data: Dict[str, Any],
        update_type: str = "update"
    ):
        """
        Send update to all subscribers of a task.

        Args:
            task_id: Task identifier
            data: Update data
            update_type: Type of update (progress, status, completed, error)
        """
        subscribers = self._subscriptions.get(task_id, set())

        message = {
            "type": update_type,
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }

        for connection_id in subscribers:
            await self._send_to_connection(connection_id, message)

    async def send_progress(
        self,
        task_id: str,
        progress: float,
        stage: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Send progress update."""
        await self.send_task_update(task_id, {
            "progress": progress,
            "stage": stage,
            "details": details or {}
        }, update_type="progress")

    async def send_status_change(
        self,
        task_id: str,
        status: str,
        message: Optional[str] = None
    ):
        """Send status change update."""
        await self.send_task_update(task_id, {
            "status": status,
            "message": message
        }, update_type="status")

    async def send_completion(
        self,
        task_id: str,
        result: Dict[str, Any]
    ):
        """Send task completion notification."""
        await self.send_task_update(task_id, result, update_type="completed")

        # Clean up subscriptions
        self._subscriptions.pop(task_id, None)

    async def send_error(
        self,
        task_id: str,
        error: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Send error notification."""
        await self.send_task_update(task_id, {
            "error": error,
            "details": details or {}
        }, update_type="error")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connections."""
        message["timestamp"] = datetime.now().isoformat()

        for connection_id in list(self._connections.keys()):
            await self._send_to_connection(connection_id, message)

    async def _send_to_connection(
        self,
        connection_id: str,
        message: Dict[str, Any]
    ):
        """Send message to specific connection."""
        websocket = self._connections.get(connection_id)
        if websocket:
            try:
                await websocket.send_json(message)
            except Exception as e:
                self._logger.error(f"Failed to send to {connection_id}: {e}")
                # Remove dead connection
                self._connections.pop(connection_id, None)

    def _get_connection_id(self, websocket: WebSocket) -> Optional[str]:
        """Get connection ID for websocket."""
        for cid, ws in self._connections.items():
            if ws == websocket:
                return cid
        return None

    # ==========================================================================
    # Statistics
    # ==========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket statistics."""
        return {
            "total_connections": len(self._connections),
            "active_subscriptions": sum(len(s) for s in self._subscriptions.values()),
            "tasks_being_watched": len(self._subscriptions)
        }


# ============================================================================
# Factory Function
# ============================================================================

def create_websocket_manager(heartbeat_interval: int = 30) -> WebSocketManager:
    """Create a WebSocket manager instance."""
    return WebSocketManager(heartbeat_interval=heartbeat_interval)
