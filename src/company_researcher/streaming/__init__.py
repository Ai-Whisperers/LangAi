"""
Streaming Module for Company Researcher.

Real-time streaming implementations for enhanced UX:
- Stream wrappers for unified interface
- Chunk processing and accumulation
- Event streaming (WebSocket, SSE, Socket.IO)
- Performance metrics (TTFT, throughput)
"""

from .stream_wrapper import (
    BaseStreamWrapper,
    LLMStreamWrapper,
    ToolStreamWrapper,
    StreamChunk,
    StreamMetrics,
    create_stream_wrapper,
)

from .chunk_processor import (
    ChunkProcessor,
    ChunkBuffer,
    ChunkAggregator,
    process_chunks,
    accumulate_response,
)

from .event_streaming import (
    EventStreamer,
    StreamEvent,
    EventType,
    WebSocketStreamer,
    SSEStreamer,
    SocketIOStreamer,
    create_event_streamer,
)

from .stream_manager import (
    StreamManager,
    StreamSession,
    StreamConfig,
    DisplayType,
    create_stream_manager,
)

__all__ = [
    # Stream Wrapper
    "BaseStreamWrapper",
    "LLMStreamWrapper",
    "ToolStreamWrapper",
    "StreamChunk",
    "StreamMetrics",
    "create_stream_wrapper",
    # Chunk Processor
    "ChunkProcessor",
    "ChunkBuffer",
    "ChunkAggregator",
    "process_chunks",
    "accumulate_response",
    # Event Streaming
    "EventStreamer",
    "StreamEvent",
    "EventType",
    "WebSocketStreamer",
    "SSEStreamer",
    "SocketIOStreamer",
    "create_event_streamer",
    # Stream Manager
    "StreamManager",
    "StreamSession",
    "StreamConfig",
    "DisplayType",
    "create_stream_manager",
]
