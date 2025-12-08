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

from .models import (
    SpanContext,
    SpanEvent,
    Span,
    MetricPoint,
)

from .exporters import (
    SpanExporter,
    ConsoleSpanExporter,
    OTLPSpanExporter,
    InMemorySpanExporter,
)

from .tracing import (
    TracerProvider,
    Tracer,
)

from .metrics import (
    Instrument,
    Counter,
    UpDownCounter,
    Histogram,
    Gauge,
    Meter,
    MeterProvider,
)

from .decorators import (
    trace,
    timed,
    counted,
)

from .globals import (
    set_tracer_provider,
    get_tracer_provider,
    get_tracer,
    set_meter_provider,
    get_meter_provider,
    get_meter,
    create_tracer_provider,
    create_meter_provider,
)

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
