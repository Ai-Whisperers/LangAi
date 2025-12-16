"""
OpenTelemetry Integration Package.

Distributed tracing and metrics:
- Trace context propagation
- Span creation and management
- Metric exporters
- Log correlation
- Integration with OTLP backends

Usage:
    from company_researcher.monitoring.telemetry import (
        TracerProvider,
        Tracer,
        Span,
        MeterProvider,
        Meter,
        get_tracer,
        get_meter,
        trace,
        timed,
        counted
    )
"""

from .decorators import counted, timed, trace
from .exporters import ConsoleSpanExporter, InMemorySpanExporter, OTLPSpanExporter, SpanExporter
from .globals import (
    create_meter_provider,
    create_tracer_provider,
    get_meter,
    get_meter_provider,
    get_tracer,
    get_tracer_provider,
    set_meter_provider,
    set_tracer_provider,
)
from .metrics import Counter, Gauge, Histogram, Instrument, Meter, MeterProvider, UpDownCounter
from .models import MetricPoint, Span, SpanContext, SpanEvent
from .tracing import Tracer, TracerProvider

__all__ = [
    # Models
    "SpanContext",
    "SpanEvent",
    "Span",
    "MetricPoint",
    # Exporters
    "SpanExporter",
    "ConsoleSpanExporter",
    "OTLPSpanExporter",
    "InMemorySpanExporter",
    # Tracing
    "TracerProvider",
    "Tracer",
    # Metrics
    "Instrument",
    "Counter",
    "UpDownCounter",
    "Histogram",
    "Gauge",
    "Meter",
    "MeterProvider",
    # Decorators
    "trace",
    "timed",
    "counted",
    # Global functions
    "set_tracer_provider",
    "get_tracer_provider",
    "get_tracer",
    "set_meter_provider",
    "get_meter_provider",
    "get_meter",
    "create_tracer_provider",
    "create_meter_provider",
]
