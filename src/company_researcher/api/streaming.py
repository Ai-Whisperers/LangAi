"""
Streaming Results Module (PS-004).

Provides real-time progress updates during research:
- Server-Sent Events (SSE) for web clients
- Async generators for programmatic use
- Progress callbacks for custom handling
- Event-based progress tracking
"""

from typing import Dict, Any, Optional, Callable, AsyncGenerator, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import json
from ..utils import get_logger, utc_now

logger = get_logger(__name__)


class EventType(str, Enum):
    """Types of streaming events."""
    RESEARCH_STARTED = "research_started"
    AGENT_STARTED = "agent_started"
    AGENT_PROGRESS = "agent_progress"
    AGENT_COMPLETED = "agent_completed"
    SEARCH_STARTED = "search_started"
    SEARCH_COMPLETED = "search_completed"
    ANALYSIS_STARTED = "analysis_started"
    ANALYSIS_PROGRESS = "analysis_progress"
    ANALYSIS_COMPLETED = "analysis_completed"
    QUALITY_CHECK = "quality_check"
    ITERATION_STARTED = "iteration_started"
    ITERATION_COMPLETED = "iteration_completed"
    RESEARCH_COMPLETED = "research_completed"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class StreamEvent:
    """A streaming event with metadata."""
    event_type: EventType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=utc_now)
    agent_name: Optional[str] = None
    progress_percent: Optional[float] = None
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "event_type": self.event_type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "agent_name": self.agent_name,
            "progress_percent": self.progress_percent,
            "message": self.message,
        }

    def to_sse(self) -> str:
        """Convert to Server-Sent Event format."""
        data = json.dumps(self.to_dict())
        return f"event: {self.event_type.value}\ndata: {data}\n\n"


class ProgressTracker:
    """
    Track research progress and emit events.

    Usage:
        tracker = ProgressTracker()

        # Register callback
        tracker.on_event(my_callback)

        # Emit events
        await tracker.emit(EventType.RESEARCH_STARTED, {"company": "Apple"})

        # Or use context managers
        async with tracker.agent_context("financial"):
            # agent work here...
            await tracker.update_progress(50, "Analyzing revenue data")
    """

    def __init__(self):
        self._callbacks: List[Callable[[StreamEvent], Any]] = []
        self._events: List[StreamEvent] = []
        self._current_agent: Optional[str] = None
        self._total_agents: int = 0
        self._completed_agents: int = 0
        self._started_at: Optional[datetime] = None

    def on_event(self, callback: Callable[[StreamEvent], Any]) -> None:
        """Register a callback for events."""
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[StreamEvent], Any]) -> None:
        """Remove a registered callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    async def emit(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        agent_name: Optional[str] = None,
        progress_percent: Optional[float] = None,
        message: Optional[str] = None
    ) -> StreamEvent:
        """Emit a streaming event."""
        event = StreamEvent(
            event_type=event_type,
            data=data,
            agent_name=agent_name or self._current_agent,
            progress_percent=progress_percent,
            message=message
        )
        self._events.append(event)

        # Notify all callbacks
        for callback in self._callbacks:
            try:
                result = callback(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Error in event callback: {e}")

        return event

    async def start_research(self, company_name: str, total_agents: int = 0) -> None:
        """Signal research has started."""
        self._started_at = utc_now()
        self._total_agents = total_agents
        self._completed_agents = 0

        await self.emit(
            EventType.RESEARCH_STARTED,
            {"company_name": company_name, "total_agents": total_agents},
            message=f"Starting research on {company_name}"
        )

    async def complete_research(self, success: bool, summary: Dict[str, Any]) -> None:
        """Signal research has completed."""
        duration = None
        if self._started_at:
            duration = (utc_now() - self._started_at).total_seconds()

        await self.emit(
            EventType.RESEARCH_COMPLETED,
            {"success": success, "summary": summary, "duration_seconds": duration},
            progress_percent=100.0,
            message="Research completed" if success else "Research failed"
        )

    async def start_agent(self, agent_name: str, description: str = "") -> None:
        """Signal an agent has started."""
        self._current_agent = agent_name
        progress = (self._completed_agents / max(self._total_agents, 1)) * 100

        await self.emit(
            EventType.AGENT_STARTED,
            {"agent_name": agent_name, "description": description},
            agent_name=agent_name,
            progress_percent=progress,
            message=f"Agent {agent_name} started"
        )

    async def complete_agent(self, agent_name: str, result: Dict[str, Any]) -> None:
        """Signal an agent has completed."""
        self._completed_agents += 1
        progress = (self._completed_agents / max(self._total_agents, 1)) * 100

        await self.emit(
            EventType.AGENT_COMPLETED,
            {"agent_name": agent_name, "result_summary": result},
            agent_name=agent_name,
            progress_percent=progress,
            message=f"Agent {agent_name} completed"
        )

        if self._current_agent == agent_name:
            self._current_agent = None

    async def update_progress(
        self,
        progress_percent: float,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update progress within current agent."""
        await self.emit(
            EventType.AGENT_PROGRESS,
            data or {},
            progress_percent=progress_percent,
            message=message
        )

    def get_events(self) -> List[StreamEvent]:
        """Get all emitted events."""
        return self._events.copy()

    def get_overall_progress(self) -> float:
        """Get overall research progress percentage."""
        if self._total_agents == 0:
            return 0.0
        return (self._completed_agents / self._total_agents) * 100


