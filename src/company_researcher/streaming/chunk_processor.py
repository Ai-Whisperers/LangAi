"""
Chunk Processing - Token accumulation and chunk management.

Handles:
- Chunk buffering and batching
- Response accumulation
- Token counting
- Content assembly
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import AsyncIterator, Callable, List, Optional

from ..utils import get_logger

logger = get_logger(__name__)


def _utcnow() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


from .stream_wrapper import StreamChunk


@dataclass
class ChunkBuffer:
    """
    Buffer for accumulating stream chunks.

    Supports batching chunks for efficient processing.
    """

    buffer_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    max_size: int = 100
    flush_interval: float = 0.1  # seconds

    _chunks: List[StreamChunk] = field(default_factory=list)
    _last_flush: datetime = field(default_factory=_utcnow)
    _total_flushed: int = 0

    def add(self, chunk: StreamChunk) -> Optional[List[StreamChunk]]:
        """
        Add chunk to buffer.

        Returns:
            List of chunks if buffer should be flushed, None otherwise
        """
        self._chunks.append(chunk)

        # Check if we should flush
        should_flush = (
            len(self._chunks) >= self.max_size
            or chunk.is_final
            or (_utcnow() - self._last_flush).total_seconds() >= self.flush_interval
        )

        if should_flush:
            return self.flush()
        return None

    def flush(self) -> List[StreamChunk]:
        """Flush and return all buffered chunks."""
        chunks = self._chunks.copy()
        self._chunks = []
        self._last_flush = _utcnow()
        self._total_flushed += len(chunks)
        return chunks

    def get_pending(self) -> List[StreamChunk]:
        """Get chunks without flushing."""
        return self._chunks.copy()

    @property
    def size(self) -> int:
        """Current buffer size."""
        return len(self._chunks)

    @property
    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        return len(self._chunks) == 0


@dataclass
class ChunkAggregator:
    """
    Aggregates chunks into complete responses.

    Tracks:
    - Content accumulation
    - Token counts
    - Timing metrics
    """

    aggregator_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    _content: str = ""
    _chunks: List[StreamChunk] = field(default_factory=list)
    _token_count: int = 0
    _start_time: Optional[datetime] = None
    _first_chunk_time: Optional[datetime] = None
    _last_chunk_time: Optional[datetime] = None

    def add_chunk(self, chunk: StreamChunk) -> None:
        """Add a chunk to the aggregation."""
        now = _utcnow()

        if self._start_time is None:
            self._start_time = now
        if self._first_chunk_time is None and chunk.content:
            self._first_chunk_time = now

        self._last_chunk_time = now
        self._content += chunk.content
        self._chunks.append(chunk)

        if chunk.token_count:
            self._token_count += chunk.token_count

    def get_content(self) -> str:
        """Get accumulated content."""
        return self._content

    def get_chunks(self) -> List[StreamChunk]:
        """Get all chunks."""
        return self._chunks.copy()

    def get_token_count(self) -> int:
        """Get total token count."""
        return self._token_count

    def get_time_to_first_token(self) -> Optional[float]:
        """Get time to first token in seconds."""
        if self._start_time and self._first_chunk_time:
            return (self._first_chunk_time - self._start_time).total_seconds()
        return None

    def get_total_duration(self) -> Optional[float]:
        """Get total duration in seconds."""
        if self._start_time and self._last_chunk_time:
            return (self._last_chunk_time - self._start_time).total_seconds()
        return None

    def get_tokens_per_second(self) -> Optional[float]:
        """Calculate tokens per second."""
        duration = self.get_total_duration()
        if duration and duration > 0:
            return self._token_count / duration
        return None

    def clear(self) -> None:
        """Clear the aggregator."""
        self._content = ""
        self._chunks = []
        self._token_count = 0
        self._start_time = None
        self._first_chunk_time = None
        self._last_chunk_time = None


class ChunkProcessor:
    """
    Processes stream chunks with transformations and filtering.

    Usage:
        processor = ChunkProcessor()
        processor.add_filter(lambda c: len(c.content) > 0)
        processor.add_transform(lambda c: c.content.upper())

        async for processed in processor.process(stream):
            print(processed)
    """

    def __init__(self, buffer_size: int = 100, flush_interval: float = 0.1):
        self._buffer = ChunkBuffer(max_size=buffer_size, flush_interval=flush_interval)
        self._aggregator = ChunkAggregator()
        self._filters: List[Callable[[StreamChunk], bool]] = []
        self._transforms: List[Callable[[StreamChunk], StreamChunk]] = []
        self._on_chunk_callbacks: List[Callable[[StreamChunk], None]] = []
        self._on_batch_callbacks: List[Callable[[List[StreamChunk]], None]] = []

    def add_filter(self, filter_fn: Callable[[StreamChunk], bool]) -> "ChunkProcessor":
        """Add a filter function. Chunks that return False are dropped."""
        self._filters.append(filter_fn)
        return self

    def add_transform(self, transform_fn: Callable[[StreamChunk], StreamChunk]) -> "ChunkProcessor":
        """Add a transform function to modify chunks."""
        self._transforms.append(transform_fn)
        return self

    def on_chunk(self, callback: Callable[[StreamChunk], None]) -> "ChunkProcessor":
        """Register callback for each processed chunk."""
        self._on_chunk_callbacks.append(callback)
        return self

    def on_batch(self, callback: Callable[[List[StreamChunk]], None]) -> "ChunkProcessor":
        """Register callback for batched chunks."""
        self._on_batch_callbacks.append(callback)
        return self

    def _apply_filters(self, chunk: StreamChunk) -> bool:
        """Apply all filters to chunk."""
        for filter_fn in self._filters:
            if not filter_fn(chunk):
                return False
        return True

    def _apply_transforms(self, chunk: StreamChunk) -> StreamChunk:
        """Apply all transforms to chunk."""
        result = chunk
        for transform_fn in self._transforms:
            result = transform_fn(result)
        return result

    async def process(self, chunks: AsyncIterator[StreamChunk]) -> AsyncIterator[StreamChunk]:
        """
        Process stream of chunks.

        Args:
            chunks: Async iterator of StreamChunk

        Yields:
            Processed StreamChunk objects
        """
        async for chunk in chunks:
            # Apply filters
            if not self._apply_filters(chunk):
                continue

            # Apply transforms
            processed = self._apply_transforms(chunk)

            # Add to aggregator
            self._aggregator.add_chunk(processed)

            # Fire chunk callbacks
            for callback in self._on_chunk_callbacks:
                try:
                    callback(processed)
                except Exception as e:
                    logger.warning(f"Chunk callback error: {e}")

            # Buffer management
            batch = self._buffer.add(processed)
            if batch:
                for callback in self._on_batch_callbacks:
                    try:
                        callback(batch)
                    except Exception as e:
                        logger.warning(f"Batch callback error: {e}")

            yield processed

        # Flush remaining
        remaining = self._buffer.flush()
        if remaining:
            for callback in self._on_batch_callbacks:
                try:
                    callback(remaining)
                except Exception as e:
                    logger.warning(f"Final batch callback error: {e}")

    def get_aggregator(self) -> ChunkAggregator:
        """Get the chunk aggregator."""
        return self._aggregator

    def get_buffer(self) -> ChunkBuffer:
        """Get the chunk buffer."""
        return self._buffer


async def process_chunks(
    chunks: AsyncIterator[StreamChunk],
    filters: Optional[List[Callable[[StreamChunk], bool]]] = None,
    transforms: Optional[List[Callable[[StreamChunk], StreamChunk]]] = None,
    on_chunk: Optional[Callable[[StreamChunk], None]] = None,
) -> AsyncIterator[StreamChunk]:
    """
    Convenience function to process chunks.

    Args:
        chunks: Stream of chunks to process
        filters: Optional list of filter functions
        transforms: Optional list of transform functions
        on_chunk: Optional callback for each chunk

    Yields:
        Processed chunks
    """
    processor = ChunkProcessor()

    if filters:
        for f in filters:
            processor.add_filter(f)

    if transforms:
        for t in transforms:
            processor.add_transform(t)

    if on_chunk:
        processor.on_chunk(on_chunk)

    async for chunk in processor.process(chunks):
        yield chunk


async def accumulate_response(
    chunks: AsyncIterator[StreamChunk], include_empty: bool = False
) -> str:
    """
    Accumulate all chunks into a single response string.

    Args:
        chunks: Stream of chunks
        include_empty: Whether to include empty chunks

    Returns:
        Complete accumulated response
    """
    aggregator = ChunkAggregator()

    async for chunk in chunks:
        if include_empty or chunk.content:
            aggregator.add_chunk(chunk)

    return aggregator.get_content()
