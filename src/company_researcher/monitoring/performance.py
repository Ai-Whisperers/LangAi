"""
Performance Monitor (Phase 19.3).

Monitor system performance:
- Latency tracking
- Throughput monitoring
- Resource utilization
- Bottleneck detection
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import time
import threading
import statistics


# ============================================================================
# Data Models
# ============================================================================

class PerformanceLevel(str, Enum):
    """Performance level indicators."""
    EXCELLENT = "excellent"  # < p50
    GOOD = "good"           # p50 - p75
    ACCEPTABLE = "acceptable"  # p75 - p90
    DEGRADED = "degraded"   # p90 - p99
    CRITICAL = "critical"   # > p99


@dataclass
class PerformanceMetric:
    """A performance measurement."""
    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": round(self.value, 4),
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class PerformanceSummary:
    """Summary of performance metrics."""
    name: str
    count: int = 0
    mean: float = 0.0
    min_value: float = float('inf')
    max_value: float = float('-inf')
    p50: float = 0.0
    p95: float = 0.0
    p99: float = 0.0
    level: PerformanceLevel = PerformanceLevel.GOOD
    trend: str = "stable"  # improving, stable, degrading

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "count": self.count,
            "mean": round(self.mean, 4),
            "min": round(self.min_value, 4) if self.min_value != float('inf') else 0,
            "max": round(self.max_value, 4) if self.max_value != float('-inf') else 0,
            "p50": round(self.p50, 4),
            "p95": round(self.p95, 4),
            "p99": round(self.p99, 4),
            "level": self.level.value,
            "trend": self.trend
        }


@dataclass
class ThroughputMetric:
    """Throughput measurement."""
    name: str
    requests_per_second: float
    requests_per_minute: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "rps": round(self.requests_per_second, 2),
            "rpm": round(self.requests_per_minute, 2),
            "timestamp": self.timestamp.isoformat()
        }


# ============================================================================
# Performance Monitor
# ============================================================================

class PerformanceMonitor:
    """
    Monitor system performance.

    Features:
    - Latency tracking
    - Throughput monitoring
    - Performance summaries
    - Trend analysis

    Usage:
        monitor = PerformanceMonitor()

        # Track operation latency
        with monitor.measure("research.financial"):
            do_financial_analysis()

        # Manual timing
        monitor.record_latency("api.request", 0.045)

        # Get summary
        summary = monitor.get_summary("research.financial")
    """

    def __init__(
        self,
        window_size: int = 1000,
        retention_hours: int = 24
    ):
        """
        Initialize performance monitor.

        Args:
            window_size: Number of samples to keep per metric
            retention_hours: Hours to retain data
        """
        self._window_size = window_size
        self._retention = timedelta(hours=retention_hours)

        # Storage
        self._latencies: Dict[str, List[PerformanceMetric]] = {}
        self._throughput_windows: Dict[str, List[float]] = {}

        # Thresholds (in seconds)
        self._thresholds: Dict[str, Dict[str, float]] = {}

        # Thread safety
        self._lock = threading.RLock()

    # ==========================================================================
    # Latency Tracking
    # ==========================================================================

    def record_latency(
        self,
        name: str,
        duration_seconds: float,
        context: Optional[Dict[str, Any]] = None
    ):
        """Record a latency measurement."""
        metric = PerformanceMetric(
            name=name,
            value=duration_seconds,
            unit="seconds",
            context=context or {}
        )

        with self._lock:
            if name not in self._latencies:
                self._latencies[name] = []

            self._latencies[name].append(metric)

            # Trim to window size
            if len(self._latencies[name]) > self._window_size:
                self._latencies[name] = self._latencies[name][-self._window_size:]

    def measure(self, name: str, context: Optional[Dict[str, Any]] = None):
        """
        Context manager for measuring operation latency.

        Usage:
            with monitor.measure("research.complete"):
                do_research()
        """
        return _MeasureContext(self, name, context)

    # ==========================================================================
    # Throughput Tracking
    # ==========================================================================

    def record_request(self, name: str = "api"):
        """Record a request for throughput calculation."""
        now = time.time()

        with self._lock:
            if name not in self._throughput_windows:
                self._throughput_windows[name] = []

            self._throughput_windows[name].append(now)

            # Keep only last minute
            cutoff = now - 60
            self._throughput_windows[name] = [
                t for t in self._throughput_windows[name] if t > cutoff
            ]

    def get_throughput(self, name: str = "api") -> ThroughputMetric:
        """Get current throughput."""
        now = time.time()

        with self._lock:
            timestamps = self._throughput_windows.get(name, [])

            # Last second
            last_second = [t for t in timestamps if t > now - 1]
            rps = len(last_second)

            # Last minute
            rpm = len(timestamps)

            return ThroughputMetric(
                name=name,
                requests_per_second=rps,
                requests_per_minute=rpm
            )

    # ==========================================================================
    # Summaries and Analysis
    # ==========================================================================

    def get_summary(self, name: str) -> PerformanceSummary:
        """Get performance summary for a metric."""
        with self._lock:
            metrics = self._latencies.get(name, [])

            summary = PerformanceSummary(name=name)

            if not metrics:
                return summary

            values = [m.value for m in metrics]
            summary.count = len(values)
            summary.mean = statistics.mean(values)
            summary.min_value = min(values)
            summary.max_value = max(values)

            sorted_values = sorted(values)
            summary.p50 = self._percentile(sorted_values, 50)
            summary.p95 = self._percentile(sorted_values, 95)
            summary.p99 = self._percentile(sorted_values, 99)

            # Determine performance level
            summary.level = self._determine_level(name, summary.p95)

            # Calculate trend
            summary.trend = self._calculate_trend(values)

            return summary

    def _percentile(self, sorted_values: List[float], p: float) -> float:
        """Calculate percentile."""
        if not sorted_values:
            return 0.0
        k = (len(sorted_values) - 1) * (p / 100)
        f = int(k)
        c = f + 1 if f + 1 < len(sorted_values) else f
        return sorted_values[f] + (k - f) * (sorted_values[c] - sorted_values[f])

    def _determine_level(self, name: str, p95: float) -> PerformanceLevel:
        """Determine performance level based on thresholds."""
        thresholds = self._thresholds.get(name, {
            "excellent": 0.1,
            "good": 0.5,
            "acceptable": 1.0,
            "degraded": 5.0
        })

        if p95 < thresholds.get("excellent", 0.1):
            return PerformanceLevel.EXCELLENT
        elif p95 < thresholds.get("good", 0.5):
            return PerformanceLevel.GOOD
        elif p95 < thresholds.get("acceptable", 1.0):
            return PerformanceLevel.ACCEPTABLE
        elif p95 < thresholds.get("degraded", 5.0):
            return PerformanceLevel.DEGRADED
        else:
            return PerformanceLevel.CRITICAL

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from recent values."""
        if len(values) < 10:
            return "stable"

        # Compare first half to second half
        mid = len(values) // 2
        first_half = statistics.mean(values[:mid])
        second_half = statistics.mean(values[mid:])

        if second_half < first_half * 0.9:
            return "improving"
        elif second_half > first_half * 1.1:
            return "degrading"
        else:
            return "stable"

    def set_thresholds(
        self,
        name: str,
        excellent: float,
        good: float,
        acceptable: float,
        degraded: float
    ):
        """Set performance thresholds for a metric."""
        self._thresholds[name] = {
            "excellent": excellent,
            "good": good,
            "acceptable": acceptable,
            "degraded": degraded
        }

    # ==========================================================================
    # Bottleneck Detection
    # ==========================================================================

    def detect_bottlenecks(self) -> List[Dict[str, Any]]:
        """Detect performance bottlenecks."""
        bottlenecks = []

        with self._lock:
            for name, metrics in self._latencies.items():
                if not metrics:
                    continue

                summary = self.get_summary(name)

                if summary.level in [PerformanceLevel.DEGRADED, PerformanceLevel.CRITICAL]:
                    bottlenecks.append({
                        "metric": name,
                        "level": summary.level.value,
                        "p95": summary.p95,
                        "trend": summary.trend,
                        "recommendation": self._get_recommendation(name, summary)
                    })

        return bottlenecks

    def _get_recommendation(
        self,
        name: str,
        summary: PerformanceSummary
    ) -> str:
        """Get recommendation for bottleneck."""
        if "llm" in name.lower() or "agent" in name.lower():
            return "Consider using a faster model or reducing token count"
        elif "search" in name.lower():
            return "Consider caching search results or reducing query count"
        elif "api" in name.lower():
            return "Consider adding caching or optimizing query patterns"
        else:
            return "Investigate slow operations and consider async processing"

    # ==========================================================================
    # Export
    # ==========================================================================

    def get_all_summaries(self) -> Dict[str, Dict[str, Any]]:
        """Get summaries for all metrics."""
        with self._lock:
            return {
                name: self.get_summary(name).to_dict()
                for name in self._latencies.keys()
            }

    def export_json(self) -> Dict[str, Any]:
        """Export performance data as JSON."""
        return {
            "summaries": self.get_all_summaries(),
            "throughput": {
                name: self.get_throughput(name).to_dict()
                for name in self._throughput_windows.keys()
            },
            "bottlenecks": self.detect_bottlenecks()
        }

    def cleanup(self, older_than: Optional[datetime] = None):
        """Remove old metrics."""
        cutoff = older_than or datetime.now() - self._retention

        with self._lock:
            for name in list(self._latencies.keys()):
                self._latencies[name] = [
                    m for m in self._latencies[name]
                    if m.timestamp >= cutoff
                ]


# ============================================================================
# Measure Context Manager
# ============================================================================

class _MeasureContext:
    """Context manager for measuring latency."""

    def __init__(
        self,
        monitor: PerformanceMonitor,
        name: str,
        context: Optional[Dict[str, Any]]
    ):
        self._monitor = monitor
        self._name = name
        self._context = context
        self._start = None

    def __enter__(self):
        self._start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self._start
        self._monitor.record_latency(self._name, duration, self._context)


# ============================================================================
# Factory Function
# ============================================================================

def create_performance_monitor(
    window_size: int = 1000,
    retention_hours: int = 24
) -> PerformanceMonitor:
    """Create a performance monitor instance."""
    return PerformanceMonitor(
        window_size=window_size,
        retention_hours=retention_hours
    )
