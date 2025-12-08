"""
Event Streaming - WebSocket, SSE, and Socket.IO implementations.

Provides real-time streaming to clients via:
- WebSocket connections
- Server-Sent Events (SSE)
- Socket.IO
"""

import asyncio
import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Set

from .stream_wrapper import StreamChunk


class EventType(str, Enum):
    """Types of stream events."""
    # Connection events
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"

    # Stream events
    STREAM_START = "stream_start"
    STREAM_CHUNK = "stream_chunk"
    STREAM_END = "stream_end"

    # Content events
    TOKEN = "token"
    MESSAGE = "message"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"

    # Agent events
    AGENT_START = "agent_start"
    AGENT_STEP = "agent_step"
    AGENT_END = "agent_end"

    # Status events
    THINKING = "thinking"
    PROGRESS = "progress"
    STATUS = "status"


@dataclass
class StreamEvent:
    """
    A stream event to be sent to clients.

    Attributes:
        event_type: Type of the event
        data: Event payload
        event_id: Unique event identifier
        timestamp: When the event was created
        metadata: Additional event metadata
    """
    event_type: EventType
    data: Any
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Optional fields for specific event types
    stream_id: Optional[str] = None
    chunk_index: Optional[int] = None
    is_final: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "stream_id": self.stream_id,
            "chunk_index": self.chunk_index,
            "is_final": self.is_final
        }

    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict(), default=str)

    def to_sse(self) -> str:
        """Convert event to SSE format."""
        lines = [
            f"id: {self.event_id}",
            f"event: {self.event_type.value}",
            f"data: {self.to_json()}"
        ]
        return "\n".join(lines) + "\n\n"

    @classmethod
    def from_chunk(cls, chunk: StreamChunk, stream_id: str) -> "StreamEvent":
        """Create event from StreamChunk."""
        return cls(
            event_type=EventType.STREAM_CHUNK,
            data={"content": chunk.content},
            stream_id=stream_id,
            chunk_index=chunk.index,
            is_final=chunk.is_final,
            metadata=chunk.metadata
        )


class EventStreamer(ABC):
    """
    Abstract base class for event streaming.

    Subclasses implement specific transport mechanisms.
    """

    def __init__(self, streamer_id: Optional[str] = None):
        self.streamer_id = streamer_id or str(uuid.uuid4())
        self._active = False
        self._event_queue: asyncio.Queue[StreamEvent] = asyncio.Queue()
        self._subscribers: Set[str] = set()
        self._event_history: List[StreamEvent] = []
        self._max_history = 1000

    @abstractmethod
    async def connect(self, client_id: str, **kwargs) -> bool:
        """Connect a client."""
        pass

    @abstractmethod
    async def disconnect(self, client_id: str) -> bool:
        """Disconnect a client."""
        pass

    @abstractmethod
    async def send_event(self, event: StreamEvent, client_id: Optional[str] = None) -> bool:
        """Send event to client(s)."""
        pass

    async def broadcast(self, event: StreamEvent) -> int:
        """Broadcast event to all connected clients."""
        sent = 0
        for client_id in self._subscribers:
            if await self.send_event(event, client_id):
                sent += 1
        return sent

    async def stream_chunks(
        self,
        chunks: AsyncIterator[StreamChunk],
        stream_id: str
    ) -> None:
        """
        Stream chunks as events.

        Args:
            chunks: Async iterator of StreamChunk
            stream_id: Identifier for this stream
        """
        # Send stream start event
        await self.broadcast(StreamEvent(
            event_type=EventType.STREAM_START,
            data={"stream_id": stream_id},
            stream_id=stream_id
        ))

        try:
            async for chunk in chunks:
                event = StreamEvent.from_chunk(chunk, stream_id)
                await self.broadcast(event)

            # Send stream end event
            await self.broadcast(StreamEvent(
                event_type=EventType.STREAM_END,
                data={"stream_id": stream_id},
                stream_id=stream_id,
                is_final=True
            ))

        except Exception as e:
            await self.broadcast(StreamEvent(
                event_type=EventType.ERROR,
                data={"error": str(e), "stream_id": stream_id},
                stream_id=stream_id
            ))
            raise

    def get_connected_clients(self) -> Set[str]:
        """Get set of connected client IDs."""
        return self._subscribers.copy()

    def get_event_history(self, limit: int = 100) -> List[StreamEvent]:
        """Get recent event history."""
        return self._event_history[-limit:]

    def _record_event(self, event: StreamEvent) -> None:
        """Record event in history."""
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]


