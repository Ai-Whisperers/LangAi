"""
Streaming Support for Anthropic API.

Enables streaming responses for real-time progress updates and better UX.
Supports both synchronous and asynchronous streaming.

Usage:
    from company_researcher.llm.streaming import get_streaming_client

    client = get_streaming_client()

    # Sync streaming with callback
    result = client.stream_message(
        model="claude-sonnet-4-20250514",
        messages=[{"role": "user", "content": "Analyze Tesla"}],
        on_text=lambda chunk: print(chunk, end="", flush=True)
    )

    # Async streaming
    async for chunk in client.astream_message(...):
        print(chunk, end="", flush=True)
"""

from typing import (
    AsyncIterator,
    Callable,
    Optional,
    List,
    Dict,
    Any,
    Generator
)
from dataclasses import dataclass
from threading import Lock

from anthropic import Anthropic

from .client_factory import get_anthropic_client


@dataclass
class StreamingStats:
    """Statistics for a streaming response."""
    chunks_received: int = 0
    total_characters: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    time_to_first_chunk_ms: Optional[float] = None
    total_time_ms: Optional[float] = None


@dataclass
class StreamingResult:
    """Result from a streaming operation."""
    content: str
    stats: StreamingStats
    stop_reason: Optional[str] = None
    model: Optional[str] = None