class StreamingResearchContext:
    """
    Context manager for streaming research results.

    Usage:
        async with StreamingResearchContext("Apple Inc.") as ctx:
            async for event in ctx.events():
                print(event)
    """

    def __init__(self, company_name: str, tracker: Optional[ProgressTracker] = None):
        self.company_name = company_name
        self.tracker = tracker or ProgressTracker()
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._active = False

    async def __aenter__(self) -> "StreamingResearchContext":
        self._active = True
        self.tracker.on_event(self._queue_event)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self._active = False
        self.tracker.remove_callback(self._queue_event)
        # Signal end of stream
        await self._event_queue.put(None)

    def _queue_event(self, event: StreamEvent) -> None:
        """Queue event for streaming."""
        if self._active:
            self._event_queue.put_nowait(event)

    async def events(self) -> AsyncGenerator[StreamEvent, None]:
        """Async generator for streaming events."""
        while self._active or not self._event_queue.empty():
            try:
                event = await asyncio.wait_for(
                    self._event_queue.get(),
                    timeout=1.0
                )
                if event is None:
                    break
                yield event
            except asyncio.TimeoutError:
                continue


async def stream_sse(tracker: ProgressTracker) -> AsyncGenerator[str, None]:
    """
    Generate Server-Sent Events from a progress tracker.

    Usage with FastAPI:
        @app.get("/research/{company}/stream")
        async def stream_research(company: str):
            tracker = ProgressTracker()
            # Start research in background
            asyncio.create_task(run_research(company, tracker))
            return StreamingResponse(
                stream_sse(tracker),
                media_type="text/event-stream"
            )
    """
    queue: asyncio.Queue = asyncio.Queue()
    completed = False

    def on_event(event: StreamEvent):
        nonlocal completed
        queue.put_nowait(event)
        if event.event_type == EventType.RESEARCH_COMPLETED:
            completed = True

    tracker.on_event(on_event)

    try:
        while not completed:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield event.to_sse()
            except asyncio.TimeoutError:
                # Send keepalive
                yield ": keepalive\n\n"
    finally:
        tracker.remove_callback(on_event)


def create_progress_tracker() -> ProgressTracker:
    """Create a new progress tracker."""
    return ProgressTracker()


def create_streaming_context(
    company_name: str,
    tracker: Optional[ProgressTracker] = None
) -> StreamingResearchContext:
    """Create a streaming research context."""
    return StreamingResearchContext(company_name, tracker)