class WebSocketStreamer(EventStreamer):
    """
    WebSocket-based event streaming.

    Usage:
        streamer = WebSocketStreamer()
        await streamer.connect(client_id, websocket=ws)
        await streamer.stream_chunks(chunks, "stream-123")
    """

    def __init__(self, streamer_id: Optional[str] = None):
        super().__init__(streamer_id)
        self._connections: Dict[str, Any] = {}  # client_id -> websocket

    async def connect(self, client_id: str, websocket: Any = None, **kwargs) -> bool:
        """Connect a WebSocket client."""
        if websocket is None:
            return False

        self._connections[client_id] = websocket
        self._subscribers.add(client_id)

        # Send connected event
        await self.send_event(
            StreamEvent(event_type=EventType.CONNECTED, data={"client_id": client_id}),
            client_id
        )
        return True

    async def disconnect(self, client_id: str) -> bool:
        """Disconnect a WebSocket client."""
        if client_id in self._connections:
            try:
                ws = self._connections[client_id]
                if hasattr(ws, 'close'):
                    await ws.close()
            except Exception:
                pass

            del self._connections[client_id]
            self._subscribers.discard(client_id)
            return True
        return False

    async def send_event(self, event: StreamEvent, client_id: Optional[str] = None) -> bool:
        """Send event via WebSocket."""
        self._record_event(event)

        if client_id:
            # Send to specific client
            if client_id in self._connections:
                try:
                    ws = self._connections[client_id]
                    if hasattr(ws, 'send_json'):
                        await ws.send_json(event.to_dict())
                    elif hasattr(ws, 'send'):
                        await ws.send(event.to_json())
                    return True
                except Exception:
                    return False
        else:
            # Broadcast to all
            return await self.broadcast(event) > 0

        return False


class SSEStreamer(EventStreamer):
    """
    Server-Sent Events (SSE) streaming.

    Usage:
        streamer = SSEStreamer()

        async def sse_endpoint(request):
            async def event_generator():
                async for event in streamer.get_events():
                    yield event.to_sse()
            return StreamingResponse(event_generator(), media_type="text/event-stream")
    """

    def __init__(self, streamer_id: Optional[str] = None):
        super().__init__(streamer_id)
        self._client_queues: Dict[str, asyncio.Queue[StreamEvent]] = {}

    async def connect(self, client_id: str, **kwargs) -> bool:
        """Register an SSE client."""
        self._client_queues[client_id] = asyncio.Queue()
        self._subscribers.add(client_id)

        # Queue connected event
        await self._client_queues[client_id].put(
            StreamEvent(event_type=EventType.CONNECTED, data={"client_id": client_id})
        )
        return True

    async def disconnect(self, client_id: str) -> bool:
        """Unregister an SSE client."""
        if client_id in self._client_queues:
            del self._client_queues[client_id]
            self._subscribers.discard(client_id)
            return True
        return False

    async def send_event(self, event: StreamEvent, client_id: Optional[str] = None) -> bool:
        """Queue event for SSE delivery."""
        self._record_event(event)

        if client_id:
            if client_id in self._client_queues:
                await self._client_queues[client_id].put(event)
                return True
            return False
        else:
            # Queue for all clients
            for queue in self._client_queues.values():
                await queue.put(event)
            return True

    async def get_events(self, client_id: str) -> AsyncIterator[StreamEvent]:
        """
        Get event stream for a client.

        This is an async generator that yields events as they arrive.
        """
        if client_id not in self._client_queues:
            await self.connect(client_id)

        queue = self._client_queues[client_id]

        try:
            while True:
                event = await queue.get()
                yield event

                if event.event_type == EventType.DISCONNECTED:
                    break
        finally:
            await self.disconnect(client_id)

    async def get_events_with_timeout(
        self,
        client_id: str,
        timeout: float = 30.0
    ) -> AsyncIterator[StreamEvent]:
        """Get events with heartbeat timeout."""
        if client_id not in self._client_queues:
            await self.connect(client_id)

        queue = self._client_queues[client_id]

        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=timeout)
                    yield event

                    if event.event_type == EventType.DISCONNECTED:
                        break
                except asyncio.TimeoutError:
                    # Send heartbeat/keep-alive
                    yield StreamEvent(
                        event_type=EventType.STATUS,
                        data={"status": "heartbeat"}
                    )
        finally:
            await self.disconnect(client_id)


