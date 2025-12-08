"""
Telemetry Models Module.

Dataclasses for spans and metrics.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class SpanContext:
    """Context for distributed tracing spans."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    trace_flags: int = 1  # sampled
    trace_state: Dict[str, str] = field(default_factory=dict)
    baggage: Dict[str, str] = field(default_factory=dict)


@dataclass
class SpanEvent:
    """Event recorded within a span."""
    name: str
    timestamp: datetime
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Span:
    """A distributed tracing span."""
    name: str
    context: SpanContext
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "OK"
    status_message: str = ""
    kind: str = "INTERNAL"  # SERVER, CLIENT, PRODUCER, CONSUMER, INTERNAL
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[SpanEvent] = field(default_factory=list)
    links: List[SpanContext] = field(default_factory=list)

    def add_event(self, name: str, attributes: Dict[str, Any] = None) -> None:
        """Add an event to the span."""
        self.events.append(SpanEvent(
            name=name,
            timestamp=datetime.utcnow(),
            attributes=attributes or {}
        ))

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute."""
        self.attributes[key] = value

    def set_status(self, status: str, message: str = "") -> None:
        """Set the span status."""
        self.status = status
        self.status_message = message

    def record_exception(self, exception: Exception) -> None:
        """Record an exception on the span."""
        self.add_event("exception", {
            "exception.type": type(exception).__name__,
            "exception.message": str(exception),
            "exception.stacktrace": ""  # Would include traceback
        })
        self.set_status("ERROR", str(exception))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to OTLP-compatible dictionary."""
        return {
            "name": self.name,
            "trace_id": self.context.trace_id,
            "span_id": self.context.span_id,
            "parent_span_id": self.context.parent_span_id,
            "start_time_unix_nano": int(self.start_time.timestamp() * 1e9),
            "end_time_unix_nano": int(self.end_time.timestamp() * 1e9) if self.end_time else None,
            "kind": self.kind,
            "status": {"code": self.status, "message": self.status_message},
            "attributes": [{"key": k, "value": {"stringValue": str(v)}} for k, v in self.attributes.items()],
            "events": [
                {
                    "name": e.name,
                    "timeUnixNano": int(e.timestamp.timestamp() * 1e9),
                    "attributes": e.attributes
                }
                for e in self.events
            ]
        }


@dataclass
class MetricPoint:
    """A single metric measurement."""
    timestamp: datetime
    value: float
    attributes: Dict[str, str] = field(default_factory=dict)
