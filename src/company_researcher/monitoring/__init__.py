"""
Monitoring & Analytics Module (Phase 19).

Comprehensive monitoring for company research:
- Metrics collection
- Cost tracking
- Performance monitoring
- Analytics and reporting
- Alerting

Usage:
    from src.company_researcher.monitoring import (
        MetricsCollector,
        CostTracker,
        PerformanceMonitor,
        AnalyticsAggregator,
        AlertManager,
        get_dashboard_data
    )

    # Track metrics
    metrics = MetricsCollector()
    metrics.record_research_start("Tesla")
    metrics.record_research_complete("Tesla", duration=45.2, cost=0.05)

    # Get dashboard data
    dashboard = get_dashboard_data()
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
]
