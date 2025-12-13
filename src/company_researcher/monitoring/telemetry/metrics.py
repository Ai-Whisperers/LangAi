"""
Metrics Module.

MeterProvider, Meter, and metric instruments.
"""

from typing import Dict, List

from .models import MetricPoint
from ...utils import utc_now


class Instrument:
    """Base class for metric instruments."""

    def __init__(self, name: str, description: str, unit: str, meter: "Meter"):
        self.name = name
        self.description = description
        self.unit = unit
        self.meter = meter
        self._points: List[MetricPoint] = []

    def _record(self, value: float, attributes: Dict[str, str] = None) -> None:
        """Record a measurement."""
        self._points.append(MetricPoint(
            timestamp=utc_now(),
            value=value,
            attributes=attributes or {}
        ))


class Counter(Instrument):
    """Monotonically increasing counter."""

    def add(self, amount: float, attributes: Dict[str, str] = None) -> None:
        """Add to the counter."""
        if amount < 0:
            raise ValueError("Counter can only be incremented")
        self._record(amount, attributes)


class UpDownCounter(Instrument):
    """Counter that can increase or decrease."""

    def add(self, amount: float, attributes: Dict[str, str] = None) -> None:
        """Add (or subtract) from the counter."""
        self._record(amount, attributes)


class Histogram(Instrument):
    """Records distribution of values."""

    def __init__(self, name: str, description: str, unit: str, meter: "Meter"):
        super().__init__(name, description, unit, meter)
        self._boundaries = [0, 5, 10, 25, 50, 75, 100, 250, 500, 750, 1000, 2500, 5000, 7500, 10000]
        self._buckets: Dict[str, Dict[float, int]] = {}

    def record(self, value: float, attributes: Dict[str, str] = None) -> None:
        """Record a value in the histogram."""
        self._record(value, attributes)

        # Update bucket counts
        attr_key = str(sorted((attributes or {}).items()))
        if attr_key not in self._buckets:
            self._buckets[attr_key] = {b: 0 for b in self._boundaries + [float('inf')]}

        for boundary in self._boundaries:
            if value <= boundary:
                self._buckets[attr_key][boundary] += 1
                break
        else:
            self._buckets[attr_key][float('inf')] += 1


class Gauge(Instrument):
    """Records current value."""

    def set(self, value: float, attributes: Dict[str, str] = None) -> None:
        """Set the gauge value."""
        self._record(value, attributes)


class Meter:
    """
    OpenTelemetry-compatible meter for metrics.

    Usage:
        meter = MeterProvider().get_meter("research")
        counter = meter.create_counter("research_requests")
        counter.add(1, {"company": "Tesla"})
    """

    def __init__(self, name: str, provider: "MeterProvider"):
        self.name = name
        self.provider = provider
        self._instruments: Dict[str, Instrument] = {}

    def create_counter(self, name: str, description: str = "", unit: str = "") -> Counter:
        """Create a counter metric."""
        counter = Counter(name, description, unit, self)
        self._instruments[name] = counter
        return counter

    def create_up_down_counter(self, name: str, description: str = "", unit: str = "") -> UpDownCounter:
        """Create an up/down counter metric."""
        counter = UpDownCounter(name, description, unit, self)
        self._instruments[name] = counter
        return counter

    def create_histogram(self, name: str, description: str = "", unit: str = "") -> Histogram:
        """Create a histogram metric."""
        histogram = Histogram(name, description, unit, self)
        self._instruments[name] = histogram
        return histogram

    def create_gauge(self, name: str, description: str = "", unit: str = "") -> Gauge:
        """Create a gauge metric."""
        gauge = Gauge(name, description, unit, self)
        self._instruments[name] = gauge
        return gauge


class MeterProvider:
    """Provider for creating meters."""

    def __init__(self, resource: Dict[str, str] = None):
        self.resource = resource or {}
        self._meters: Dict[str, Meter] = {}

    def get_meter(self, name: str) -> Meter:
        """Get or create a meter."""
        if name not in self._meters:
            self._meters[name] = Meter(name, self)
        return self._meters[name]
