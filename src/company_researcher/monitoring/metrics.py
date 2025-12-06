"""
Metrics Collector (Phase 19.1).

Centralized metrics collection:
- Counter metrics
- Gauge metrics
- Histogram metrics
- Timer metrics
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import time
import threading
import statistics


# ============================================================================
# Enums and Data Models
# ============================================================================

class MetricType(str, Enum):
    """Types of metrics."""
    COUNTER = "counter"      # Monotonically increasing
    GAUGE = "gauge"          # Point-in-time value
    HISTOGRAM = "histogram"  # Distribution of values
    TIMER = "timer"          # Duration measurements


@dataclass
class Metric:
    """A recorded metric."""
    name: str
    type: MetricType
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels,
            "unit": self.unit
        }


@dataclass
class MetricSummary:
    """Summary statistics for a metric."""
    name: str
    count: int = 0
    total: float = 0.0
    min_value: float = float('inf')
    max_value: float = float('-inf')
    mean: float = 0.0
    std_dev: float = 0.0
    p50: float = 0.0
    p95: float = 0.0
    p99: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "count": self.count,
            "total": round(self.total, 4),
            "min": round(self.min_value, 4) if self.min_value != float('inf') else 0,
            "max": round(self.max_value, 4) if self.max_value != float('-inf') else 0,
            "mean": round(self.mean, 4),
            "std_dev": round(self.std_dev, 4),
            "p50": round(self.p50, 4),
            "p95": round(self.p95, 4),
            "p99": round(self.p99, 4)
        }


# ============================================================================
# Metrics Collector
# ============================================================================

class MetricsCollector:
    """
    Centralized metrics collection.

    Features:
    - Multiple metric types
    - Label-based filtering
    - Time-window aggregations
    - Export capabilities

    Usage:
        collector = MetricsCollector()

        # Record metrics
        collector.increment("research.started")
        collector.gauge("active_tasks", 5)
        collector.timing("research.duration", 45.2)
        collector.histogram("agent.tokens", 1500)

        # Get summaries
        summary = collector.get_summary("research.duration")
    """

    def __init__(
        self,
        retention_hours: int = 24,
        flush_interval_seconds: int = 60
    ):
        """
        Initialize metrics collector.

        Args:
            retention_hours: Hours to retain metrics
            flush_interval_seconds: Seconds between flushes
        """
        self._retention = timedelta(hours=retention_hours)
        self._flush_interval = flush_interval_seconds

        # Storage
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._timers: Dict[str, List[float]] = defaultdict(list)
        self._metrics: List[Metric] = []

        # Thread safety
        self._lock = threading.RLock()

        # Callbacks
        self._on_metric: List[Callable] = []

    # ==========================================================================
    # Recording Metrics
    # ==========================================================================

    def increment(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None
    ):
        """Increment a counter metric."""
        with self._lock:
            key = self._make_key(name, labels)
            self._counters[key] += value

            self._record(Metric(
                name=name,
                type=MetricType.COUNTER,
                value=self._counters[key],
                labels=labels or {}
            ))

    def decrement(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None
    ):
        """Decrement a counter (for gauges)."""
        with self._lock:
            key = self._make_key(name, labels)
            self._counters[key] -= value

            self._record(Metric(
                name=name,
                type=MetricType.COUNTER,
                value=self._counters[key],
                labels=labels or {}
            ))

    def gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """Set a gauge metric."""
        with self._lock:
            key = self._make_key(name, labels)
            self._gauges[key] = value

            self._record(Metric(
                name=name,
                type=MetricType.GAUGE,
                value=value,
                labels=labels or {}
            ))

    def timing(
        self,
        name: str,
        duration_seconds: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """Record a timing metric."""
        with self._lock:
            key = self._make_key(name, labels)
            self._timers[key].append(duration_seconds)

            self._record(Metric(
                name=name,
                type=MetricType.TIMER,
                value=duration_seconds,
                labels=labels or {},
                unit="seconds"
            ))

    def histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """Record a histogram metric."""
        with self._lock:
            key = self._make_key(name, labels)
            self._histograms[key].append(value)

            self._record(Metric(
                name=name,
                type=MetricType.HISTOGRAM,
                value=value,
                labels=labels or {}
            ))

    def _record(self, metric: Metric):
        """Record metric and notify callbacks."""
        self._metrics.append(metric)

        # Notify callbacks
        for callback in self._on_metric:
            try:
                callback(metric)
            except Exception:
                pass

    def _make_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """Create unique key for metric."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    # ==========================================================================
    # Context Manager for Timing
    # ==========================================================================

    def timer(self, name: str, labels: Optional[Dict[str, str]] = None):
        """
        Context manager for timing operations.

        Usage:
            with collector.timer("research.duration"):
                do_research()
        """
        return _TimerContext(self, name, labels)

    # ==========================================================================
    # Research-Specific Metrics
    # ==========================================================================

    def record_research_start(
        self,
        company_name: str,
        depth: str = "standard"
    ):
        """Record research start."""
        self.increment("research.started", labels={"depth": depth})
        self.gauge("research.active", self._counters.get("research.started", 0))

    def record_research_complete(
        self,
        company_name: str,
        duration_seconds: float,
        cost: float,
        depth: str = "standard"
    ):
        """Record research completion."""
        self.increment("research.completed", labels={"depth": depth})
        self.timing("research.duration", duration_seconds, {"depth": depth})
        self.histogram("research.cost", cost, {"depth": depth})

    def record_research_failed(
        self,
        company_name: str,
        error: str,
        depth: str = "standard"
    ):
        """Record research failure."""
        self.increment("research.failed", labels={"depth": depth})
        self.increment(f"research.errors.{error[:50]}")

    def record_agent_execution(
        self,
        agent_name: str,
        duration_seconds: float,
        tokens_used: int,
        cost: float
    ):
        """Record agent execution metrics."""
        self.timing(f"agent.{agent_name}.duration", duration_seconds)
        self.histogram(f"agent.{agent_name}.tokens", tokens_used)
        self.histogram(f"agent.{agent_name}.cost", cost)
        self.increment(f"agent.{agent_name}.calls")

    def record_api_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: float
    ):
        """Record API request metrics."""
        self.increment("api.requests", labels={"endpoint": endpoint, "method": method})
        self.increment(f"api.status.{status_code}")
        self.timing("api.latency", duration_ms / 1000, {"endpoint": endpoint})

    # ==========================================================================
    # Retrieval and Aggregation
    # ==========================================================================

    def get_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get current counter value."""
        key = self._make_key(name, labels)
        return self._counters.get(key, 0.0)

    def get_gauge(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get current gauge value."""
        key = self._make_key(name, labels)
        return self._gauges.get(key, 0.0)

    def get_summary(
        self,
        name: str,
        labels: Optional[Dict[str, str]] = None
    ) -> MetricSummary:
        """Get summary statistics for a metric."""
        key = self._make_key(name, labels)

        # Check histograms and timers
        values = self._histograms.get(key, []) or self._timers.get(key, [])

        summary = MetricSummary(name=name)

        if values:
            summary.count = len(values)
            summary.total = sum(values)
            summary.min_value = min(values)
            summary.max_value = max(values)
            summary.mean = statistics.mean(values)

            if len(values) > 1:
                summary.std_dev = statistics.stdev(values)

            sorted_values = sorted(values)
            summary.p50 = self._percentile(sorted_values, 50)
            summary.p95 = self._percentile(sorted_values, 95)
            summary.p99 = self._percentile(sorted_values, 99)

        return summary

    def _percentile(self, sorted_values: List[float], p: float) -> float:
        """Calculate percentile from sorted values."""
        if not sorted_values:
            return 0.0
        k = (len(sorted_values) - 1) * (p / 100)
        f = int(k)
        c = f + 1 if f + 1 < len(sorted_values) else f
        return sorted_values[f] + (k - f) * (sorted_values[c] - sorted_values[f])

    def get_all_metrics(
        self,
        since: Optional[datetime] = None
    ) -> List[Metric]:
        """Get all recorded metrics."""
        with self._lock:
            if since:
                return [m for m in self._metrics if m.timestamp >= since]
            return list(self._metrics)

    def get_metrics_by_name(self, name: str) -> List[Metric]:
        """Get metrics by name."""
        with self._lock:
            return [m for m in self._metrics if m.name == name]

    # ==========================================================================
    # Export and Callbacks
    # ==========================================================================

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []

        # Counters
        for key, value in self._counters.items():
            lines.append(f"{key.replace('.', '_')} {value}")

        # Gauges
        for key, value in self._gauges.items():
            lines.append(f"{key.replace('.', '_')} {value}")

        return "\n".join(lines)

    def export_json(self) -> Dict[str, Any]:
        """Export metrics as JSON."""
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {k: self.get_summary(k).to_dict() for k in self._histograms},
            "timers": {k: self.get_summary(k).to_dict() for k in self._timers}
        }

    def on_metric(self, callback: Callable[[Metric], None]):
        """Register callback for new metrics."""
        self._on_metric.append(callback)

    # ==========================================================================
    # Cleanup
    # ==========================================================================

    def cleanup(self, older_than: Optional[datetime] = None):
        """Remove old metrics."""
        with self._lock:
            cutoff = older_than or datetime.now() - self._retention
            self._metrics = [m for m in self._metrics if m.timestamp >= cutoff]

    def reset(self):
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._timers.clear()
            self._metrics.clear()


# ============================================================================
# Timer Context Manager
# ============================================================================

class _TimerContext:
    """Context manager for timing operations."""

    def __init__(
        self,
        collector: MetricsCollector,
        name: str,
        labels: Optional[Dict[str, str]]
    ):
        self._collector = collector
        self._name = name
        self._labels = labels
        self._start = None

    def __enter__(self):
        self._start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self._start
        self._collector.timing(self._name, duration, self._labels)


# ============================================================================
# Factory Function
# ============================================================================

def create_metrics_collector(retention_hours: int = 24) -> MetricsCollector:
    """Create a metrics collector instance."""
    return MetricsCollector(retention_hours=retention_hours)


# Global instance
_global_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector."""
    global _global_collector
    if _global_collector is None:
        _global_collector = MetricsCollector()
    return _global_collector