class StreamingClient:
    """
    Handles streaming responses from Anthropic.

    Provides both synchronous and asynchronous streaming with
    callback support for real-time processing.
    """

    def __init__(self, client: Optional[Anthropic] = None):
        """
        Initialize the streaming client.

        Args:
            client: Optional Anthropic client. If not provided, uses singleton.
        """
        self.client = client or get_anthropic_client()

    def stream_message(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        max_tokens: int = 1000,
        temperature: float = 0.0,
        system: Optional[str] = None,
        on_text: Optional[Callable[[str], None]] = None,
        on_start: Optional[Callable[[], None]] = None,
        on_complete: Optional[Callable[[StreamingResult], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        **kwargs
    ) -> StreamingResult:
        """
        Stream a message with optional callbacks.

        Args:
            model: Model to use
            messages: Conversation messages
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            system: Optional system prompt
            on_text: Callback for each text chunk
            on_start: Callback when streaming starts
            on_complete: Callback when streaming completes
            on_error: Callback on error
            **kwargs: Additional parameters

        Returns:
            StreamingResult with full content and statistics
        """
        import time

        full_response = ""
        stats = StreamingStats()
        start_time = time.time()
        first_chunk_time = None

        params = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
            **kwargs
        }

        if system:
            params["system"] = system

        try:
            if on_start:
                on_start()

            with self.client.messages.stream(**params) as stream:
                for text in stream.text_stream:
                    if first_chunk_time is None:
                        first_chunk_time = time.time()
                        stats.time_to_first_chunk_ms = (first_chunk_time - start_time) * 1000

                    full_response += text
                    stats.chunks_received += 1
                    stats.total_characters += len(text)

                    if on_text:
                        on_text(text)

                # Get final message for usage stats
                final_message = stream.get_final_message()
                stats.input_tokens = final_message.usage.input_tokens
                stats.output_tokens = final_message.usage.output_tokens
                stop_reason = final_message.stop_reason

            stats.total_time_ms = (time.time() - start_time) * 1000

            result = StreamingResult(
                content=full_response,
                stats=stats,
                stop_reason=stop_reason,
                model=model
            )

            if on_complete:
                on_complete(result)

            return result

        except Exception as e:
            if on_error:
                on_error(e)
            raise

    def stream_to_generator(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        max_tokens: int = 1000,
        temperature: float = 0.0,
        system: Optional[str] = None,
        **kwargs
    ) -> Generator[str, None, StreamingResult]:
        """
        Stream message as a generator.

        Yields text chunks and returns final result.

        Args:
            model: Model to use
            messages: Conversation messages
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            system: Optional system prompt
            **kwargs: Additional parameters

        Yields:
            Text chunks

        Returns:
            StreamingResult (accessible via generator.value after exhaustion)
        """
        import time

        full_response = ""
        stats = StreamingStats()
        start_time = time.time()
        first_chunk_time = None

        params = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
            **kwargs
        }

        if system:
            params["system"] = system

        with self.client.messages.stream(**params) as stream:
            for text in stream.text_stream:
                if first_chunk_time is None:
                    first_chunk_time = time.time()
                    stats.time_to_first_chunk_ms = (first_chunk_time - start_time) * 1000

                full_response += text
                stats.chunks_received += 1
                stats.total_characters += len(text)

                yield text

            final_message = stream.get_final_message()
            stats.input_tokens = final_message.usage.input_tokens
            stats.output_tokens = final_message.usage.output_tokens
            stop_reason = final_message.stop_reason

        stats.total_time_ms = (time.time() - start_time) * 1000

        return StreamingResult(
            content=full_response,
            stats=stats,
            stop_reason=stop_reason,
            model=model
        )

    async def astream_message(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        max_tokens: int = 1000,
        temperature: float = 0.0,
        system: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Async stream a message.

        Args:
            model: Model to use
            messages: Conversation messages
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            system: Optional system prompt
            **kwargs: Additional parameters

        Yields:
            Text chunks asynchronously
        """
        params = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
            **kwargs
        }

        if system:
            params["system"] = system

        async with self.client.messages.stream(**params) as stream:
            async for text in stream.text_stream:
                yield text

    async def astream_with_stats(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        max_tokens: int = 1000,
        temperature: float = 0.0,
        system: Optional[str] = None,
        **kwargs
    ) -> StreamingResult:
        """
        Async stream with full statistics.

        Args:
            model: Model to use
            messages: Conversation messages
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            system: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            StreamingResult with content and statistics
        """
        import time

        full_response = ""
        stats = StreamingStats()
        start_time = time.time()
        first_chunk_time = None

        params = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
            **kwargs
        }

        if system:
            params["system"] = system

        async with self.client.messages.stream(**params) as stream:
            async for text in stream.text_stream:
                if first_chunk_time is None:
                    first_chunk_time = time.time()
                    stats.time_to_first_chunk_ms = (first_chunk_time - start_time) * 1000

                full_response += text
                stats.chunks_received += 1
                stats.total_characters += len(text)

            final_message = await stream.get_final_message()
            stats.input_tokens = final_message.usage.input_tokens
            stats.output_tokens = final_message.usage.output_tokens
            stop_reason = final_message.stop_reason

        stats.total_time_ms = (time.time() - start_time) * 1000

        return StreamingResult(
            content=full_response,
            stats=stats,
            stop_reason=stop_reason,
            model=model
        )


# Singleton instance
_streaming_client: Optional[StreamingClient] = None
_streaming_lock = Lock()


def get_streaming_client() -> StreamingClient:
    """
    Get singleton streaming client instance.

    Returns:
        StreamingClient instance
    """
    global _streaming_client
    if _streaming_client is None:
        with _streaming_lock:
            if _streaming_client is None:
                _streaming_client = StreamingClient()
    return _streaming_client


class StreamingProgressPrinter:
    """
    Helper class for printing streaming progress.

    Useful for CLI applications that want to show real-time output.
    """

    def __init__(
        self,
        prefix: str = "",
        suffix: str = "",
        show_stats: bool = True
    ):
        """
        Initialize the progress printer.

        Args:
            prefix: Text to print before streaming starts
            suffix: Text to print after streaming completes
            show_stats: Whether to show statistics after completion
        """
        self.prefix = prefix
        self.suffix = suffix
        self.show_stats = show_stats

    def on_start(self) -> None:
        """Called when streaming starts."""
        if self.prefix:
            print(self.prefix, end="", flush=True)

    def on_text(self, text: str) -> None:
        """Called for each text chunk."""
        print(text, end="", flush=True)

    def on_complete(self, result: StreamingResult) -> None:
        """Called when streaming completes."""
        print()  # Newline after streaming
        if self.suffix:
            print(self.suffix)
        if self.show_stats:
            print(f"\n[Streaming Stats]")
            print(f"  Time to first chunk: {result.stats.time_to_first_chunk_ms:.0f}ms")
            print(f"  Total time: {result.stats.total_time_ms:.0f}ms")
            print(f"  Chunks: {result.stats.chunks_received}")
            print(f"  Tokens: {result.stats.input_tokens} in / {result.stats.output_tokens} out")

    def on_error(self, error: Exception) -> None:
        """Called on error."""
        print(f"\n[Streaming Error] {error}")


def stream_research_analysis(
    company_name: str,
    analysis_type: str,
    content: str,
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 1000,
    show_progress: bool = True
) -> StreamingResult:
    """
    Stream a research analysis with optional progress display.

    Convenience function for streaming research agent outputs.

    Args:
        company_name: Company being analyzed
        analysis_type: Type of analysis
        content: Content to analyze
        model: Model to use
        max_tokens: Maximum tokens
        show_progress: Whether to show real-time progress

    Returns:
        StreamingResult with analysis
    """
    client = get_streaming_client()

    prompts = {
        "financial": "You are a financial analyst. Analyze the financial data.",
        "market": "You are a market analyst. Analyze market positioning.",
        "product": "You are a product analyst. Analyze products and technology.",
        "synthesis": "You are a senior analyst. Synthesize the research findings."
    }

    system = prompts.get(analysis_type, "You are a research analyst.")

    messages = [{
        "role": "user",
        "content": f"Company: {company_name}\n\nContent:\n{content}\n\nProvide your analysis:"
    }]

    if show_progress:
        printer = StreamingProgressPrinter(
            prefix=f"\n[{analysis_type.title()} Analysis - Streaming]\n",
            show_stats=True
        )
        return client.stream_message(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            system=system,
            on_start=printer.on_start,
            on_text=printer.on_text,
            on_complete=printer.on_complete,
            on_error=printer.on_error
        )
    else:
        return client.stream_message(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            system=system
        )
