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
from .telemetry import (  # Models; Exporters; Tracing; Metrics; Decorators; Global functions
    ConsoleSpanExporter,
    Counter,
    Gauge,
    Histogram,
    InMemorySpanExporter,
    Instrument,
    Meter,
    MeterProvider,
    MetricPoint,
    OTLPSpanExporter,
    Span,
    SpanContext,
    SpanEvent,
    SpanExporter,
    Tracer,
    TracerProvider,
    UpDownCounter,
    counted,
    create_meter_provider,
    create_tracer_provider,
    get_meter,
    get_meter_provider,
    get_tracer,
    get_tracer_provider,
    set_meter_provider,
    set_tracer_provider,
    timed,
    trace,
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
