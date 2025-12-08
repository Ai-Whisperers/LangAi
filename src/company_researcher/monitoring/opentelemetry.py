"""
OpenTelemetry Integration - Distributed tracing and metrics.

DEPRECATED: This module re-exports from the modular telemetry package.
Import directly from company_researcher.monitoring.telemetry instead:

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

# Re-export all public API from the telemetry package for backward compatibility
from .telemetry import (
    # Models
    SpanContext,
    SpanEvent,
    Span,
    MetricPoint,
    # Exporters
    SpanExporter,
    ConsoleSpanExporter,
    OTLPSpanExporter,
    InMemorySpanExporter,
    # Tracing
    TracerProvider,
    Tracer,
    # Metrics
    Instrument,
    Counter,
    UpDownCounter,
    Histogram,
    Gauge,
    Meter,
    MeterProvider,
    # Decorators
    trace,
    timed,
    counted,
    # Global functions
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
