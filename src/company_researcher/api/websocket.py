"""
WebSocket Manager (Phase 18.3).

Real-time updates via WebSocket:
- Task progress updates
- Research completion notifications
- Live agent status
"""

import re
import threading
from typing import Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import logging

try:
    from fastapi import WebSocket
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    class WebSocket:
        pass


def _utcnow() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


# ============================================================================
# Input Validation
# ============================================================================

# Valid message types
VALID_MESSAGE_TYPES = {"subscribe", "unsubscribe", "ping", "list_subscriptions"}

# Task ID pattern (alphanumeric with underscores)
TASK_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,100}$')

# Maximum message size (10KB)
MAX_MESSAGE_SIZE = 10 * 1024

# Maximum subscriptions per connection
MAX_SUBSCRIPTIONS_PER_CONNECTION = 50


@dataclass
class ValidationResult:
    """Result of message validation."""
    valid: bool
    error: Optional[str] = None
    sanitized: Optional[Dict[str, Any]] = None


def validate_websocket_message(message: Any, max_size: int = MAX_MESSAGE_SIZE) -> ValidationResult:
    """
    Validate incoming WebSocket message.

    Args:
        message: Raw message data
        max_size: Maximum message size in bytes

    Returns:
        ValidationResult with valid flag and sanitized data
    """
    # Check if message is a dict
    if not isinstance(message, dict):
        return ValidationResult(valid=False, error="Message must be a JSON object")

    # Check message size (approximate)
    try:
        message_str = json.dumps(message)
        if len(message_str) > max_size:
            return ValidationResult(valid=False, error=f"Message too large (max {max_size} bytes)")
    except (TypeError, ValueError):
        return ValidationResult(valid=False, error="Invalid message format")

    # Validate message type
    msg_type = message.get("type")
    if not msg_type:
        return ValidationResult(valid=False, error="Missing 'type' field")

    if not isinstance(msg_type, str):
        return ValidationResult(valid=False, error="'type' must be a string")

    if msg_type not in VALID_MESSAGE_TYPES:
        return ValidationResult(
            valid=False,
            error=f"Invalid message type. Allowed: {', '.join(VALID_MESSAGE_TYPES)}"
        )

    # Validate task_id if present
    task_id = message.get("task_id")
    if task_id is not None:
        if not isinstance(task_id, str):
            return ValidationResult(valid=False, error="'task_id' must be a string")

        if not TASK_ID_PATTERN.match(task_id):
            return ValidationResult(
                valid=False,
                error="Invalid task_id format (alphanumeric, underscore, hyphen only, max 100 chars)"
            )

    # Return sanitized message with only allowed fields
    sanitized = {"type": msg_type}
    if task_id:
        sanitized["task_id"] = task_id

    return ValidationResult(valid=True, sanitized=sanitized)


# ============================================================================
# Rate Limiting for WebSocket
# ============================================================================

@dataclass
class ConnectionRateState:
    """Rate limiting state for a connection."""
    message_count: int = 0
    window_start: datetime = field(default_factory=_utcnow)
    violations: int = 0