class SocketIOStreamer(EventStreamer):
    """
    Socket.IO-based event streaming.

    Usage:
        streamer = SocketIOStreamer(sio=socketio_server)

        @sio.on('connect')
        async def on_connect(sid, environ):
            await streamer.connect(sid)

        await streamer.stream_chunks(chunks, "stream-123")
    """

    def __init__(
        self,
        sio: Any = None,
        namespace: str = "/",
        streamer_id: Optional[str] = None
    ):
        super().__init__(streamer_id)
        self._sio = sio
        self._namespace = namespace
        self._rooms: Dict[str, Set[str]] = {}  # room -> set of client_ids

    async def connect(self, client_id: str, room: Optional[str] = None, **kwargs) -> bool:
        """Connect a Socket.IO client."""
        self._subscribers.add(client_id)

        if room:
            if room not in self._rooms:
                self._rooms[room] = set()
            self._rooms[room].add(client_id)

            if self._sio and hasattr(self._sio, 'enter_room'):
                await self._sio.enter_room(client_id, room, namespace=self._namespace)

        # Emit connected event
        await self.send_event(
            StreamEvent(event_type=EventType.CONNECTED, data={"client_id": client_id}),
            client_id
        )
        return True

    async def disconnect(self, client_id: str) -> bool:
        """Disconnect a Socket.IO client."""
        self._subscribers.discard(client_id)

        # Remove from all rooms
        for room_clients in self._rooms.values():
            room_clients.discard(client_id)

        return True

    async def send_event(self, event: StreamEvent, client_id: Optional[str] = None) -> bool:
        """Send event via Socket.IO."""
        self._record_event(event)

        if not self._sio:
            return False

        try:
            event_name = event.event_type.value
            event_data = event.to_dict()

            if client_id:
                # Send to specific client
                await self._sio.emit(
                    event_name,
                    event_data,
                    to=client_id,
                    namespace=self._namespace
                )
            else:
                # Broadcast to all in namespace
                await self._sio.emit(
                    event_name,
                    event_data,
                    namespace=self._namespace
                )
            return True
        except Exception:
            return False

    async def send_to_room(self, event: StreamEvent, room: str) -> bool:
        """Send event to all clients in a room."""
        self._record_event(event)

        if not self._sio:
            return False

        try:
            await self._sio.emit(
                event.event_type.value,
                event.to_dict(),
                room=room,
                namespace=self._namespace
            )
            return True
        except Exception:
            return False

    def join_room(self, client_id: str, room: str) -> None:
        """Add client to a room."""
        if room not in self._rooms:
            self._rooms[room] = set()
        self._rooms[room].add(client_id)

    def leave_room(self, client_id: str, room: str) -> None:
        """Remove client from a room."""
        if room in self._rooms:
            self._rooms[room].discard(client_id)

    def get_room_clients(self, room: str) -> Set[str]:
        """Get all clients in a room."""
        return self._rooms.get(room, set()).copy()


def create_event_streamer(
    streamer_type: str = "websocket",
    **kwargs
) -> EventStreamer:
    """
    Factory function to create event streamer.

    Args:
        streamer_type: Type of streamer ("websocket", "sse", "socketio")
        **kwargs: Additional arguments for the streamer

    Returns:
        EventStreamer instance
    """
    if streamer_type == "websocket":
        return WebSocketStreamer(**kwargs)
    elif streamer_type == "sse":
        return SSEStreamer(**kwargs)
    elif streamer_type == "socketio":
        return SocketIOStreamer(**kwargs)
    else:
        raise ValueError(f"Unknown streamer type: {streamer_type}")
