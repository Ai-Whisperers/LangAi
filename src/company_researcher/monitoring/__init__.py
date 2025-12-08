"""
Monitoring & Analytics Module (Phase 19).

Comprehensive monitoring for company research:
- Metrics collection
- Cost tracking
- Performance monitoring
- Analytics and reporting
- Alerting
- OpenTelemetry integration

Usage:
    from src.company_researcher.monitoring import (
        MetricsCollector,
        CostTracker,
        PerformanceMonitor,
        AnalyticsAggregator,
        AlertManager,
        get_dashboard_data,
        # OpenTelemetry
        TracerProvider,
        get_tracer,
        trace,
        timed
    )

    # Track metrics
    metrics = MetricsCollector()
    metrics.record_research_start("Tesla")
    metrics.record_research_complete("Tesla", duration=45.2, cost=0.05)

    # Get dashboard data
    dashboard = get_dashboard_data()

    # Distributed tracing
    tracer = get_tracer("research")
    with tracer.start_span("fetch_data") as span:
        span.set_attribute("company", "Tesla")
        # do work
"""

from .metrics import (
    MetricsCollector,
    Metric,
    MetricType,
    create_metrics_collector,
)

from .cost_tracker import (
    CostTracker,
    CostEntry,
    CostCategory,
    create_cost_tracker,
)

from .performance import (
    PerformanceMonitor,
    PerformanceMetric,
    create_performance_monitor,
)

from .analytics import (
    AnalyticsAggregator,
    TimeRange,
    get_dashboard_data,
    create_analytics_aggregator,
)

from .alerts import (
    AlertManager,
    Alert,
    AlertSeverity,
    AlertRule,
    create_alert_manager,
)

from .opentelemetry import (
    # Tracing
    TracerProvider,
    Tracer,
    Span,
    SpanContext,
    SpanEvent,
    SpanExporter,
    ConsoleSpanExporter,
    OTLPSpanExporter,
    InMemorySpanExporter,
    # Metrics
    MeterProvider,
    Meter,
    Counter,
    UpDownCounter,
    Histogram,
    Gauge,
    MetricPoint,
    # Decorators
    trace,
    timed,
    counted,
    # Factory functions
    create_tracer_provider,
    create_meter_provider,
    # Global accessors
    get_tracer_provider,
    set_tracer_provider,
    get_tracer,
    get_meter_provider,
    set_meter_provider,
    get_meter,
)

__all__ = [
    # Metrics
    "MetricsCollector",
    "Metric",
    "MetricType",
    "create_metrics_collector",
    # Cost
    "CostTracker",
    "CostEntry",
    "CostCategory",
    "create_cost_tracker",
    # Performance
    "PerformanceMonitor",
    "PerformanceMetric",
    "create_performance_monitor",
    # Analytics
    "AnalyticsAggregator",
    "TimeRange",
    "get_dashboard_data",
    "create_analytics_aggregator",
    # Alerts
    "AlertManager",
    "Alert",
    "AlertSeverity",
    "AlertRule",
    "create_alert_manager",
    # OpenTelemetry Tracing
    "TracerProvider",
    "Tracer",
    "Span",
    "SpanContext",
    "SpanEvent",
    "SpanExporter",
    "ConsoleSpanExporter",
    "OTLPSpanExporter",
    "InMemorySpanExporter",
    # OpenTelemetry Metrics
    "MeterProvider",
    "Meter",
    "Counter",
    "UpDownCounter",
    "Histogram",
    "Gauge",
    "MetricPoint",
    # OpenTelemetry Decorators
    "trace",
    "timed",
    "counted",
    # OpenTelemetry Factory
    "create_tracer_provider",
    "create_meter_provider",
    "get_tracer_provider",
    "set_tracer_provider",
    "get_tracer",
    "get_meter_provider",
    "set_meter_provider",
    "get_meter",
]
