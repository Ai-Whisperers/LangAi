"""
Stream Wrapper Pattern - Unified streaming interface.

Provides consistent streaming interface across different sources:
- LLM responses
- Tool executions
- Agent outputs
"""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, TypeVar, Generic
from ..utils import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


def _utcnow() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class StreamStatus(str, Enum):
    """Status of a stream."""
    PENDING = "pending"
    STREAMING = "streaming"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class StreamChunk:
    """Individual chunk from a stream."""
    id: str
    content: str
    index: int
    timestamp: datetime = field(default_factory=_utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_final: bool = False

    # Token information
    token_count: Optional[int] = None
    cumulative_tokens: Optional[int] = None

    # Source information
    source_type: Optional[str] = None
    model: Optional[str] = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class StreamMetrics:
    """Performance metrics for streaming."""
    stream_id: str
    start_time: datetime
    end_time: Optional[datetime] = None

    # Time metrics
    time_to_first_token: Optional[float] = None  # seconds
    total_duration: Optional[float] = None  # seconds

    # Token metrics
    total_tokens: int = 0
    tokens_per_second: float = 0.0

    # Chunk metrics
    total_chunks: int = 0
    average_chunk_size: float = 0.0

    # Error tracking
    errors: List[str] = field(default_factory=list)
    retries: int = 0

    def calculate_final_metrics(self) -> None:
        """Calculate final metrics when stream completes."""
        if self.end_time and self.start_time:
            self.total_duration = (self.end_time - self.start_time).total_seconds()
            if self.total_duration > 0:
                self.tokens_per_second = self.total_tokens / self.total_duration
            if self.total_chunks > 0:
                self.average_chunk_size = self.total_tokens / self.total_chunks


class BaseStreamWrapper(ABC, Generic[T]):
    """
    Base class for stream wrappers providing unified interface.

    Usage:
        wrapper = LLMStreamWrapper(llm_response)
        async for chunk in wrapper:
            print(chunk.content)

        metrics = wrapper.get_metrics()
    """

    def __init__(self, stream_id: Optional[str] = None):
        self.stream_id = stream_id or str(uuid.uuid4())
        self.status = StreamStatus.PENDING
        self._metrics = StreamMetrics(
            stream_id=self.stream_id,
            start_time=_utcnow()
        )
        self._chunks: List[StreamChunk] = []
        self._callbacks: List[Callable[[StreamChunk], None]] = []
        self._error_callbacks: List[Callable[[Exception], None]] = []
        self._complete_callbacks: List[Callable[[StreamMetrics], None]] = []
        self._chunk_index = 0
        self._accumulated_content = ""
        self._first_token_received = False

    @abstractmethod
    async def _get_chunks(self) -> AsyncIterator[T]:
        """Get raw chunks from the underlying source."""

    @abstractmethod
    def _process_chunk(self, raw_chunk: T) -> StreamChunk:
        """Process raw chunk into StreamChunk."""

    def on_chunk(self, callback: Callable[[StreamChunk], None]) -> "BaseStreamWrapper":
        """Register callback for each chunk."""
        self._callbacks.append(callback)
        return self

    def on_error(self, callback: Callable[[Exception], None]) -> "BaseStreamWrapper":
        """Register callback for errors."""
        self._error_callbacks.append(callback)
        return self

    def on_complete(self, callback: Callable[[StreamMetrics], None]) -> "BaseStreamWrapper":
        """Register callback for stream completion."""
        self._complete_callbacks.append(callback)
        return self

    async def __aiter__(self) -> AsyncIterator[StreamChunk]:
        """Async iteration over stream chunks."""
        self.status = StreamStatus.STREAMING

        try:
            async for raw_chunk in self._get_chunks():
                chunk = self._process_chunk(raw_chunk)
                chunk.index = self._chunk_index
                self._chunk_index += 1

                # Track first token
                if not self._first_token_received and chunk.content:
                    self._first_token_received = True
                    self._metrics.time_to_first_token = (
                        _utcnow() - self._metrics.start_time
                    ).total_seconds()

                # Accumulate content
                self._accumulated_content += chunk.content
                self._chunks.append(chunk)

                # Update metrics
                self._metrics.total_chunks += 1
                if chunk.token_count:
                    self._metrics.total_tokens += chunk.token_count

                # Fire callbacks
                for callback in self._callbacks:
                    try:
                        callback(chunk)
                    except Exception as e:
                        logger.warning(f"Stream chunk callback error: {e}")

                yield chunk

            # Mark final chunk
            if self._chunks:
                self._chunks[-1].is_final = True

            # Complete stream
            self.status = StreamStatus.COMPLETED
            self._metrics.end_time = _utcnow()
            self._metrics.calculate_final_metrics()

            # Fire completion callbacks
            for callback in self._complete_callbacks:
                try:
                    callback(self._metrics)
                except Exception as e:
                    logger.warning(f"Stream completion callback error: {e}")

        except Exception as e:
            self.status = StreamStatus.ERROR
            self._metrics.errors.append(str(e))
            self._metrics.end_time = _utcnow()

            # Fire error callbacks
            for callback in self._error_callbacks:
                try:
                    callback(e)
                except Exception as cb_error:
                    logger.warning(f"Stream error callback failed: {cb_error}")

            raise

    def get_accumulated_content(self) -> str:
        """Get all content accumulated so far."""
        return self._accumulated_content

    def get_chunks(self) -> List[StreamChunk]:
        """Get all chunks received so far."""
        return self._chunks.copy()

    def get_metrics(self) -> StreamMetrics:
        """Get current metrics."""
        return self._metrics

    def cancel(self) -> None:
        """Cancel the stream."""
        self.status = StreamStatus.CANCELLED
        self._metrics.end_time = _utcnow()
        self._metrics.calculate_final_metrics()


class LLMStreamWrapper(BaseStreamWrapper[Any]):
    """
    Stream wrapper for LLM responses.

    Handles streaming from various LLM providers:
    - OpenAI
    - Anthropic
    - LangChain
    """

    def __init__(
        self,
        llm_stream: Any,
        model: Optional[str] = None,
        stream_id: Optional[str] = None
    ):
        super().__init__(stream_id)
        self._llm_stream = llm_stream
        self._model = model

    async def _get_chunks(self) -> AsyncIterator[Any]:
        """Get chunks from LLM stream."""
        if hasattr(self._llm_stream, '__aiter__'):
            async for chunk in self._llm_stream:
                yield chunk
        elif hasattr(self._llm_stream, '__iter__'):
            for chunk in self._llm_stream:
                yield chunk
        else:
            # Single response, not a stream
            yield self._llm_stream

    def _process_chunk(self, raw_chunk: Any) -> StreamChunk:
        """Process LLM chunk into StreamChunk."""
        content = ""
        token_count = None
        metadata = {}

        # Handle different chunk formats
        if hasattr(raw_chunk, 'content'):
            # LangChain AIMessageChunk
            content = raw_chunk.content or ""
            if hasattr(raw_chunk, 'usage_metadata'):
                metadata['usage'] = raw_chunk.usage_metadata
        elif hasattr(raw_chunk, 'choices'):
            # OpenAI format
            if raw_chunk.choices:
                delta = raw_chunk.choices[0].delta
                content = getattr(delta, 'content', '') or ""
            if hasattr(raw_chunk, 'usage'):
                metadata['usage'] = raw_chunk.usage
        elif hasattr(raw_chunk, 'delta'):
            # Anthropic format
            if hasattr(raw_chunk.delta, 'text'):
                content = raw_chunk.delta.text or ""
        elif isinstance(raw_chunk, str):
            content = raw_chunk
        elif isinstance(raw_chunk, dict):
            content = raw_chunk.get('content', '') or raw_chunk.get('text', '')
            metadata = {k: v for k, v in raw_chunk.items() if k not in ('content', 'text')}

        # Estimate token count (rough: 4 chars per token)
        if content:
            token_count = max(1, len(content) // 4)

        return StreamChunk(
            id=str(uuid.uuid4()),
            content=content,
            index=0,  # Will be set by base class
            token_count=token_count,
            source_type="llm",
            model=self._model,
            metadata=metadata
        )


class ToolStreamWrapper(BaseStreamWrapper[Dict[str, Any]]):
    """
    Stream wrapper for tool execution results.

    Handles streaming output from tools that support it.
    """

    def __init__(
        self,
        tool_stream: Any,
        tool_name: str,
        stream_id: Optional[str] = None
    ):
        super().__init__(stream_id)
        self._tool_stream = tool_stream
        self._tool_name = tool_name

    async def _get_chunks(self) -> AsyncIterator[Dict[str, Any]]:
        """Get chunks from tool stream."""
        if hasattr(self._tool_stream, '__aiter__'):
            async for chunk in self._tool_stream:
                yield chunk
        elif hasattr(self._tool_stream, '__iter__'):
            for chunk in self._tool_stream:
                yield chunk
        else:
            # Single result
            yield {"content": str(self._tool_stream)}

    def _process_chunk(self, raw_chunk: Dict[str, Any]) -> StreamChunk:
        """Process tool chunk into StreamChunk."""
        content = ""
        metadata = {}

        if isinstance(raw_chunk, dict):
            content = raw_chunk.get('content', '') or raw_chunk.get('output', '')
            metadata = {k: v for k, v in raw_chunk.items() if k not in ('content', 'output')}
        elif isinstance(raw_chunk, str):
            content = raw_chunk
        else:
            content = str(raw_chunk)

        return StreamChunk(
            id=str(uuid.uuid4()),
            content=content,
            index=0,
            source_type="tool",
            metadata={**metadata, "tool_name": self._tool_name}
        )


def create_stream_wrapper(
    stream: Any,
    stream_type: str = "auto",
    **kwargs
) -> BaseStreamWrapper:
    """
    Factory function to create appropriate stream wrapper.

    Args:
        stream: The stream to wrap
        stream_type: Type of stream ("llm", "tool", "auto")
        **kwargs: Additional arguments for the wrapper

    Returns:
        Appropriate stream wrapper instance
    """
    if stream_type == "llm":
        return LLMStreamWrapper(stream, **kwargs)
    elif stream_type == "tool":
        return ToolStreamWrapper(stream, **kwargs)
    elif stream_type == "auto":
        # Try to detect stream type
        if hasattr(stream, 'choices') or hasattr(stream, 'content'):
            return LLMStreamWrapper(stream, **kwargs)
        else:
            return ToolStreamWrapper(stream, tool_name=kwargs.get('tool_name', 'unknown'), **kwargs)
    else:
        raise ValueError(f"Unknown stream type: {stream_type}")