class WebSocketRateLimiter:
    """
    Rate limiter for WebSocket connections.

    Limits:
    - Messages per second per connection
    - Total connections per IP (if available)
    """

    def __init__(
        self,
        messages_per_second: int = 10,
        max_connections: int = 100,
        ban_threshold: int = 5
    ):
        self.messages_per_second = messages_per_second
        self.max_connections = max_connections
        self.ban_threshold = ban_threshold
        self._connection_states: Dict[str, ConnectionRateState] = {}
        self._banned_connections: Set[str] = set()
        self._lock = threading.RLock()
        self._logger = logging.getLogger("api.websocket.ratelimit")

    def is_connection_allowed(self) -> bool:
        """Check if a new connection is allowed."""
        with self._lock:
            return len(self._connection_states) < self.max_connections

    def register_connection(self, connection_id: str) -> bool:
        """Register a new connection for rate limiting."""
        with self._lock:
            if connection_id in self._banned_connections:
                return False
            if len(self._connection_states) >= self.max_connections:
                return False
            self._connection_states[connection_id] = ConnectionRateState()
            return True

    def unregister_connection(self, connection_id: str) -> None:
        """Unregister a connection."""
        with self._lock:
            self._connection_states.pop(connection_id, None)

    def is_message_allowed(self, connection_id: str) -> tuple[bool, Optional[str]]:
        """
        Check if a message is allowed for this connection.

        Returns:
            Tuple of (allowed, error_message)
        """
        with self._lock:
            if connection_id in self._banned_connections:
                return False, "Connection is banned due to rate limit violations"

            state = self._connection_states.get(connection_id)
            if not state:
                return False, "Connection not registered"

            now = _utcnow()
            elapsed = (now - state.window_start).total_seconds()

            # Reset window if more than 1 second has passed
            if elapsed >= 1.0:
                state.message_count = 0
                state.window_start = now

            # Check rate limit
            if state.message_count >= self.messages_per_second:
                state.violations += 1

                # Ban if too many violations
                if state.violations >= self.ban_threshold:
                    self._banned_connections.add(connection_id)
                    self._logger.warning(f"Connection {connection_id} banned for rate limit violations")
                    return False, "Connection banned due to repeated rate limit violations"

                return False, f"Rate limit exceeded ({self.messages_per_second}/sec)"

            state.message_count += 1
            return True, None

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics."""
        with self._lock:
            return {
                "active_connections": len(self._connection_states),
                "banned_connections": len(self._banned_connections),
                "max_connections": self.max_connections
            }


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

    def __init__(
        self,
        heartbeat_interval: int = 30,
        messages_per_second: int = 10,
        max_connections: int = 100
    ):
        """
        Initialize WebSocket manager.

        Args:
            heartbeat_interval: Seconds between heartbeats
            messages_per_second: Rate limit for messages per connection
            max_connections: Maximum total connections
        """
        self._connections: Dict[str, WebSocket] = {}
        self._subscriptions: Dict[str, Set[str]] = {}  # task_id -> connection_ids
        self._connection_tasks: Dict[str, Set[str]] = {}  # connection_id -> task_ids
        self._heartbeat_interval = heartbeat_interval
        self._logger = logging.getLogger("api.websocket")
        self._connection_counter = 0

        # Rate limiting
        self._rate_limiter = WebSocketRateLimiter(
            messages_per_second=messages_per_second,
            max_connections=max_connections
        )

    async def connect(self, websocket: WebSocket) -> Optional[str]:
        """
        Accept new WebSocket connection.

        Returns:
            Connection ID or None if connection rejected
        """
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI required for WebSocket support")

        # Check connection limit
        if not self._rate_limiter.is_connection_allowed():
            self._logger.warning("Connection rejected: max connections reached")
            await websocket.close(code=1013, reason="Max connections reached")
            return None

        await websocket.accept()

        self._connection_counter += 1
        connection_id = f"ws_{self._connection_counter}"

        # Register with rate limiter
        if not self._rate_limiter.register_connection(connection_id):
            await websocket.close(code=1013, reason="Connection not allowed")
            return None

        self._connections[connection_id] = websocket
        self._connection_tasks[connection_id] = set()

        self._logger.info(f"WebSocket connected: {connection_id}")

        # Send welcome message
        await self._send_to_connection(connection_id, {
            "type": "connected",
            "connection_id": connection_id,
            "timestamp": _utcnow().isoformat()
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

            # Unregister from rate limiter
            self._rate_limiter.unregister_connection(connection_id)

            self._logger.info(f"WebSocket disconnected: {connection_id}")

    async def handle_message(
        self,
        websocket: WebSocket,
        message: Dict[str, Any]
    ):
        """
        Handle incoming WebSocket message with validation and rate limiting.

        Message types:
        - subscribe: Subscribe to task updates
        - unsubscribe: Unsubscribe from task
        - ping: Heartbeat ping
        - list_subscriptions: List current subscriptions
        """
        connection_id = self._get_connection_id(websocket)

        if not connection_id:
            return

        # Check rate limit
        allowed, error = self._rate_limiter.is_message_allowed(connection_id)
        if not allowed:
            await self._send_to_connection(connection_id, {
                "type": "error",
                "error": error,
                "timestamp": _utcnow().isoformat()
            })
            return

        # Validate message
        validation = validate_websocket_message(message)
        if not validation.valid:
            await self._send_to_connection(connection_id, {
                "type": "error",
                "error": validation.error,
                "timestamp": _utcnow().isoformat()
            })
            self._logger.warning(f"Invalid message from {connection_id}: {validation.error}")
            return

        # Use sanitized message
        sanitized = validation.sanitized
        msg_type = sanitized.get("type")

        if msg_type == "subscribe":
            task_id = sanitized.get("task_id")
            if task_id:
                await self._subscribe(connection_id, task_id)

        elif msg_type == "unsubscribe":
            task_id = sanitized.get("task_id")
            if task_id:
                await self._unsubscribe(connection_id, task_id)

        elif msg_type == "ping":
            await self._send_to_connection(connection_id, {
                "type": "pong",
                "timestamp": _utcnow().isoformat()
            })

        elif msg_type == "list_subscriptions":
            tasks = list(self._connection_tasks.get(connection_id, set()))
            await self._send_to_connection(connection_id, {
                "type": "subscriptions",
                "task_ids": tasks
            })

    async def _subscribe(self, connection_id: str, task_id: str):
        """Subscribe connection to task updates."""
        # Check subscription limit
        current_subscriptions = self._connection_tasks.get(connection_id, set())
        if len(current_subscriptions) >= MAX_SUBSCRIPTIONS_PER_CONNECTION:
            await self._send_to_connection(connection_id, {
                "type": "error",
                "error": f"Max subscriptions reached ({MAX_SUBSCRIPTIONS_PER_CONNECTION})",
                "timestamp": _utcnow().isoformat()
            })
            return

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
            "timestamp": _utcnow().isoformat(),
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
        message["timestamp"] = _utcnow().isoformat()

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
            "tasks_being_watched": len(self._subscriptions),
            "rate_limiter": self._rate_limiter.get_stats()
        }


# ============================================================================
# Factory Function
# ============================================================================

def create_websocket_manager(
    heartbeat_interval: int = 30,
    messages_per_second: int = 10,
    max_connections: int = 100
) -> WebSocketManager:
    """
    Create a WebSocket manager instance.

    Args:
        heartbeat_interval: Seconds between heartbeats
        messages_per_second: Rate limit for messages per connection
        max_connections: Maximum total connections

    Returns:
        Configured WebSocketManager instance
    """
    return WebSocketManager(
        heartbeat_interval=heartbeat_interval,
        messages_per_second=messages_per_second,
        max_connections=max_connections
    )
