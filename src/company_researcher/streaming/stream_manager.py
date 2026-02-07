"""
Stream Manager - Central management of streaming sessions.

Provides:
- Session management
- Display type configuration
- Stream lifecycle management
- Multi-stream coordination
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Set

from ..utils import get_logger

logger = get_logger(__name__)


def _utcnow() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


from .event_streaming import EventStreamer, EventType, StreamEvent, create_event_streamer
from .stream_wrapper import StreamChunk, StreamMetrics, StreamStatus, create_stream_wrapper


class DisplayType(str, Enum):
    """Display types for stream output."""

    BUBBLE = "bubble"  # Chat bubble display
    INLINE = "inline"  # Inline text display
    PANEL = "panel"  # Side panel display
    NOTIFICATION = "notification"  # Toast notification
    HIDDEN = "hidden"  # No display (background processing)
    MARKDOWN = "markdown"  # Markdown rendered display
    CODE = "code"  # Code block display


@dataclass
class StreamConfig:
    """Configuration for a stream session."""

    # Display settings
    display_type: DisplayType = DisplayType.INLINE
    show_typing_indicator: bool = True
    enable_markdown: bool = True
    highlight_code: bool = True

    # Buffering settings
    buffer_size: int = 100
    flush_interval: float = 0.1  # seconds
    batch_chunks: bool = False

    # Performance settings
    enable_metrics: bool = True
    track_tokens: bool = True
    measure_ttft: bool = True  # Time to first token

    # Behavior settings
    auto_scroll: bool = True
    allow_cancel: bool = True
    retry_on_error: bool = True
    max_retries: int = 3

    # Event settings
    emit_events: bool = True
    event_namespace: str = "/"


@dataclass
class StreamSession:
    """
    Represents an active streaming session.

    Tracks all state and metrics for a single stream.
    """

    session_id: str
    config: StreamConfig
    status: StreamStatus = StreamStatus.PENDING
    created_at: datetime = field(default_factory=_utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Content tracking
    content: str = ""
    chunks: List[StreamChunk] = field(default_factory=list)

    # Metrics
    metrics: Optional[StreamMetrics] = None

    # Error tracking
    errors: List[str] = field(default_factory=list)
    retry_count: int = 0

    # Display info
    display_type: DisplayType = DisplayType.INLINE
    display_id: Optional[str] = None

    # Callbacks
    _on_chunk_callbacks: List[Callable] = field(default_factory=list)
    _on_complete_callbacks: List[Callable] = field(default_factory=list)
    _on_error_callbacks: List[Callable] = field(default_factory=list)

    def add_chunk(self, chunk: StreamChunk) -> None:
        """Add a chunk to the session."""
        self.chunks.append(chunk)
        self.content += chunk.content

        for callback in self._on_chunk_callbacks:
            try:
                callback(chunk)
            except Exception as e:
                logger.warning(f"Session chunk callback error: {e}")

    def complete(self, metrics: Optional[StreamMetrics] = None) -> None:
        """Mark session as complete."""
        self.status = StreamStatus.COMPLETED
        self.completed_at = _utcnow()
        self.metrics = metrics

        for callback in self._on_complete_callbacks:
            try:
                callback(self)
            except Exception as e:
                logger.warning(f"Session completion callback error: {e}")

    def fail(self, error: str) -> None:
        """Mark session as failed."""
        self.status = StreamStatus.ERROR
        self.completed_at = _utcnow()
        self.errors.append(error)

        for callback in self._on_error_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.warning(f"Session error callback error: {e}")

    def on_chunk(self, callback: Callable[[StreamChunk], None]) -> "StreamSession":
        """Register chunk callback."""
        self._on_chunk_callbacks.append(callback)
        return self

    def on_complete(self, callback: Callable[["StreamSession"], None]) -> "StreamSession":
        """Register completion callback."""
        self._on_complete_callbacks.append(callback)
        return self

    def on_error(self, callback: Callable[[str], None]) -> "StreamSession":
        """Register error callback."""
        self._on_error_callbacks.append(callback)
        return self

    def get_duration(self) -> Optional[float]:
        """Get session duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "status": self.status.value,
            "content": self.content,
            "chunk_count": len(self.chunks),
            "display_type": self.display_type.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration": self.get_duration(),
            "errors": self.errors,
            "metrics": (
                {
                    "total_tokens": self.metrics.total_tokens if self.metrics else 0,
                    "time_to_first_token": (
                        self.metrics.time_to_first_token if self.metrics else None
                    ),
                    "tokens_per_second": self.metrics.tokens_per_second if self.metrics else None,
                }
                if self.metrics
                else None
            ),
        }


class StreamManager:
    """
    Central manager for all streaming operations.

    Usage:
        manager = StreamManager()

        # Create a stream session
        session = manager.create_session(
            display_type=DisplayType.BUBBLE,
            show_typing_indicator=True
        )

        # Stream LLM response
        async for chunk in manager.stream_llm(llm_response, session.session_id):
            print(chunk.content)

        # Get session metrics
        metrics = manager.get_session(session.session_id).metrics
    """

    def __init__(
        self,
        default_config: Optional[StreamConfig] = None,
        event_streamer: Optional[EventStreamer] = None,
    ):
        self._default_config = default_config or StreamConfig()
        self._sessions: Dict[str, StreamSession] = {}
        self._active_streams: Set[str] = set()
        self._event_streamer = event_streamer
        self._global_callbacks: Dict[str, List[Callable]] = {
            "on_session_start": [],
            "on_session_end": [],
            "on_chunk": [],
            "on_error": [],
        }

    def create_session(
        self,
        session_id: Optional[str] = None,
        config: Optional[StreamConfig] = None,
        display_type: Optional[DisplayType] = None,
        **kwargs,
    ) -> StreamSession:
        """
        Create a new streaming session.

        Args:
            session_id: Optional custom session ID
            config: Optional custom configuration
            display_type: Override display type
            **kwargs: Additional config overrides

        Returns:
            New StreamSession instance
        """
        session_id = session_id or str(uuid.uuid4())
        config = config or StreamConfig(**{**self._default_config.__dict__, **kwargs})

        if display_type:
            config.display_type = display_type

        session = StreamSession(
            session_id=session_id, config=config, display_type=config.display_type
        )

        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[StreamSession]:
        """Get a session by ID."""
        return self._sessions.get(session_id)

    def get_active_sessions(self) -> List[StreamSession]:
        """Get all active sessions."""
        return [s for s in self._sessions.values() if s.status == StreamStatus.STREAMING]

    def get_all_sessions(self) -> List[StreamSession]:
        """Get all sessions."""
        return list(self._sessions.values())

    async def stream_llm(
        self, llm_stream: Any, session_id: str, model: Optional[str] = None
    ) -> AsyncIterator[StreamChunk]:
        """
        Stream LLM response into a session.

        Args:
            llm_stream: The LLM stream to process
            session_id: Session to stream into
            model: Optional model name

        Yields:
            StreamChunk objects
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # Create wrapper
        wrapper = create_stream_wrapper(
            llm_stream, stream_type="llm", model=model, stream_id=session_id
        )

        # Start session
        session.status = StreamStatus.STREAMING
        session.started_at = _utcnow()
        self._active_streams.add(session_id)

        # Fire start callbacks
        for callback in self._global_callbacks["on_session_start"]:
            try:
                callback(session)
            except Exception as e:
                logger.warning(f"Session start callback error: {e}")

        # Send stream start event
        if self._event_streamer:
            await self._event_streamer.broadcast(
                StreamEvent(
                    event_type=EventType.STREAM_START,
                    data={"session_id": session_id, "display_type": session.display_type.value},
                    stream_id=session_id,
                )
            )

        try:
            async for chunk in wrapper:
                session.add_chunk(chunk)

                # Fire chunk callbacks
                for callback in self._global_callbacks["on_chunk"]:
                    try:
                        callback(chunk, session)
                    except Exception as e:
                        logger.warning(f"Global chunk callback error: {e}")

                # Send chunk event
                if self._event_streamer:
                    await self._event_streamer.broadcast(StreamEvent.from_chunk(chunk, session_id))

                yield chunk

            # Complete session
            session.complete(wrapper.get_metrics())
            self._active_streams.discard(session_id)

            # Fire end callbacks
            for callback in self._global_callbacks["on_session_end"]:
                try:
                    callback(session)
                except Exception as e:
                    logger.warning(f"Session end callback error: {e}")

            # Send stream end event
            if self._event_streamer:
                await self._event_streamer.broadcast(
                    StreamEvent(
                        event_type=EventType.STREAM_END,
                        data=session.to_dict(),
                        stream_id=session_id,
                        is_final=True,
                    )
                )

        except Exception as e:
            session.fail(str(e))
            self._active_streams.discard(session_id)

            # Fire error callbacks
            for callback in self._global_callbacks["on_error"]:
                try:
                    callback(e, session)
                except Exception as cb_error:
                    logger.warning(f"Global error callback error: {cb_error}")

            # Send error event
            if self._event_streamer:
                await self._event_streamer.broadcast(
                    StreamEvent(
                        event_type=EventType.ERROR,
                        data={"error": str(e), "session_id": session_id},
                        stream_id=session_id,
                    )
                )

            raise

    async def stream_tool(
        self, tool_stream: Any, session_id: str, tool_name: str
    ) -> AsyncIterator[StreamChunk]:
        """
        Stream tool execution into a session.

        Args:
            tool_stream: The tool stream to process
            session_id: Session to stream into
            tool_name: Name of the tool

        Yields:
            StreamChunk objects
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # Create wrapper
        wrapper = create_stream_wrapper(
            tool_stream, stream_type="tool", tool_name=tool_name, stream_id=session_id
        )

        # Start session
        session.status = StreamStatus.STREAMING
        session.started_at = _utcnow()
        self._active_streams.add(session_id)

        # Send tool call event
        if self._event_streamer:
            await self._event_streamer.broadcast(
                StreamEvent(
                    event_type=EventType.TOOL_CALL,
                    data={"session_id": session_id, "tool_name": tool_name},
                    stream_id=session_id,
                )
            )

        try:
            async for chunk in wrapper:
                session.add_chunk(chunk)

                # Send chunk event
                if self._event_streamer:
                    await self._event_streamer.broadcast(StreamEvent.from_chunk(chunk, session_id))

                yield chunk

            # Complete session
            session.complete(wrapper.get_metrics())
            self._active_streams.discard(session_id)

            # Send tool result event
            if self._event_streamer:
                await self._event_streamer.broadcast(
                    StreamEvent(
                        event_type=EventType.TOOL_RESULT,
                        data={
                            "session_id": session_id,
                            "tool_name": tool_name,
                            "result": session.content,
                        },
                        stream_id=session_id,
                        is_final=True,
                    )
                )

        except Exception as e:
            session.fail(str(e))
            self._active_streams.discard(session_id)

            if self._event_streamer:
                await self._event_streamer.broadcast(
                    StreamEvent(
                        event_type=EventType.ERROR,
                        data={"error": str(e), "session_id": session_id},
                        stream_id=session_id,
                    )
                )

            raise

    def cancel_session(self, session_id: str) -> bool:
        """Cancel an active session."""
        session = self.get_session(session_id)
        if session and session.status == StreamStatus.STREAMING:
            session.status = StreamStatus.CANCELLED
            session.completed_at = _utcnow()
            self._active_streams.discard(session_id)
            return True
        return False

    def on_session_start(self, callback: Callable[[StreamSession], None]) -> "StreamManager":
        """Register callback for session start."""
        self._global_callbacks["on_session_start"].append(callback)
        return self

    def on_session_end(self, callback: Callable[[StreamSession], None]) -> "StreamManager":
        """Register callback for session end."""
        self._global_callbacks["on_session_end"].append(callback)
        return self

    def on_chunk(self, callback: Callable[[StreamChunk, StreamSession], None]) -> "StreamManager":
        """Register callback for each chunk."""
        self._global_callbacks["on_chunk"].append(callback)
        return self

    def on_error(self, callback: Callable[[Exception, StreamSession], None]) -> "StreamManager":
        """Register callback for errors."""
        self._global_callbacks["on_error"].append(callback)
        return self

    def set_event_streamer(self, streamer: EventStreamer) -> None:
        """Set the event streamer for real-time events."""
        self._event_streamer = streamer

    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics."""
        sessions = list(self._sessions.values())
        completed = [s for s in sessions if s.status == StreamStatus.COMPLETED]

        total_tokens = sum(s.metrics.total_tokens for s in completed if s.metrics)

        avg_ttft = None
        ttft_values = [
            s.metrics.time_to_first_token
            for s in completed
            if s.metrics and s.metrics.time_to_first_token
        ]
        if ttft_values:
            avg_ttft = sum(ttft_values) / len(ttft_values)

        return {
            "total_sessions": len(sessions),
            "active_sessions": len(self._active_streams),
            "completed_sessions": len(completed),
            "failed_sessions": len([s for s in sessions if s.status == StreamStatus.ERROR]),
            "total_tokens": total_tokens,
            "average_time_to_first_token": avg_ttft,
        }

    def cleanup_old_sessions(self, max_age_seconds: float = 3600) -> int:
        """Remove sessions older than max_age_seconds."""
        now = _utcnow()
        removed = 0

        for session_id in list(self._sessions.keys()):
            session = self._sessions[session_id]
            if session.status not in (StreamStatus.PENDING, StreamStatus.STREAMING):
                age = (now - session.created_at).total_seconds()
                if age > max_age_seconds:
                    del self._sessions[session_id]
                    removed += 1

        return removed


def create_stream_manager(
    event_streamer_type: Optional[str] = None,
    default_config: Optional[StreamConfig] = None,
    **streamer_kwargs,
) -> StreamManager:
    """
    Factory function to create a StreamManager.

    Args:
        event_streamer_type: Type of event streamer ("websocket", "sse", "socketio", None)
        default_config: Default stream configuration
        **streamer_kwargs: Arguments for the event streamer

    Returns:
        Configured StreamManager instance
    """
    event_streamer = None
    if event_streamer_type:
        event_streamer = create_event_streamer(event_streamer_type, **streamer_kwargs)

    return StreamManager(default_config=default_config, event_streamer=event_streamer)
